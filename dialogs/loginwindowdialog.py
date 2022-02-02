import sys
from PyQt5 import QtCore
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView

##

#Window of the Login feature containing the "LoginWindow" class
#
#@Antoine
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
##

#The _loadFinished methode calls a html page when the login process is finished
#
#@Antoine
    def _loadFinished(self, result):
        self.page().toHtml(self.callable)
##

#The callablemethode defines html as data
#
#@Antoine
    def callable(self, data):
        self.html = data
