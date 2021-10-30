import sys
from PyQt5 import QtCore
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView


class LoginWindow(QWebEngineView):
    logged_in = QtCore.pyqtSignal(['QString'])

    def __init__(self, app):
        super(LoginWindow, self).__init__()
        self.nam = self.page()
        self.app = app
        self.setUrl(QUrl(AuthUrl))
        self.show()
        self.loadFinished.connect(self._loadFinished)
        interceptor = RequestInterceptor(self.app)
        self.page().profile().setRequestInterceptor(interceptor)
        sys.exit(app.exec_())

    def _loadFinished(self, result):
        self.page().toHtml(self.callable)

    def callable(self, data):
        self.html = data
