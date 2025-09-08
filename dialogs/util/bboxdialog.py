from qgis.PyQt.QtWidgets import QDialog, QAction, QMessageBox
from qgis.PyQt.QtGui import QStandardItem,QStandardItemModel
from qgis.core import QgsRasterLayer, QgsProject, QgsCoordinateReferenceSystem, \
    QgsCoordinateTransform, QgsPointXY, QgsRectangle
from qgis.gui import QgsMapToolPan
from qgis.PyQt import uic
from qgis.core import Qgis, QgsGeometry,QgsVectorLayer,QgsFeature
from qgis.core import QgsMessageLog

from ...util.sparqlutils import SPARQLUtils
from ...util.ui.uiutils import UIUtils
from ...util.ui.mappingtools import RectangleMapTool,CircleMapTool,PolygonSelectMapTool
from ...util.geocodingutils import GeocodingUtils, SPARQLCompleter
import os.path
import json

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '../ui/bboxdialog.ui'))

MESSAGE_CATEGORY = 'BBOXDialog'

class BBOXDialog(QDialog, FORM_CLASS):

    def __init__(self, inp_sparql, triplestoreconf, title="Choose Geospatial Constraint",templayer=None, ext_map_canvas=None):
        super(QDialog, self).__init__()
        self.setupUi(self)
        self.ext_map_canvas=ext_map_canvas
        self.setWindowTitle(title)
        self.setWindowIcon(UIUtils.bboxicon)
        self.inp_sparql = inp_sparql
        self.rectangle = False
        self.circle = False
        self.polygon = True
        self.templayer=templayer
        #QgsMessageLog.logMessage("Templayer: " + str(templayer), MESSAGE_CATEGORY, Qgis.Info)
        self.tabWidget.removeTab(3)
        self.sparqlcompleter=SPARQLCompleter([])
        self.triplestoreconf = triplestoreconf
        self.vl = QgsVectorLayer("Point", "temporary_points", "memory")
        self.vl_geocoding = QgsVectorLayer("Polygon", "temporary_polygons", "memory")
        self.vl_layerextent = QgsVectorLayer("Polygon", "temporary_polys", "memory")
        self.layerExtentOrBBOX = False
        self.map_canvas.setMinimumSize(500, 475)
        actionPan = QAction("Pan", self)
        actionPan.setCheckable(True)
        actionPan.triggered.connect(self.pan)
        self.toolPan = QgsMapToolPan(self.map_canvas)
        self.toolPan.setAction(actionPan)
        self.toolPan3 = QgsMapToolPan(self.map_canvas_layerextent)
        self.toolPan2 = QgsMapToolPan(self.map_canvas_geocoding)
        self.toolPan2.setAction(actionPan)
        self.toolPan3.setAction(actionPan)
        uri = "url=http://a.tile.openstreetmap.org/{z}/{x}/{y}.png&zmin=0&type=xyz"
        self.mts_layer = QgsRasterLayer(uri, 'OSM', 'wms')
        if not self.mts_layer.isValid():
            print("Layer failed to load!")
        self.rect_tool = RectangleMapTool(self.map_canvas)
        self.circ_tool = CircleMapTool(self.map_canvas, 1)
        self.poly_tool = PolygonSelectMapTool(self.map_canvas)
        self.map_canvas.setMapTool(self.rect_tool)
        self.map_canvas.setExtent(self.mts_layer.extent())
        self.map_canvas_geocoding.setExtent(self.mts_layer.extent())
        self.map_canvas_layerextent.setExtent(self.mts_layer.extent())
        self.map_canvas_geocoding.setMapTool(self.toolPan2)
        self.map_canvas_geocoding.setDestinationCrs(QgsCoordinateReferenceSystem('EPSG:3857'))
        self.map_canvas_layerextent.setMapTool(self.toolPan3)
        self.map_canvas_layerextent.setDestinationCrs(QgsCoordinateReferenceSystem('EPSG:3857'))
        self.map_canvas.setDestinationCrs(QgsCoordinateReferenceSystem('EPSG:3857'))
        if self.templayer is not None:
            self.templayer.invertSelection()
            self.map_canvas.setLayers([self.vl, self.templayer, self.mts_layer])
            self.map_canvas.zoomToSelected(self.templayer)
            self.map_canvas.zoomOut()
            self.map_canvas.zoomOut()
            self.map_canvas_geocoding.setLayers([self.vl_geocoding,self.templayer, self.mts_layer])
            self.map_canvas_geocoding.zoomToSelected(self.templayer)
            self.map_canvas_geocoding.zoomOut()
            self.map_canvas_geocoding.zoomOut()
            self.map_canvas_layerextent.setLayers([self.vl_layerextent,self.templayer, self.mts_layer])
            if len(QgsProject.instance().layerTreeRoot().children()) > 0:
                self.map_canvas_layerextent.zoomToSelected(self.templayer)
                self.map_canvas_layerextent.zoomOut()
                self.map_canvas_layerextent.zoomOut()
            self.templayer.invertSelection()
        else:
            self.map_canvas.setLayers([self.vl, self.mts_layer])
            self.map_canvas_geocoding.setLayers([self.vl_geocoding, self.mts_layer])
            self.map_canvas_layerextent.setLayers([self.vl_layerextent, self.mts_layer])
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
        self.geocodeSearch.setCompleter(self.sparqlcompleter)
        self.geocodeSearchButton.clicked.connect(self.geocodeInput)
        self.geocodeSearch.textChanged.connect(self.insertCompletion)
        self.b1.clicked.connect(self.setBBOXInQuery)
        self.chooseBBOXLayer.currentIndexChanged.connect(self.showExtent)
        if len(self.chooseBBOXLayer)>0:
            self.showExtent()

    def showExtent(self):
        geom=self.chooseBBOXLayer.currentLayer().extent()
        crs = self.chooseBBOXLayer.currentLayer().crs()
        if geom is not None:
            self.vl_layerextent.startEditing()
            listOfIds = [feat.id() for feat in self.vl_layerextent.getFeatures()]
            self.vl_layerextent.deleteFeatures(listOfIds)
            feat = QgsFeature()
            #QgsMessageLog.logMessage("Geocoding: " + str(QgsGeometry.fromRect(geom).asWkt()), MESSAGE_CATEGORY, Qgis.Info)
            feat.setGeometry(QgsGeometry.fromRect(geom))
            self.vl_layerextent.addFeature(feat)
            self.vl_layerextent.commitChanges()
            self.vl_layerextent.setCrs(crs)
            self.vl_layerextent.updateExtents()
            self.vl_layerextent.invertSelection()
            self.map_canvas_layerextent.zoomToSelected(self.vl_layerextent)
            self.map_canvas_layerextent.zoomOut()
            self.map_canvas_layerextent.zoomOut()

    def insertCompletion(self, completion):
        if(completion==self.geocodeSearch.completer().currentCompletion()):
            geom=self.geocodeSearch.completer().completionModel().sourceModel().itemFromIndex(self.geocodeSearch.completer().completionModel().mapToSource(self.geocodeSearch.completer().currentIndex())).data(256)
            crs=self.geocodeSearch.completer().completionModel().sourceModel().itemFromIndex(self.geocodeSearch.completer().completionModel().mapToSource(self.geocodeSearch.completer().currentIndex())).data(257)
            self.vl_geocoding.startEditing()
            listOfIds = [feat.id() for feat in self.vl_geocoding.getFeatures()]
            self.vl_geocoding.deleteFeatures(listOfIds)
            self.vl_geocoding2=QgsVectorLayer(json.dumps(geom), "mygeojson", "ogr")
            #feat = QgsFeature()
            #feat.setGeometry(QgsGeometry.fromJson(geom))
            features=self.vl_geocoding2.getFeatures()
            for feat in features:
                self.vl_geocoding.addFeature(feat)
            self.vl_geocoding.commitChanges()
            #self.vl_geocoding.setCrs(crs)
            self.vl_geocoding.updateExtents()
            self.vl_geocoding.invertSelection()
            self.map_canvas_geocoding.zoomToSelected(self.vl_geocoding)
            self.map_canvas_geocoding.zoomOut()
            self.map_canvas_geocoding.zoomOut()


    def geocodeInput(self):
        searchString=self.geocodeSearch.text()
        geocoder=self.geocoderSelection.currentText()
        if geocoder=="Nominatim":
            QgsMessageLog.logMessage("Geocoding: " + str(searchString), MESSAGE_CATEGORY, Qgis.Info)
            gc=GeocodingUtils()
            results=gc.geocode(searchString)
            QgsMessageLog.logMessage("Nominatim Response: " + str(results), MESSAGE_CATEGORY, Qgis.Info)
            choosemodel=self.sparqlcompleter.model()
            choosemodel.clear()
            for rec in results:
                if "class" in rec and rec["class"]=="boundary":
                    QgsMessageLog.logMessage("Nominatim Response: " + str(rec["geojson"]), MESSAGE_CATEGORY, Qgis.Info)
                    curitem=QStandardItem(rec["display_name"])
                    curitem.setData(rec["geojson"],256)
                    #curitem.setData(rec.crs(), 257)
                    curitem.setData(rec["boundingbox"], 258)
                    QgsMessageLog.logMessage("Nominatim Response: " + str(curitem.data(256)), MESSAGE_CATEGORY,
                                             Qgis.Info)
                    choosemodel.appendRow(curitem)
            popupp=self.sparqlcompleter.popup()
            popupp.show()
            #popupp.x=self.geocodeSearch.x()
            #popupp.y=self.geocodeSearch.y()+self.geocodeSearch.height()

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
            self.mts_layer = self.chooseBBOXLayer.currentLayer()
            self.layerExtentOrBBOX = True
            self.setBBOXInQuery()
            self.close()
        else:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("No layer loaded in QGIS!")
            msgBox.setText("No layer has been loaded in QGIS to get an extent from!")
            msgBox.exec()

    def setBBOXInQuery(self,bbox):
        if self.ext_map_canvas is not None:
            layerlist = self.ext_map_canvas.layers()
            if self.tabWidget.currentIndex()==0:
                layerlist.insert(1, QgsVectorLayer(self.vl.source(), self.vl.name(), self.vl.providerType()))
            if self.tabWidget.currentIndex()==1:
                layerlist.insert(1, QgsVectorLayer(self.vl_geocoding.source(), self.vl_geocoding.name(), self.vl_geocoding.providerType()))
            if self.tabWidget.currentIndex()==2:
                layerlist.insert(1, QgsVectorLayer(self.vl_layerextent.source(), self.vl_layerextent.name(), self.vl_layerextent.providerType()))
            self.ext_map_canvas.setLayers(layerlist)
        sourceCrs = None
        polygon=None
        pointt1=None
        pointt2=None
        pointt3=None
        pointt4=None
        if self.layerExtentOrBBOX:
            xMax = self.mts_layer.extent().xMaximum()
            xMin = self.mts_layer.extent().xMinimum()
            yMin = self.mts_layer.extent().yMinimum()
            yMax = self.mts_layer.extent().yMaximum()
            pointt1 = QgsGeometry.fromPointXY(QgsPointXY(xMax, yMin))
            pointt2 = QgsGeometry.fromPointXY(QgsPointXY(xMin, yMin))
            pointt3 = QgsGeometry.fromPointXY(QgsPointXY(xMin, yMax))
            pointt4 = QgsGeometry.fromPointXY(QgsPointXY(xMax, yMax))
            polygon = QgsGeometry.fromPolylineXY(
                [pointt1.asPoint(), pointt2.asPoint(), pointt3.asPoint(), pointt4.asPoint()])
            self.polygon=True
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
                self.rectangle=True
                pointt1 = QgsGeometry.fromWkt(self.rect_tool.point1.asWkt())
                pointt2 = QgsGeometry.fromWkt(self.rect_tool.point2.asWkt())
                pointt3 = QgsGeometry.fromWkt(self.rect_tool.point3.asWkt())
                pointt4 = QgsGeometry.fromWkt(self.rect_tool.point4.asWkt())
                if sourceCrs is not None:
                    tr = QgsCoordinateTransform(sourceCrs, destCrs, QgsProject.instance())
                    pointt1.transform(tr)
                    pointt2.transform(tr)
                    pointt3.transform(tr)
                    pointt4.transform(tr)
                polygon = QgsGeometry.fromPolylineXY(
                    [pointt1.asPoint(), pointt2.asPoint(), pointt3.asPoint(), pointt4.asPoint()])
        if polygon is not None:
            center = polygon.centroid()
        # distance = QgsDistanceArea()
        # distance.setSourceCrs(destCrs)
        # distance.setEllipsoidalMode(True)
        # distance.setEllipsoid('WGS84')
        self.curquery=""
        if self.inp_sparql is not None:
            self.curquery = self.inp_sparql.toPlainText()
        if self.rectangle or self.circle:
            widthm = 100  # distance.measureLine(pointt1, pointt2)
            self.curbbox = []
            self.curbbox.append(pointt1)
            self.curbbox.append(pointt2)
            self.curbbox.append(pointt3)
            self.curbbox.append(pointt4)
            self.close()
            self.curquery=SPARQLUtils.constructBBOXQuerySegment(self.triplestoreconf,self.curbbox,widthm,self.curquery)
            #QgsMessageLog.logMessage(curquery, MESSAGE_CATEGORY, Qgis.Info)
        elif polygon:
            widthm = 100
            if "bboxquery" in self.triplestoreconf and \
                    self.triplestoreconf["bboxquery"]["type"] == "geosparql":
                self.curquery = self.curquery[0:self.curquery.rfind(
                    '}')] + f'FILTER(geof:sfIntersects(?geo,"{polygon.asWkt()}"^^geo:wktLiteral))'
            else:
                QgsMessageLog.logMessage(polygon,MESSAGE_CATEGORY,Qgis.Info)
                self.curquery = SPARQLUtils.constructBBOXQuerySegment(self.triplestoreconf, polygon.boundingBox(),
                                                             widthm, self.curquery)
        if self.inp_sparql is not None:
            self.inp_sparql.setPlainText(self.curquery)
        self.accept()
