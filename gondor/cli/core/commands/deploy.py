import gzip
import json
import os
import sys
import time

# Remove These once dependency on them is gone
import urllib2

from cement2.core import controller
from cement2.core import handler
from cement2.core import hook

from gondor.cli.core.interfaces import BaseCommand


class Deploy(BaseCommand):
    class meta:
        interface = controller.IController
        label = "deploy"
        description = "deploy your applicaton to Gondor"
        
        defaults = dict()
        
        arguments = [
            (["label"], dict(action="store", help="an instance label")),
            (["commit"], dict(action="store", help="commit to deploy")),
            ]
    
    @property
    def usage_text(self):
        return "%s %s [--help] <label> <commit>" % (self.app.args.prog, self.meta.label)
    
    @controller.expose(hide=True)
    def default(self):
        label = self.pargs.label
        commit = self.pargs.commit
        
        tar_path = None
        tarball_path = None
        
        try:
            # Shouldn't be able to get an error here. We already check this.
            packager = handler.get("project_packager", self.config.get("gondor", "vcs"))(self.config)
            
            # Package Project
            tar_path, commit, sha = packager.package_project(label, commit)
            
            if tar_path is None:
                self.render({
                    "level": "error",
                    "message": "Their was an Error with the path given by the Project Packager for %s" % self.config.get("gondor", "vcs")
                })
                sys.exit(1)
            
            # Run pre_compress_tarball hook
            for res in hook.run("pre_compress_tarball", tar_path):
                # We don't need to do anything with the return value
                # This hooks exists only to modify the existing tarfile
                # prior to compressing it.
                pass
            
            tarball_path = os.path.abspath(os.path.join(self.config.get("project", "repo_root"), "%s-%s.tar.gz" % (label, sha)))
            
            # Build the Tarball
            self.render(dict(message="Building tarball".ljust(35, "."), raw=True))
            with open(tar_path, "rb") as tar_fp:
                try:
                    tarball = gzip.open(tarball_path, mode="wb")
                    tarball.writelines(tar_fp)
                finally:
                    tarball.close()
            self.render(dict(message="[ok]"))
            
            # Deploy To Gondor
            self.render(dict(message="Pushing tarball to Gondor".ljust(35, "."), raw=True))
            with open(tarball_path, "rb") as tarball:
                params = dict(
                    label=label,
                    sha=sha,
                    commit=commit,
                    tarball=tarball,
                    project_root=os.path.relpath(self.config.get("project", "root"), self.config.get("project", "repo_root")),
                    app=json.dumps(dict(self.config.items("app"))),
                )
                
                try:
                    response = self.api.deploy(params)
                except KeyboardInterrupt:
                    self.render(dict(message="[canceled]"))
                    sys.exit(1)
                except urllib2.HTTPError:
                    raise  # @@@ Display an Error
                else:
                    self.render(dict(message="[ok]"))
                    data = json.loads(response.read())
        finally:
            if tar_path and os.path.exists(tar_path):
                os.unlink(tar_path)
            if tarball_path and os.path.exists(tarball_path):
                os.unlink(tarball_path)
        
        # Poll for Status
        if data["status"] == "error":
            self.render(dict(message=data["message"], level="error"))
        elif data["status"] == "success":
            task_id = data["deployment"]
            instance_url = data.get("url")
            
            self.render(dict(message="Deploying".ljust(35, "."), raw=True))
            
            processing = True
            
            while processing:
                try:
                    response = self.api.task_status(label, task_id)
                except urllib2.URLError:  # @@@ Raise some sort of Gondor Api Error
                    # @@@ add max retries
                    continue
                
                data = json.loads(response.read())
                
                if data["status"] == "success":
                    if data["state"] == "finished":
                        processing = False
                        self.render(dict(message="[ok]"))
                        
                        if instance_url:
                            self.render(dict(message="\nVisit: %s" % instance_url))
                elif data["state"] == "failed":
                    self.render(dict(message="[failed]"))
                    self.render(dict(message=data["reason"], level="error"))
                    sys.exit(1)
                elif data["state"] == "locked":
                    self.render(dict(message="[locked]"))
                    self.render(dict(message="Your deployment failed due to being locked. This means there is another deployment already in progress."))
                    sys.exit(1)
                elif data["status"] == "error":
                    self.render(dict(message="[error]"))
                    self.render(dict(message=data["message"], level="error"))
                else:
                    time.sleep(2)
