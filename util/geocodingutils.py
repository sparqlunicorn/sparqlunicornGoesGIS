
from qgis.PyQt.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from qgis.PyQt import QtCore
from qgis.PyQt.QtCore import QSortFilterProxyModel, Qt, QUrl
from qgis.PyQt.QtGui import QStandardItemModel
from qgis.PyQt.QtWidgets import QCompleter,QMessageBox
from qgis.core import QgsMessageLog, Qgis
from qgis.core import (
    QgsRectangle,
    QgsNominatimGeocoder,
    QgsGeocoderContext,
    QgsCoordinateTransformContext,
    QgsGeocoderInterface,
    QgsBlockingNetworkRequest,
    QgsNetworkAccessManager,
    QgsNetworkReplyContent
)

import json
import requests

MESSAGE_CATEGORY="GeocodingUtils"

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
        url = f"{self.endpointReverse}?lat={lat}&lon={lon}polygon_geojson=1&format=json"
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

    def geocode(self,text):
        nominatimurl = UIUtils.nominatimurl.format(**{'address': text})
        nominatimurl+="&polygon_geojson=1"
        QgsMessageLog.logMessage("Request URL: " + str(nominatimurl), MESSAGE_CATEGORY,
                                 Qgis.Info)
        response = requests.get(nominatimurl).json()
        QgsMessageLog.logMessage("Handling response: " + str(response), MESSAGE_CATEGORY,
                                 Qgis.Info)
        return response
        """
        request = QNetworkRequest(QUrl(nominatimurl))
        request.setHeader(QNetworkRequest.UserAgentHeader, 'PyQGIS@GIS-OPS.com')
        man=QgsNetworkAccessManager.instance()
        man.finished.connect(self.handleResponse)
        reply =man.get(request)
        status_code = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)
        QgsMessageLog.logMessage("Geocoding: " + str(nominatimurl), MESSAGE_CATEGORY,
                                 Qgis.Info)
        QgsMessageLog.logMessage("Sent nominatim query: " + str(nominatimurl)+"  "+str(reply), MESSAGE_CATEGORY,
                                 Qgis.Info)
        #self.networkrequest(nominatimurl)
        """

    def networkrequest(self, nurl):
        global reply
        self.manager = QgsNetworkAccessManager()
        url = QUrl(nurl)
        request = QNetworkRequest(url)
        res=self.manager.get(request)
        res.finished.connect(self.handleResponse)


    def handleResponse(self, reply):
        QgsMessageLog.logMessage("Handling respoonse: " + str(reply.content), MESSAGE_CATEGORY,
                                 Qgis.Info)
        er = reply.error()
        if er == QNetworkReply.NoError:
            QgsMessageLog.logMessage("No error!", MESSAGE_CATEGORY,Qgis.Info)
            QgsMessageLog.logMessage(str(reply), MESSAGE_CATEGORY, Qgis.Info)
            results = json.loads(str(reply, 'utf-8'))
            QgsMessageLog.logMessage("JSON: " + str(results), MESSAGE_CATEGORY,Qgis.Info)
            self.nominatimmap = {}
            chooselist = []
            for rec in results:
                chooselist.append(rec['display_name'])
                self.nominatimmap[rec['display_name']] = [rec['lon'], rec['lat']]
        else:
            QgsMessageLog.logMessage("Error occured: " + str(er), MESSAGE_CATEGORY,
                                     Qgis.Info)