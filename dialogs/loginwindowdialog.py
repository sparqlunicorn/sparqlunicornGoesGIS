import sys
from PyQt5 import QtCore
from PyQt5.QtCore import QUrl
from qgis.PyQt.QtWidgets import QDialog
from qgis.PyQt import uic
import os
from PyQt5.QtWebEngineWidgets import QWebEngineView



FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/oauthlogindialog.ui'))

# Class representing a search dialog which may be used to search for concepts or properties.


class LoginWindowDialog(QDialog, FORM_CLASS):
    logged_in = QtCore.pyqtSignal(['QString'])

    def __init__(self, app):
        super(QDialog, self).__init__()
        self.setupUi(self)
        #self.nam = self.page()
        #self.app = app
        #self.setUrl(QUrl(AuthUrl))
        #self.show()
        #self.loadFinished.connect(self._loadFinished)
        #interceptor = RequestInterceptor(self.app)
        #self.page().profile().setRequestInterceptor(interceptor)
        #sys.exit(app.exec_())

    def _loadFinished(self, result):
        self.page().toHtml(self.callable)

    def callable(self, data):
        self.html = data
