import sys
from urllib.parse import urlencode, parse_qs
from PyQt5 import QtCore
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication

class LoginWindow(QWebEngineView):
    logged_in = QtCore.pyqtSignal(['QString'])

<<<<<<< HEAD
    def __init__(self, app):
        super(LoginWindow, self).__init__()
        self.nam = self.page()
        self.app = app
        self.setUrl(QUrl(AuthUrl))
        self.show()
        self.loadFinished.connect(self._loadFinished)
        interceptor = RequestInterceptor(self.app)
=======
    def __init__(self, app, authurl,interceptor):
        super(LoginWindow, self).__init__()
        self.nam = self.page()
        self.app = app
        self.setUrl(QUrl(authurl))
        self.show()
        self.loadFinished.connect(self._loadFinished)
        self.interceptor = interceptor
>>>>>>> 62eabd13feb11502469f2bb0c5c2a2fb1328b89b
        self.page().profile().setRequestInterceptor(interceptor)
        sys.exit(app.exec_())

    def _loadFinished(self, result):
        self.page().toHtml(self.callable)

    def callable(self, data):
        self.html = data
<<<<<<< HEAD
=======
		

>>>>>>> 62eabd13feb11502469f2bb0c5c2a2fb1328b89b
