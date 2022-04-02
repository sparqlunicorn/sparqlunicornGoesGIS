from qgis.PyQt.QtWidgets import QDialog, QAction, QMessageBox, QCompleter, QLineEdit
from qgis.PyQt.QtGui import QStandardItem,QStandardItemModel
from qgis.PyQt.QtCore import QUrl
from qgis.PyQt import QtCore
from qgis.PyQt.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from qgis.core import QgsVectorLayer, QgsRasterLayer, QgsProject, QgsGeometry, QgsCoordinateReferenceSystem, \
    QgsCoordinateTransform, QgsPointXY, QgsPoint
from qgis.gui import QgsMapToolPan
from qgis.PyQt import uic
from qgis.PyQt.QtCore import QSortFilterProxyModel, Qt
from qgis.core import Qgis, QgsGeometry,QgsVectorLayer
from qgis.core import QgsMessageLog

from ..util.ui.uiutils import UIUtils
from ..util.ui.mappingtools import RectangleMapTool
from ..util.ui.mappingtools import CircleMapTool
from ..util.ui.mappingtools import PolygonMapTool
import os.path
import json

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/bboxdialog.ui'))

MESSAGE_CATEGORY = 'BBOXDialog'

class SPARQLCompleter(QCompleter):
    insertText = QtCore.pyqtSignal(str)

    def __init__(self, autocomplete, parent=None):
        QCompleter.__init__(self, autocomplete, parent)
        self.setCompletionMode(QCompleter.PopupCompletion)
        self.setFilterMode(Qt.MatchContains)
        self.source_model=None
        self.setModel(QStandardItemModel())
        # self.highlighted.connect(self.setHighlighted)

    def setModel(self, model):
        self.source_model = model
        super(SPARQLCompleter, self).setModel(self.source_model)

    def updateModel(self):
        local_completion_prefix = self.local_completion_prefix
        class InnerProxyModel(QSortFilterProxyModel):
            def filterAcceptsRow(self, sourceRow, sourceParent):
                index0 = self.sourceModel().index(sourceRow, 0, sourceParent)
                QgsMessageLog.logMessage("Chosen data: " + str(index0.data(256)), MESSAGE_CATEGORY, Qgis.Info)
                self.zoomToCoordinates(index0)
                return local_completion_prefix.lower() in self.sourceModel().data(index0).lower()
        proxy_model = InnerProxyModel()
        proxy_model.setSourceModel(self.source_model)
        super(SPARQLCompleter, self).setModel(proxy_model)

    def setHighlighted(self, text):
        self.lastSelected = text

    def getSelected(self):
        return self.lastSelected


class NominatimText(QLineEdit):

    def __init__(self, map_canvas):
        super(self.__class__, self).__init__()
        self.map_canvas = map_canvas

    def insertCompletion(self, completion):
        scale = 50
        rect = QgsRectangle(completion.data(256).x() - scale, completion.data(256).y() - scale, completion.data(256).x() + scale, completion.data(256).y() + scale)
        self.map_canvas.setExtent(rect)
        self.map_canvas.refresh()


class BBOXDialog(QDialog, FORM_CLASS):

    def __init__(self, inp_sparql, triplestoreconf, endpointIndex,title="Choose BoundingBox"):
        super(QDialog, self).__init__()
        self.setupUi(self)
        self.setWindowTitle(title)
        self.setWindowIcon(UIUtils.bboxicon)
        self.inp_sparql = inp_sparql
        self.sparqlcompleter=SPARQLCompleter([])
        self.triplestoreconf = triplestoreconf
        self.endpointIndex = endpointIndex
        self.vl = QgsVectorLayer("Point", "temporary_points", "memory")
        self.layerExtentOrBBOX = False
        self.map_canvas.setMinimumSize(500, 475)
        self.nominatimmap = {}
        actionPan = QAction("Pan", self)
        actionPan.setCheckable(True)
        actionPan.triggered.connect(self.pan)
        self.toolPan = QgsMapToolPan(self.map_canvas)
        self.toolPan.setAction(actionPan)
        uri = "url=http://a.tile.openstreetmap.org/{z}/{x}/{y}.png&zmin=0&type=xyz"
        self.mts_layer = QgsRasterLayer(uri, 'OSM', 'wms')
        if not self.mts_layer.isValid():
            print("Layer failed to load!")
        self.rect_tool = RectangleMapTool(self.map_canvas)
        self.circ_tool = CircleMapTool(self.map_canvas, 1)
        self.poly_tool = PolygonMapTool(self.map_canvas)
        self.map_canvas.setMapTool(self.rect_tool)
        self.map_canvas.setExtent(self.mts_layer.extent())
        self.map_canvas.setLayers([self.vl, self.mts_layer])
        self.map_canvas.setCurrentLayer(self.mts_layer)
        self.pan()
        self.selectCircle.hide()
        self.crsdialog.setCrs(QgsCoordinateReferenceSystem('EPSG:4326'))
        self.crsdialog.show()
        self.panButton.clicked.connect(self.pan)
        self.selectCircle.clicked.connect(self.selectcircle)
        self.selectPolygon.clicked.connect(self.selectpolygon)
        self.selectButton.clicked.connect(self.selectarea)
        self.zoomIn.clicked.connect(self.map_canvas.zoomIn)
        self.zoomOut.clicked.connect(self.map_canvas.zoomOut)
        self.b2.clicked.connect(self.setBBOXExtentQuery)
        #self.geocodeSearch=NominatimText(self.map_canvas)
        self.geocodeSearch.setCompleter(self.sparqlcompleter)
        self.geocodeSearch.textChanged.connect(self.geocode)
        layers = QgsProject.instance().layerTreeRoot().children()
        for layer in layers:
            self.chooseBBOXLayer.addItem(layer.name())
        self.searchButton.clicked.connect(self.geocode)
        self.b1.clicked.connect(self.setBBOXInQuery)

    def geocode(self):
        try:
            nominatimurl = UIUtils.nominatimurl.format(**{'address': self.geocodeSearch.text()})
            self.networkrequest(nominatimurl)
        except Exception as e:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("Mandatory variables missing!")
            msgBox.setText(str(e))
            msgBox.exec()

    def networkrequest(self, nurl):
        global reply
        self.manager = QNetworkAccessManager()
        url = QUrl(nurl)
        request = QNetworkRequest(url)
        self.manager.finished.connect(self.handleResponse)
        self.manager.get(request)

    def handleResponse(self, reply):
        er = reply.error()
        if er == QNetworkReply.NoError:
            bytes_string = reply.readAll()
            print(str(bytes_string, 'utf-8'))
            results = json.loads(str(bytes_string, 'utf-8'))
            choosemodel=self.sparqlcompleter.model()
            choosemodel.clear()
            for rec in results:
                curitem=QStandardItem(rec['display_name'])
                curitem.setData(QgsPoint(float(rec['lat']),float(rec['lon'])),256)
                choosemodel.appendRow(curitem)
            QgsMessageLog.logMessage("Nominatim Response: " + str(results), MESSAGE_CATEGORY, Qgis.Info)
            popupp=self.sparqlcompleter.popup()
            popupp.x=self.geocodeSearch.x()
            popupp.y=self.geocodeSearch.y()+self.geocodeSearch.height()
            popupp.show()
        else:
            print("Error occured: ", er)

    def zoomToCoordinates(self, completion):
        scale = 50
        rect = QgsRectangle(completion.data(256).x() - scale, completion.data(256).y() - scale, completion.data(256).x() + scale, completion.data(256).y() + scale)
        self.map_canvas.setExtent(rect)
        self.map_canvas.refresh()
        #self.map_canvas.zoomWithCenter(, completion.data(256).y(), True)

    def pan(self):
        self.map_canvas.setMapTool(self.toolPan)

    def selectarea(self):
        self.rectangle = True
        self.circle = False
        self.polygon = False
        self.map_canvas.setMapTool(self.rect_tool)

    def selectcircle(self):
        self.rectangle = False
        self.circle = True
        self.polygon = False
        self.map_canvas.setMapTool(self.circ_tool)

    def selectpolygon(self):
        self.rectangle = False
        self.circle = False
        self.polygon = True
        self.map_canvas.setMapTool(self.poly_tool)

    def setBBOXExtentQuery(self):
        if len(QgsProject.instance().layerTreeRoot().children()) > 0:
            self.mts_layer = QgsProject.instance().layerTreeRoot().children()[
                self.chooseBBOXLayer.currentIndex()].layer()
            self.layerExtentOrBBOX = True
            self.setBBOXInQuery()
            self.close()
        else:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("No layer loaded in QGIS!")
            msgBox.setText("No layer has been loaded in QGIS to get an extent from!")
            msgBox.exec()

    def setBBOXInQuery(self):
        sourceCrs = None
        if self.layerExtentOrBBOX:
            xMax = self.mts_layer.extent().xMaximum()
            xMin = self.mts_layer.extent().xMinimum()
            yMin = self.mts_layer.extent().yMinimum()
            yMax = self.mts_layer.extent().yMaximum()
            pointt1 = QgsGeometry.fromPointXY(QgsPointXY(xMax, yMin))
            pointt2 = QgsGeometry.fromPointXY(QgsPointXY(xMin, yMin))
            pointt3 = QgsGeometry.fromPointXY(QgsPointXY(xMin, yMax))
            pointt4 = QgsGeometry.fromPointXY(QgsPointXY(xMax, yMax))
            sourceCrs = QgsCoordinateReferenceSystem(self.mts_layer.crs())
        else:
            sourceCrs = QgsCoordinateReferenceSystem(self.mts_layer.crs())
            destCrs = self.crsdialog.crs()
            if self.polygon:
                polygon = self.poly_tool.rb.asGeometry()
                tr = QgsCoordinateTransform(sourceCrs, destCrs, QgsProject.instance())
                polygon.transform(tr)
            elif self.circle:
                pointt1 = QgsGeometry.fromWkt(self.circ_tool.point1.asWkt())
                pointt2 = QgsGeometry.fromWkt(self.circ_tool.point2.asWkt())
                pointt3 = QgsGeometry.fromWkt(self.circ_tool.point3.asWkt())
                pointt4 = QgsGeometry.fromWkt(self.circ_tool.point4.asWkt())
            else:
                pointt1 = QgsGeometry.fromWkt(self.rect_tool.point1.asWkt())
                pointt2 = QgsGeometry.fromWkt(self.rect_tool.point2.asWkt())
                pointt3 = QgsGeometry.fromWkt(self.rect_tool.point3.asWkt())
                pointt4 = QgsGeometry.fromWkt(self.rect_tool.point4.asWkt())
                if sourceCrs != None:
                    tr = QgsCoordinateTransform(sourceCrs, destCrs, QgsProject.instance())
                    pointt1.transform(tr)
                    pointt2.transform(tr)
                    pointt3.transform(tr)
                    pointt4.transform(tr)
                polygon = QgsGeometry.fromPolylineXY(
                    [pointt1.asPoint(), pointt2.asPoint(), pointt3.asPoint(), pointt4.asPoint()])
        center = polygon.centroid()
        # distance = QgsDistanceArea()
        # distance.setSourceCrs(destCrs)
        # distance.setEllipsoidalMode(True)
        # distance.setEllipsoid('WGS84')
        curquery = self.inp_sparql.toPlainText()
        if self.rectangle or self.circle:
            widthm = 100  # distance.measureLine(pointt1, pointt2)
            self.curbbox = []
            self.curbbox.append(pointt1)
            self.curbbox.append(pointt2)
            self.curbbox.append(pointt3)
            self.curbbox.append(pointt4)
            self.close()
            if "bboxquery" in self.triplestoreconf[self.endpointIndex] and \
                    self.triplestoreconf[self.endpointIndex]["bboxquery"]["type"] == "geosparql":
                curquery = curquery[0:curquery.rfind('}')] + self.triplestoreconf[self.endpointIndex]["bboxquery"][
                    "query"].replace("%%x1%%", str(pointt1.asPoint().x())).replace("%%x2%%",
                                                                                   str(pointt3.asPoint().x())).replace(
                    "%%y1%%", str(pointt1.asPoint().y())).replace("%%y2%%",
                                                                  str(pointt3.asPoint().y())) + "}\n" + curquery[
                                                                                                        curquery.rfind(
                                                                                                            '}') + 1:]
            elif "bboxquery" in self.triplestoreconf[self.endpointIndex] and \
                    self.triplestoreconf[self.endpointIndex]["bboxquery"]["type"] == "minmax":
                curquery = curquery[0:curquery.rfind('}')] + self.triplestoreconf[self.endpointIndex]["bboxquery"][
                    "query"].replace("%%minPoint%%", pointt2.asWkt()).replace("%%maxPoint%%",
                                                                              pointt4.asWkt()) + curquery[
                                                                                                 curquery.rfind(
                                                                                                     '}') + 1:]
            elif "bboxquery" in self.triplestoreconf[self.endpointIndex] and \
                    self.triplestoreconf[self.endpointIndex]["bboxquery"]["type"] == "pointdistance":
                curquery = curquery[0:curquery.rfind('}')] + self.triplestoreconf[self.endpointIndex]["bboxquery"][
                    "query"].replace("%%lat%%", str(center.asPoint().y())).replace("%%lon%%",
                                                                                   str(center.asPoint().x())).replace(
                    "%%distance%%", str(widthm / 1000)) + curquery[curquery.rfind('}') + 1:]
        elif polygon:
            widthm = 100
            if "bboxquery" in self.triplestoreconf[self.endpointIndex] and \
                    self.triplestoreconf[self.endpointIndex]["bboxquery"]["type"] == "geosparql":
                curquery = curquery[0:curquery.rfind(
                    '}')] + "FILTER(geof:sfIntersects(?geo,\"" + polygon.asWkt() + "\"^^geo:wktLiteral))"
            elif "bboxquery" in self.triplestoreconf[self.endpointIndex] and \
                    self.triplestoreconf[self.endpointIndex]["bboxquery"]["type"] == "minmax":
                curquery = curquery[0:curquery.rfind('}')] + self.triplestoreconf[self.endpointIndex]["bboxquery"][
                    "query"].replace("%%minPoint%%", "POINT(" + str(polygon.boundingBox().yMinimum()) + " " + str(
                    polygon.boundingBox().xMinimum()) + ")").replace("%%maxPoint%%", "POINT(" + str(
                    polygon.boundingBox().yMaximum()) + " " + str(polygon.boundingBox().xMaximum()) + ")") + curquery[
                                                                                                             curquery.rfind(
                                                                                                                 '}') + 1:]
            elif "bboxquery" in self.triplestoreconf[self.endpointIndex] and \
                    self.triplestoreconf[self.endpointIndex]["bboxquery"]["type"] == "pointdistance":
                curquery = curquery[0:curquery.rfind('}')] + self.triplestoreconf[self.endpointIndex]["bboxquery"][
                    "query"].replace("%%lat%%", str(polygon.boundingBox().center().asPoint().y())).replace("%%lon%%",
                                                                                                           str(polygon.boundingBox().center().asPoint().x())).replace(
                    "%%distance%%", str(widthm / 1000)) + curquery[curquery.rfind('}') + 1:]
        self.inp_sparql.setPlainText(curquery)
        self.close()
