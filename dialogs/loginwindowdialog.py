import sys
from PyQt5 import QtCore
from PyQt5.QtWebKitWidgets import QWebView
from PyQt5.QtCore import QUrl
from ..util.oauth import OAuthConfiguration
from qgis.PyQt.QtWidgets import QDialog
from qgis.PyQt import uic
import os

#from ..util.oauth import RequestInterceptor

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/oauthlogindialog.ui'))

# Class representing a search dialog which may be used to search for concepts or properties.

class LoginWindowDialog(QDialog, FORM_CLASS):
    logged_in = QtCore.pyqtSignal(['QString'])

    def __init__(self, app):
        super(QDialog, self).__init__()
        self.setupUi(self)
        self.googleOAuthButton.clicked.connect(self.createGoogleDialog)
        self.gitlabcomOAuthButton.clicked.connect(lambda: LoginWindow(self, "gitlabcom"))
        self.orcidOAuthButton.clicked.connect(lambda: LoginWindow(self, "orcid"))
        self.githubOAuthButton.clicked.connect(lambda: LoginWindow(self, "github"))

    def _loadFinished(self, result):
        self.page().toHtml(self.callable)

    def callable(self, data):
        self.html = data
        
    def createGoogleDialog(self):
        self.myWV = QWebView(None)
        self.myWV.load(QUrl(OAuthConfiguration.getAuthUrl("google")))#QUrl("http://www.google.de"))#OAuthConfiguration.AuthUrl["google"]))
        self.myWV.show()
        #LoginWindow(self, "google")


class LoginWindow(QWebView):
    logged_in = QtCore.pyqtSignal(['QString'])

    def __init__(self, app,provider):
        super(LoginWindow, self).__init__()
        self.nam = self.page()
        self.app = app
        self.setUrl(QUrl(OAuthConfiguration.AuthUrl[provider]))
        self.show()
        self.loadFinished.connect(self._loadFinished)
        #interceptor = RequestInterceptor(self.app,provider)
        #self.page().profile().setRequestInterceptor(interceptor)
        sys.exit(app.exec_())

    def _loadFinished(self, result):
        self.page().toHtml(self.callable)

    def callable(self, data):
        self.html = data

