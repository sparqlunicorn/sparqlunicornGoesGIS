
from qgis.PyQt.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from qgis.PyQt import QtCore
from qgis.core import Qgis
from qgis.PyQt.QtCore import QSortFilterProxyModel, Qt, QUrl
from qgis.PyQt.QtGui import QStandardItem,QStandardItemModel
from qgis.PyQt.QtWidgets import QCompleter,QMessageBox,QLineEdit
from qgis.core import QgsMessageLog
from qgis.core import (
    QgsRectangle,
    QgsNominatimGeocoder,
    QgsGeocoderContext,
    QgsCoordinateTransformContext,
    QgsGeocoderInterface,
    QgsBlockingNetworkRequest
)

import json

from .ui.uiutils import UIUtils


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
                self.zoomToCoordinates(index0)
                return local_completion_prefix.lower() in self.sourceModel().data(index0).lower()
        proxy_model = InnerProxyModel()
        proxy_model.setSourceModel(self.source_model)
        super(SPARQLCompleter, self).setModel(proxy_model)

    def setHighlighted(self, text):
        self.lastSelected = text

    def getSelected(self):
        return self.lastSelected


class QgsNominatimRevGeocoder(QgsNominatimGeocoder):

    def __init__(self, endpointReverse="https://nominatim.openstreetmap.org/reverse"):
        super().__init__()
        self.endpointReverse = endpointReverse

    def flags(self):
        return QgsGeocoderInterface.Flag.GeocodesStrings & QgsGeocoderInterface.Flag.GeocodesFeatures

    def geocodeFeature(self, feature, context, feedback=None):
        pt = feature.geometry().asPoint()
        lon, lat = pt.x(), pt.y()
        url = f"{self.endpointReverse}?lat={lat}&lon={lon}&format=json"
        request = QgsBlockingNetworkRequest()
        request.get(QNetworkRequest(QUrl(url)))
        reply = request.reply()
        content = reply.content()
        jsonContent = json.loads(content.data().decode())
        return self.jsonToResult(jsonContent)

class GeocodingUtils:

    def batchGeocoding(self):
        print("Batch geocoding stub")

    @staticmethod
    def geocodeWithAPI(address):
        n = QgsNominatimGeocoder()
        context = QgsGeocoderContext(QgsCoordinateTransformContext())
        out = n.geocodeString(address, context)
        return out

    @staticmethod
    def reversegeocodeWithAPI(feature):
        n = QgsNominatimRevGeocoder()
        context = QgsGeocoderContext(QgsCoordinateTransformContext())
        out = n.geocodeFeature(feature, context)
        return out

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
            self.nominatimmap = {}
            chooselist = []
            for rec in results:
                chooselist.append(rec['display_name'])
                self.nominatimmap[rec['display_name']] = [rec['lon'], rec['lat']]
        else:
            print("Error occured: ", er)