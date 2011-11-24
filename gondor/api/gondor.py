from __future__ import absolute_import

import copy

from gondor import __version__
from gondor.api import requests

DEFAULT_API = "https://api.gondor.io"
DEFAULT_ENDPOINTS = dict(
    deploy="%(api)s/deploy/",
    task_status="%(api)s/task/status/"
)
DEFAULT_ENDPOINTS = {
    "deploy": "%(api)s/deploy/",
    "instance.create": "%(api)s/instance/create/",
    "task.status": "%(api)s/task/status/",
}


class Instance(object):
    
    def __init__(self, session, api_url, endpoints, default_params):
        self.requests = session
        self.api_url = api_url
        self.endpoints = endpoints
        self.default_params = default_params
    
    def create(self, label, kind, project_root):
        url = self.endpoints["instance.create"] % dict(api=self.api_url)
        
        data = copy.deepcopy(self.default_params)
        data.update({
            "label": label,
            "kind": kind,
            "project_root": project_root,
        })
        
        response = self.requests.post(url, data=data)
        response.raise_for_status()
        
        return response


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
        
        self.auth = (self.username, self.password)
        self.default_params = {
            "version": __version__,
            "site_key": self.site_key,
        }
        
        self.requests = requests.session(auth=self.auth)
        
        # Add Sub API
        self.instance = Instance(self.requests, self.api_url, self.endpoints, self.default_params)
    
    def get_url(self, endpoint):
        endpoint_url = self.endpoints.get(endpoint)
        if endpoint_url is not None:
            return endpoint_url % dict(api=self.api_url)
    
    def deploy(self, params, tarball):
        url = self.get_url("deploy")
        
        data = copy.deepcopy(self.default_params)
        data.update(params)
        
        response = self.requests.post(url, data=data, files={"tarball": tarball})
        response.raise_for_status()
        
        return response
    
    def task_status(self, label, task_id):
        url = self.get_url("task_status")
        
        params = copy.deepcopy(self.default_params)
        params.update({
            "label": label,
            "task_id": task_id,
        })
        
        response = self.requests.get(url, params=params)
        response.raise_for_status()
        
        return response
