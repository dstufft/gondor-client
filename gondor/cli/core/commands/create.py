import json
import os

from cement2.core import controller
from cement2.core import handler

from gondor.api import requests
from gondor.cli.core.interfaces import BaseCommand

KIND_CHOICES = ["dev", "staging", "production"]


class Create(BaseCommand):
    class meta:
        interface = controller.IController
        label = "create"
        description = "deploy your applicaton to Gondor"
        
        defaults = dict()
        
        arguments = [
            (["--kind"], dict(action="store", help="type of instance to create", default=KIND_CHOICES[0], choices=KIND_CHOICES)),
            (["label"], dict(action="store", help="an instance label")),
            ]
    
    @property
    def usage_text(self):
        return "%s %s [--help] [--kind KIND] <label>" % (self.app.args.prog, self.meta.label)
    
    @controller.expose(hide=True)
    def default(self):
        label = self.pargs.label
        kind = self.pargs.kind
        
        # Shouldn't be able to get an error here. We already check this.
        packager = handler.get("project_packager", self.config.get("gondor", "vcs"))(self.config)
        
        self.render(dict(message="Creating instance on Gondor".ljust(35, "."), raw=True))
        
        try:
            response = self.api.instance.create(
                label=label, kind=kind,
                project_root=os.path.relpath(self.config.get("project", "root"), self.config.get("project", "repo_root")),
            )
        except requests.exceptions.HTTPError:
            pass  # @@@ Raise Some sort of Error Here
        
        data = json.loads(response.content)
        
        if data["status"] == "success":
            ctx = {"label": label, "vcs_current": packager.current_working}
            
            self.render(dict(message="[ok]"))
            self.render(dict(message="\nRun: gondor deploy %(label)s %(vcs_current)s" % ctx))
            self.render(dict(message="Visit: %s" % data["url"]))
        elif data["status"] == "error":
            self.render(dict(message="[error]"))
            self.render(dict(level="error", message=data["message"]))
        else:
            self.render(dict(message="[unknown]"))
            self.render(dict(level="error", message=data["message"]))
