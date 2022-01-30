
from qgis.PyQt.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtWidgets import QMessageBox

import json

from .ui.uiutils import UIUtils


class GeocodingUtils:

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