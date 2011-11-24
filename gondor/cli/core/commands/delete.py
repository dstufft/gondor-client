import json
import sys

from cement2.core import controller
from cement2.core import handler

from gondor.api import requests
from gondor.cli.core.interfaces import BaseCommand


class Delete(BaseCommand):
    class meta:
        interface = controller.IController
        label = "delete"
        description = "deletes an instance from your Gondor site"
        
        defaults = dict()
        
        arguments = [
            (["label"], dict(action="store", help="an instance label")),
        ]
    
    @property
    def usage_text(self):
        return "%s %s [--help] <label>" % (self.app.args.prog, self.meta.label)
    
    @controller.expose(hide=True)
    def default(self):
        label = self.pargs.label
        
        text = "ARE YOU SURE YOU WANT TO DELETE THIS INSTANCE? [y/N] "
        self.render(dict(message=text, raw=True))
        user_input = raw_input()  # @@@ Should this be changed so it's not tied to CLI?
        
        if user_input.lower() != "y":
            self.render(dict(message="Exiting without deleting the instance."))
            sys.exit(0)
        
        self.render(dict(message="Deleting instance on Gondor".ljust(35, "."), raw=True))
        
        try:
            response = self.api.instance.delete(label=label)
        except requests.exceptions.HTTPError:
            pass  # @@@ Raise Some sort of Error Here
        
        data = json.loads(response.content)
        
        if data["status"] == "success":
            self.render(dict(message="[ok]"))
        elif data["status"] == "error":
            self.render(dict(message="[error]"))
            self.render(dict(level="error", message=data["message"]))
        else:
            self.render(dict(message="[unknown]"))
