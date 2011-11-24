import json
import sys
import time

from cement2.core import controller

from gondor.api import requests
from gondor.cli.core.interfaces import BaseCommand


class SQLDump(BaseCommand):
    class meta:
        interface = controller.IController
        label = "sqldump"
        description = "outputs a database dump from a Gondor site instance"
        
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
        
        try:
            response = self.api.instance.sqldump(label=label)
        except requests.exceptions.HTTPError:
            raise  # @@@ Raise Some sort of Error Here
        
        data = json.loads(response.content)
        
        if data["status"] == "error":
            self.render(dict(level="error", message=data["message"]))
        elif data["status"] == "success":
            task_id = data["task"]
            
            while True:
                try:
                    response = self.api.task.status(label=label, task_id=task_id)
                except requests.exceptions.HTTPError:
                    continue  # @@@ Add some sort of Max Retries
                
                data = json.loads(response.content)
                
                if data["status"] == "error":
                    self.render(dict(
                        level="error",
                        message=data["message"],
                    ))
                    sys.exit(1)
                if data["status"] == "success":
                    if data["state"] == "finished":
                        break
                    elif data["state"] == "failed":
                        self.render(dict(
                            level="error",
                            message=data["message"],
                        ))
                        sys.exit(1)
                    elif data["state"] == "locked":
                        self.render(dict(
                            level="error",
                            message=(
                                "Your database dump failed due to be being locked. "
                                "This means there is another database dump already "
                                "in progress."
                            ),
                        ))
                        sys.exit(1)
                    else:
                        time.sleep(2)
            
            response = self.api.instance.fetchdump(data["result"]["public_url"])
            self.render(dict(message=response.content))
