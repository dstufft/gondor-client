import gzip
import json
import os
import sys
import time

# Remove These once dependency on them is gone
import urllib
import urllib2

from cement2.core.exc import CementRuntimeError

from gondor import __version__
from gondor.api import Gondor
from gondor.cli.core import controller
from gondor.cli.core import handler
from gondor.cli.core import hook


class Command(controller.CementBaseController):
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
            try:
                packager = handler.get("project_packager", self.config.get("gondor", "vcs"))(self.config)
            except CementRuntimeError:
                raise  # @@@ Print an error message
            
            # Package Project
            tar_path, commit, sha = packager.package_project(label, commit)
            
            if tar_path is None:
                pass  # @@@ Raise an Error
            
            # Run pre_compress_tarball hook
            for res in hook.run("pre_compress_tarball", tar_path):
                # We don't need to do anything with the return value
                # This hooks exists only to modify the existing tarfile
                # prior to compressing it.
                pass
            
            tarball_path = os.path.abspath(os.path.join(self.config.get("project", "repo_root"), "%s-%s.tar.gz" % (label, sha)))
            
            # Build the Tarball
            with open(tar_path, "rb") as tar_fp:
                try:
                    tarball = gzip.open(tarball_path, mode="wb")
                    tarball.writelines(tar_fp)
                finally:
                    tarball.close()
            
            # @@@ move this to self.setup() ?
            # @@@ Allow using key instead of password as well
            self.api = Gondor(self.config.get("auth", "username"), self.config.get("auth", "password"))
            
            # Deploy To Gondor
            with open(tarball_path, "rb") as tarball:
                params = {
                    "version": __version__,
                    "site_key": self.config.get("gondor", "site_key"),
                    "label": label,
                    "sha": sha,
                    "commit": commit,
                    "tarball": tarball,
                    "project_root":  os.path.relpath(self.config.get("project", "root"), self.config.get("project", "repo_root")),
                    "app": json.dumps(dict(self.config.items("app"))),
                }
                try:
                    response = self.api.deploy(params)
                except KeyboardInterrupt:
                    print "Canceling uploading... [ok]"
                    sys.exit(1)
                except urllib2.HTTPError:
                    raise  # @@@ Display an Error
                else:
                    data = json.loads(response.read())
        finally:
            if tar_path and os.path.exists(tar_path):
                os.unlink(tar_path)
            if tarball_path and os.path.exists(tarball_path):
                os.unlink(tarball_path)
        
        # Poll for Status
        if data["status"] == "error":
            print data["message"]
        elif data["status"] == "success":
            deployment_id = data["deployment"]
            
            if "url" in data:
                instance_url = data["url"]
            else:
                instance_url = None
            
            print "Deploying..."
            
            while True:
                params = {
                    "version": __version__,
                    "site_key": self.config.get("gondor", "site_key"),
                    "instance_label": label,
                    "task_id": deployment_id,
                }
                
                url = "%s/task_status/" % "https://api.gondor.io"
            
                try:
                    response = self.api._make_api_call(url, urllib.urlencode(params))
                except urllib2.URLError:
                    # @@@ add max retries
                    continue
                data = json.loads(response.read())
                
                if data["status"] == "error":
                    print "[error]"
                    print data["message"]
                elif data["status"] == "success":
                    if data["state"] == "finished":
                        print "ok"
                        if instance_url:
                            print "Visit: %s" % instance_url
                        break
                elif data["state"] == "failed":
                    print "[failed]"
                    print data["reason"]
                    sys.exit(1)
                elif data["state"] == "locked":
                    print "[locked]"
                    print "Your deployment failed due to being locked. This means there is another deployment already in progress."
                    sys.exit(1)
                else:
                    time.sleep(2)
