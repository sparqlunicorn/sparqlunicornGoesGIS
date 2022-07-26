from urllib.parse import urlencode


class OAuthConfiguration:
    ClientId = {"orcid":"","google":"","gitlabcom":"","github":""}
    ClientSecret = {"orcid":"","google":"","gitlabcom":"","github":""}
    Scopes ={ "orcid":['user_read', 'channel_subscriptions', 'channel_check_subscription', 'user_subscriptions', 'channel_editor',
            'chat_login'],"google":[],"gitlabcom":[],"github":[]}
    RedirectUrl = 'localhost/callback'
    RedirectScheme = 'http://'

    ResponseType = 'code'

    AuthUrl={"orcid":" https://orcid.org/oauth/authorize?{headers}","google":"","gitlabcom":"https://gitlab.example.com/oauth/authorize?{headers}","github":"https://github.com/login/oauth/authorize?{headers}"}

    @staticmethod
    def getAuthUrl(provider):
        if provider in OAuthConfiguration.AuthUrl:
            return OAuthConfiguration.AuthUrl[provider]\
                .format(headers=urlencode(
                {"client_id":OAuthConfiguration.ClientId[provider],
                 "redirect_uri": OAuthConfiguration.RedirectScheme+OAuthConfiguration.RedirectUrl,
                 "response_type": OAuthConfiguration.ResponseType,
                 'scope': str.join(' ', OAuthConfiguration.Scopes[provider])
                 }))
        return None
"""
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
"""
