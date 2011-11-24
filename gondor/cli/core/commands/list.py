import json

from cement2.core import controller

from gondor.api import requests
from gondor.cli.core.interfaces import BaseCommand


class List(BaseCommand):
    class meta:
        interface = controller.IController
        label = "list"
        description = "lists all instances from your Gondor site"
        
        defaults = dict()
        
        arguments = []
    
    @property
    def usage_text(self):
        return "%s %s [--help]" % (self.app.args.prog, self.meta.label)
    
    @controller.expose(hide=True)
    def default(self):
        try:
            response = self.api.instance.list()
        except requests.exceptions.HTTPError:
            raise  # @@@ Raise Some sort of Error Here
        
        data = json.loads(response.content)
        
        if data["status"] == "success":
            instances = sorted(data["instances"], key=lambda v: v["label"])
            if instances:
                for instance in instances:
                    self.render(dict(
                        message="%(label)s [%(kind)s] %(url)s %(last_deployment)s" % {
                            "label": instance["label"],
                            "kind": instance["kind"],
                            "url": instance["url"],
                            "last_deployment": instance["last_deployment"]["sha"][:8]
                        }
                    ))
            else:
                self.render(dict(message="No Instances Found"))
        elif data["status"] == "error":
            self.render(dict(level="error", message=data["message"]))
