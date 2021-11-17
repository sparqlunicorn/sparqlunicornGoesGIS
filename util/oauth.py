import sys
from urllib.parse import urlencode, parse_qs
import requests
from PyQt5 import QtCore
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication

ClientId = {"orcid":"","google":"","gitlabcom":"","github":""}
ClientSecret = {"orcid":"","google":"","gitlabcom":"","github":""}
RedirectUrl = 'localhost/callback'
RedirectScheme = 'http://'
Scopes = ['user_read', 'channel_subscriptions', 'channel_check_subscription', 'user_subscriptions', 'channel_editor',
          'chat_login']

ResponseType = 'code'

Headers = {'client_id': ClientId, 'redirect_uri': RedirectScheme+RedirectUrl, 'response_type': ResponseType,
           'scope': str.join(' ', Scopes)}

#AuthUrl = 'https://api.twitch.tv/kraken/oauth2/authorize?{headers}'.format(headers=urlencode(Headers))

AuthUrl={"orcid":" https://orcid.org/oauth/authorize?{headers}","google":"","gitlabcom":"https://gitlab.example.com/oauth/authorize?{headers}","github":"https://github.com/login/oauth/authorize?{headers}"}

class RequestInterceptor(QWebEngineUrlRequestInterceptor):

    oauthcode=None

    def __init__(self, app,provider):
        super(RequestInterceptor, self).__init__()
        self.app = app
        self.provider=provider

    def interceptRequest(self, info):
        if RedirectUrl == (info.requestUrl().host()+info.requestUrl().path()):
            params = parse_qs(info.requestUrl().query())
            if 'code' in params.keys():
                print('OAuth code is {code}'.format(code=params['code']))
                self.oauthcode=params['code']

"""
class GoogleRequestInterceptor(RequestInterceptor):
	
	def __init__(self, app):
        super(RequestInterceptor, self).__init__()
        self.app = app
		
    def interceptRequest(self, info):
        if RedirectUrl == (info.requestUrl().host()+info.requestUrl().path()):
            params = parse_qs(info.requestUrl().query())
            if 'code' in params.keys():
                print('OAuth code is {code}'.format(code=params['code']))
                self.oauthcode=params['code']
				
    def getUserInformation(self):
        r=requests.get("https://oauth2.googleapis.com/tokeninfo?id_token="+self.authcode)
		res = r.json()
        user=UserMetaData()
 
class ORCIDRequestInterceptor(RequestInterceptor):
	
	def __init__(self, app):
        super(RequestInterceptor, self).__init__()
        self.app = app
		
    def interceptRequest(self, info):
        if RedirectUrl == (info.requestUrl().host()+info.requestUrl().path()):
            params = parse_qs(info.requestUrl().query())
            if 'code' in params.keys():
                print('OAuth code is {code}'.format(code=params['code']))
                self.oauthcode=params['code']
				
    def getUserInformation(self):

class GithubRequestInterceptor(RequestInterceptor):
	
	def __init__(self, app):
        super(RequestInterceptor, self).__init__()
        self.app = app
		
    def interceptRequest(self, info):
        if RedirectUrl == (info.requestUrl().host()+info.requestUrl().path()):
            params = parse_qs(info.requestUrl().query())
            if 'code' in params.keys():
                print('OAuth code is {code}'.format(code=params['code']))
                self.oauthcode=params['code']
				
    def getUserInformation(self):

"""
class UserMetaData:

    username=None
	 
    firstname=None

    lastname=None
	
    userid=None
	
    name=None
	
    authenticatedby=None
	
    userurl=None
	
    

class GitlabRequestInterceptor(RequestInterceptor):
	
	def __init__(self, app):
        super(RequestInterceptor, self).__init__()
        self.app = app
    def interceptRequest(self, info):
        if RedirectUrl == (info.requestUrl().host()+info.requestUrl().path()):
            params = parse_qs(info.requestUrl().query())
            if 'code' in params.keys():
                print('OAuth code is {code}'.format(code=params['code']))
                self.oauthcode=params['code']
				
    def getUserInformation(self,baseurl):
        r = requests.get(baseurl+"/users?username="+)
		res = r.json()
        user=UserMetaData()
        user.username=res["username"]
        user.name=res["name"]
        user.userurl=res["web_url"]
        user.userid=res["id"]
        user.authenticatedby="Gitlab ("+baseurl+")"

