import base64
import urllib2

from gondor import http


class Gondor(object):
    
    def __init__(self, username, password=None, key=None):
        if password is None and key is None:
            pass  # Raise an Error about not having password or key
        self.username = username
        self.password = key or password
    
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
    
    def deploy(self, params, url=None):
        if url is None:
            # @@@ Pull These values from the config
            url = "%s/deploy/" % "https://api.gondor.io"
        
        handlers = [
            http.MultipartPostHandler,
        ]
        
        return self._make_api_call(url, params, extra_handlers=handlers)
