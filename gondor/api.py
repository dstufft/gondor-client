import base64
import urllib
import urllib2

from gondor import __version__
from gondor import http


class Gondor(object):
    
    def __init__(self, username, password=None, key=None, site_key=None):
        if password is None and key is None:
            pass  # Raise an Error about not having password or key
        
        if site_key is None:
            pass  # Raise an Error about not having a site_key
        
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
    
    def deploy(self, params,):
        # @@@ Pull These values from the config
        url = "%s/deploy/" % "https://api.gondor.io"
        
        params.update(dict(version=__version__, site_key=self.site_key))
        
        handlers = [http.MultipartPostHandler]
        
        return self._make_api_call(url, params, extra_handlers=handlers)
    
    def task_status(self, label, task_id):
        # @@@ Pull these values from the config
        url = "%s/task/status/" % "https://api.gondor.io"
        
        params = dict(label=label, task_id=task_id)
        params.update(dict(version=__version__, site_key=self.site_key))
        
        return self._make_api_call(url, urllib.urlencode(params))
