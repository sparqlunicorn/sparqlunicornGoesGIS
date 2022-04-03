from qgis.gui import QgsMapToolEmitPoint, QgsMapCanvas, QgsRubberBand, QgsMapTool, QgsMapToolPan
from qgis.PyQt.QtCore import pyqtSignal, QUrl, Qt
from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtGui import QColor, QKeySequence
from qgis.core import QgsProject, Qgis, QgsRasterLayer, QgsPointXY, QgsRectangle, QgsDistanceArea, QgsWkbTypes
from math import sqrt, pi, cos, sin


class MapUtils:

    @staticmethod
    def initMapToolOSM(mapwidget,templayer=None):
        uri = "url=http://a.tile.openstreetmap.org/{z}/{x}/{y}.png&zmin=0&type=xyz"
        mts_layer = QgsRasterLayer(uri, 'OSM', 'wms')
        if not mts_layer.isValid():
            print("Layer failed to load!")
        mapwidget.setExtent(mts_layer.extent())
        if templayer!=None:
            mapwidget.setLayers([templayer, mts_layer])
        else:
            mapwidget.setLayers([mts_layer])
        mapwidget.setCurrentLayer(mts_layer)

class CircleMapTool(QgsMapTool):
    '''Outil de sélection par cercle, tiré de selectPlusFr'''

    selectionDone = pyqtSignal()
    move = pyqtSignal()

    def __init__(self, iface, segments):
        canvas = iface
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas
        self.iface = iface
        self.status = 0
        self.segments = segments
        self.rb = QgsRubberBand(self.canvas, QgsWkbTypes.PolygonGeometry)
        self.rb.setColor(QColor(255, 0, 0, 100))

    def canvasPressEvent(self, e):
        if not e.button() == Qt.LeftButton:
            return
        self.status = 1
        self.center = self.toMapCoordinates(e.pos())
        self.rbcircle(self.rb, self.center, self.center, self.segments)
        return

    def canvasMoveEvent(self, e):
        if not self.status == 1:
            return
        # construct a circle with N segments
        cp = self.toMapCoordinates(e.pos())
        self.rbcircle(self.rb, self.center, cp, self.segments)
        self.rb.show()
        self.move.emit()

    def canvasReleaseEvent(self, e):
        '''La sélection est faîte'''
        if not e.button() == Qt.LeftButton:
            return None
        self.status = 0
        if self.rb.numberOfVertices() > 3:
            self.selectionDone.emit()
        else:
            radius = 2
            # , ok = QInputDialog.getDouble(self.iface.mainWindow(), tr('Radius'),tr('Give a radius in m:'), min=0)
            if radius > 0:
                cp = self.toMapCoordinates(e.pos())
                cp.setX(cp.x() + radius)
                self.rbcircle(self.rb, self.toMapCoordinates(
                    e.pos()), cp, self.segments)
                self.rb.show()
                self.selectionDone.emit()
        return None

    def reset(self):
        self.status = 0
        self.rb.reset(True)

    def deactivate(self):
        self.rb.reset(True)
        QgsMapTool.deactivate(self)

    def rbcircle(self, rb, center, edgePoint, N):
        r = sqrt(center.sqrDist(edgePoint))
        self.rb.reset(QgsWkbTypes.PolygonGeometry)
        for itheta in range(N + 1):
            theta = itheta * (2.0 * pi / N)
            rb.addPoint(QgsPointXY(center.x() + r * cos(theta),
                                   center.y() + r * sin(theta)))
        return


class PolygonMapTool(QgsMapTool):

    selectionDone = pyqtSignal()
    move = pyqtSignal()

    def __init__(self, iface):
        canvas = iface
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas
        self.iface = iface
        self.status = 0
        self.rb = QgsRubberBand(self.canvas, QgsWkbTypes.PolygonGeometry)
        self.rb.setColor(QColor(255, 0, 0, 100))

    def keyPressEvent(self, e):
        if e.matches(QKeySequence.Undo):
            if self.rb.numberOfVertices() > 1:
                self.rb.removeLastPoint()

    def canvasPressEvent(self, e):
        if e.button() == Qt.LeftButton:
            if self.status == 0:
                self.rb.reset(QgsWkbTypes.PolygonGeometry)
                self.status = 1
            self.rb.addPoint(self.toMapCoordinates(e.pos()))
        else:
            if self.rb.numberOfVertices() > 2:
                self.status = 0
                self.selectionDone.emit()
            else:
                self.reset()
        return None

    def canvasMoveEvent(self, e):
        if self.rb.numberOfVertices() > 0 and self.status == 1:
            self.rb.removeLastPoint(0)
            self.rb.addPoint(self.toMapCoordinates(e.pos()))
        self.move.emit()
        return None

    def reset(self):
        self.status = 0
        self.rb.reset(True)

    def deactivate(self):
        self.rb.reset(True)
        QgsMapTool.deactivate(self)


class RectangleMapTool(QgsMapToolEmitPoint):
    rectangleCreated = pyqtSignal()
    deactivated = pyqtSignal()

    point1 = ""
    point2 = ""
    point3 = ""
    point4 = ""
    chosen = False

    def __init__(self, canvas):
        self.canvas = canvas
        QgsMapToolEmitPoint.__init__(self, self.canvas)

        self.rubberBand = QgsRubberBand(self.canvas, QgsWkbTypes.PolygonGeometry)
        self.rubberBand.setColor(QColor(255, 0, 0, 100))
        self.rubberBand.setWidth(2)

        self.reset()

    def reset(self):
        self.startPoint = self.endPoint = None
        self.isEmittingPoint = False
        self.rubberBand.reset(QgsWkbTypes.PolygonGeometry)

    def canvasPressEvent(self, e):
        self.startPoint = self.toMapCoordinates(e.pos())
        self.endPoint = self.startPoint
        self.isEmittingPoint = True

        self.showRect(self.startPoint, self.endPoint)

    def canvasReleaseEvent(self, e):
        self.isEmittingPoint = False
        if self.rectangle() is not None:
            self.rectangleCreated.emit()

    def canvasMoveEvent(self, e):
        if not self.isEmittingPoint:
            return
        self.endPoint = self.toMapCoordinates(e.pos())
        self.showRect(self.startPoint, self.endPoint)

    def showRect(self, startPoint, endPoint):
        self.rubberBand.reset(QgsWkbTypes.PolygonGeometry)
        if startPoint.x() == endPoint.x() or startPoint.y() == endPoint.y():
            return

        self.point1 = QgsPointXY(startPoint.x(), startPoint.y())
        self.point2 = QgsPointXY(startPoint.x(), endPoint.y())
        self.point3 = QgsPointXY(endPoint.x(), endPoint.y())
        self.point4 = QgsPointXY(endPoint.x(), startPoint.y())

        self.rubberBand.addPoint(self.point1, False)
        self.rubberBand.addPoint(self.point2, False)
        self.rubberBand.addPoint(self.point3, False)
        # True to update canvas
        self.rubberBand.addPoint(self.point4, True)
        self.rubberBand.show()
        chosen = True

    def rectangle(self):
        if self.startPoint is None or self.endPoint is None:
            return None
        elif self.startPoint.x() == self.endPoint.x() or \
                self.startPoint.y() == self.endPoint.y():
            return None

        return QgsRectangle(self.startPoint, self.endPoint)

    def setRectangle(self, rect):
        if rect == self.rectangle():
            return False

        if rect is None:
            self.reset()
        else:
            self.startPoint = QgsPointXY(rect.xMaximum(), rect.yMaximum())
            self.endPoint = QgsPointXY(rect.xMinimum(), rect.yMinimum())
            self.showRect(self.startPoint, self.endPoint)
        return True

    def deactivate(self):
        QgsMapTool.deactivate(self)
        self.deactivated.emit()
