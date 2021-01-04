
from qgis.PyQt.QtWidgets import QDialog,QLabel,QComboBox,QPushButton,QAction
from qgis.core import QgsVectorLayer,QgsRasterLayer,QgsProject,QgsGeometry,QgsFeature, QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsWkbTypes,QgsMapLayer,QgsPointXY
from qgis.gui import QgsMapCanvas,QgsMapToolPan
from qgis.PyQt import uic
from .rectanglemaptool import RectangleMapTool
import os.path

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'bboxdialog.ui'))

class BBOXDialog(QDialog,FORM_CLASS):
	
    def __init__(self,inp_sparql,triplestoreconf,endpointIndex):
        super(QDialog, self).__init__()
        self.setupUi(self)
        self.inp_sparql=inp_sparql
        self.triplestoreconf=triplestoreconf
        self.endpointIndex=endpointIndex
        self.vl = QgsVectorLayer("Point", "temporary_points", "memory")
        self.map_canvas = QgsMapCanvas(self)
        self.layerExtentOrBBOX=False
        self.map_canvas.setMinimumSize(500, 475)
        actionPan = QAction("Pan", self)
        actionPan.setCheckable(True)
        actionPan.triggered.connect(self.pan)
        self.toolPan = QgsMapToolPan(self.map_canvas)
        self.toolPan.setAction(actionPan)
        uri="url=http://a.tile.openstreetmap.org/{z}/{x}/{y}.png&zmin=0&type=xyz"
        self.mts_layer=QgsRasterLayer(uri,'OSM','wms')
        if not self.mts_layer.isValid():
            print ("Layer failed to load!")
        self.rect_tool = RectangleMapTool(self.map_canvas)
        self.map_canvas.setMapTool(self.rect_tool)
        self.map_canvas.setExtent(self.mts_layer.extent())
        self.map_canvas.setLayers( [self.vl,self.mts_layer] )
        self.map_canvas.setCurrentLayer(self.mts_layer)
        self.pan()
        #chooseLayerLabel=QLabel("Choose Layer Extent:",self)
        #chooseLayerLabel.move(0,480)	
        #self.chooseBBOXLayer=QComboBox(self)	
        #self.chooseBBOXLayer.move(150,475)	
        #b2 = QPushButton("Apply Layer Extent",self)	
        #b2.move(10,500)	
        self.panButton.clicked.connect(self.pan)
        self.selectButton.clicked.connect(self.selectarea)
        self.zoomIn.clicked.connect(self.map_canvas.zoomIn)
        self.zoomOut.clicked.connect(self.map_canvas.zoomOut)
        self.b2.clicked.connect(self.setBBOXExtentQuery)	
        layers = QgsProject.instance().layerTreeRoot().children()	
        for layer in layers:	
            self.chooseBBOXLayer.addItem(layer.name())  	
        #b1 = QPushButton("Apply BBOX",self)
        #b1.move(400,500)
        self.b1.clicked.connect(self.setBBOXInQuery)
	
    def pan(self):
        self.map_canvas.setMapTool(self.toolPan)

    def selectarea(self):
        self.map_canvas.setMapTool(self.rect_tool)
        
    def setBBOXExtentQuery(self):	
        self.mts_layer=QgsProject.instance().layerTreeRoot().children()[self.chooseBBOXLayer.currentIndex()].layer()	
        self.layerExtentOrBBOX=True	
        self.setBBOXInQuery()
	
    def setBBOXInQuery(self):
        sourceCrs=None
        if self.layerExtentOrBBOX:
            xMax=self.mts_layer.extent().xMaximum()
            xMin=self.mts_layer.extent().xMinimum()
            yMin=self.mts_layer.extent().yMinimum()
            yMax=self.mts_layer.extent().yMaximum()
            pointt1=QgsGeometry.fromPointXY(QgsPointXY(xMax,yMin))	
            pointt2=QgsGeometry.fromPointXY(QgsPointXY(xMin,yMin))	
            pointt3=QgsGeometry.fromPointXY(QgsPointXY(xMin,yMax))	
            pointt4=QgsGeometry.fromPointXY(QgsPointXY(xMax,yMax))
            sourceCrs = QgsCoordinateReferenceSystem(self.mts_layer.crs())	
        else:	
            pointt1=QgsGeometry.fromWkt(self.rect_tool.point1.asWkt())	
            pointt2=QgsGeometry.fromWkt(self.rect_tool.point2.asWkt())	
            pointt3=QgsGeometry.fromWkt(self.rect_tool.point3.asWkt())	
            pointt4=QgsGeometry.fromWkt(self.rect_tool.point4.asWkt())	
            sourceCrs = QgsCoordinateReferenceSystem(self.mts_layer.crs())
        if sourceCrs!=None:
            destCrs = QgsCoordinateReferenceSystem(4326)
            tr = QgsCoordinateTransform(sourceCrs, destCrs, QgsProject.instance())
            pointt1.transform(tr)
            pointt2.transform(tr)
            pointt3.transform(tr)
            pointt4.transform(tr)
        polygon = QgsGeometry.fromPolylineXY( [pointt1.asPoint(),pointt2.asPoint(),pointt3.asPoint(),pointt4.asPoint()] )
        center=polygon.centroid()
        #distance = QgsDistanceArea()
        #distance.setSourceCrs(destCrs)
        #distance.setEllipsoidalMode(True)
        #distance.setEllipsoid('WGS84')
        widthm = 100 #distance.measureLine(pointt1, pointt2)
        self.curbbox=[]
        self.curbbox.append(pointt1)
        self.curbbox.append(pointt2)
        self.curbbox.append(pointt3)
        self.curbbox.append(pointt4)
        self.close()
        curquery=self.inp_sparql.toPlainText()
        if "bboxquery" in self.triplestoreconf[self.endpointIndex] and self.triplestoreconf[self.endpointIndex]["bboxquery"]["type"]=="minmax":
             curquery=curquery[0:curquery.rfind('}')]+self.triplestoreconf[self.endpointIndex]["bboxquery"]["query"].replace("%%minPoint%%",pointt2.asWkt()).replace("%%maxPoint%%",pointt4.asWkt())+curquery[curquery.rfind('}')+1:]
        elif "bboxquery" in self.triplestoreconf[self.endpointIndex] and self.triplestoreconf[self.endpointIndex]["bboxquery"]["type"]=="pointdistance":
            curquery=curquery[0:curquery.rfind('}')]+self.triplestoreconf[self.endpointIndex]["bboxquery"]["query"].replace("%%lat%%",str(center.asPoint().y())).replace("%%lon%%",str(center.asPoint().x())).replace("%%distance%%",str(widthm/1000))+curquery[curquery.rfind('}')+1:]
        self.inp_sparql.setPlainText(curquery)
