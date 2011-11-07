import base64
import urllib
import urllib2

from gondor import __version__
from gondor import http

DEFAULT_API = "https://api.gondor.io"
DEFAULT_ENDPOINTS = dict(
    deploy="%(api)s/deploy/",
    task_status="%(api)s/task/status/"
)


class Gondor(object):
    
    def __init__(self, username, password=None, key=None, site_key=None, api_url=None, endpoints=None):
        if password is None and key is None:
            pass  # Raise an Error about not having password or key
        
        if site_key is None:
            pass  # Raise an Error about not having a site_key
        
        self.api_url = api_url if api_url is not None else DEFAULT_API
        self.endpoints = endpoints if endpoints is not None else DEFAULT_ENDPOINTS
        
        self.username = username
        self.password = key or password
        self.site_key = site_key
    
    def _make_api_call(self, url, params, extra_handlers=None):
        handlers = [
            http.HTTPSHandler,
        ]
        
        if extra_handlers is not None:
            handlers.extend(extra_handlers)
        
        opener = urllib2.build_opener(*handlers)
        request = urllib2.Request(url, params)
        
        request.add_unredirected_header(
            "Authorization",
            "Basic %s" % base64.b64encode("%s:%s" % (self.username, self.password)).strip()
        )
        
        return opener.open(request)
    
    def get_url(self, endpoint):
        endpoint_url = self.endpoints.get(endpoint)
        if endpoint_url is not None:
            return endpoint_url % dict(api=self.api_url)
    
    def deploy(self, params):
        url = self.get_url("deploy")
        
        params.update(dict(version=__version__, site_key=self.site_key))
        
        handlers = [http.MultipartPostHandler]
        
        return self._make_api_call(url, params, extra_handlers=handlers)
    
    def task_status(self, label, task_id):
        url = self.get_url("task_status")
        
        params = dict(label=label, task_id=task_id)
        params.update(dict(version=__version__, site_key=self.site_key))
        
        return self._make_api_call(url, urllib.urlencode(params))
