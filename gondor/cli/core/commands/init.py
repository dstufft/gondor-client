import os
import sys

from cement2.core import controller
from cement2.core import handler

from gondor.cli.core.interfaces import BaseCommand


class Init(BaseCommand):
    class meta:
        interface = controller.IController
        label = "init"
        description = "initalizes a gondor project"
        
        defaults = {}
        
        arguments = [
            (["site_key"], dict(action="store", help="They key to a site", nargs="?")),
        ]
    
    @controller.expose(hide=True)
    def default(self):
        if self.pargs is None:
            # Prompt for Site Key
            pass
        
        # Ensure Directory is a Django Directory
        files = [
            os.path.join(os.getcwd(), "__init__.py"),
            os.path.join(os.getcwd(), "manage.py")
        ]
        
        if not all([os.path.exists(f) for f in files]):
            self.render(dict(message="Must run Gondor from a Django project directory.", level="error"))
            sys.exit(1)
        
        gondor_dir = os.path.abspath(os.path.join(os.getcwd(), ".gondor"))
        
        repo_root = None
        looked_for = []
        vcs_type = None
        
        for packager in handler.list("project_packager"):
            p = packager(self.config)
            looked_for.append(p.meta.label)
            repo_root = p.get_repo_root(os.getcwd())
            if repo_root is not None:
                vcs_type = p.meta.label
                break
        
        if repo_root is None:
            self.render(dict(message="Unable to find a supported version control system. Looked for: %s" % ", ".join(looked_for), level="error"))
            sys.exit(1)
        
        if os.path.exists(gondor_dir):
            self.render(dict(message="Detected existing .gondor directory. Not overriding."))
            sys.exit(1)
        else:
            if repo_root == os.getcwd():
                self.render(dict(
                    message="WARNING: we've detected your repo root (directory containing .%s) is the same "
                            "directory as your project root. This is certainly allowed, but many of our "
                            "users have problems with this setup because the parent directory is *not* the "
                            "same on Gondor as it is locally. See https://gondor.io/support/project-layout/ "
                            "for more information on the suggested layout.",
                    level="error",
                ))
            
            config_template = ""  # @@@ Where should this come from?
            
            self.render(dict(message="Writing configuration (.gondor/config)".ljust(35, "."), raw=True))
            os.mkdir(gondor_dir)
            # @@@ Write Default Config File
            self.render(dict(message="[ok]"))
            
            self.render(dict(
                message="You are now ready to deploy your project to Gondor. You might want to first "
                        "check .gondor/config (in this directory) for correct values for your application "
                        "Once you are ready, run:\n"
                        "    gondor deploy primary %s" % handler.get("project_packager", vcs_type)(self.config)
            ))
