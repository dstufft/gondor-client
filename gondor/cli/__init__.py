import os
import sys

from cement2.core import backend, foundation, handler
from cement2.core.exc import CementRuntimeError

from gondor import utils

from gondor.cli.core.commands import register as register_commands
from gondor.cli.core.handlers import register as register_handlers
from gondor.cli.core.interfaces import register as register_interfaces


def main():
    # @@@ Handle Error Here
    gondor_config_dir = os.path.join(utils.find_nearest(os.getcwd(), ".gondor"), ".gondor")
    
    # set default configuration options
    defaults = backend.defaults("gondor")
    
    defaults["base"]["debug"] = False
    defaults["base"]["output_handler"] = "stream"
    
    defaults["base"]["plugin_handler"] = "gondor_plugins"
    defaults["base"]["plugin_bootstrap_module"] = "gondor.cli.ext"
    
    defaults["base"]["config_files"] = [
        os.path.expanduser("~/.gondor"),
        os.path.join(gondor_config_dir, "config")
    ]
    
    defaults["project"] = {
        "config_dir": gondor_config_dir,
        "root": utils.find_nearest(os.getcwd(), ".gondor"),
    }
    
    # create an application
    app = foundation.lay_cement("gondor", defaults=defaults)
    
    # register interfaces
    register_interfaces()
    
    # register handlers
    register_handlers()
    
    # register core commands
    register_commands()
    
    # setup the application
    app.setup()
    
    # Add Local Environment Settings to the Config
    try:
        packager = handler.get("project_packager", app.config.get("gondor", "vcs"))(app.config)
    except CementRuntimeError:
        app.render({
            "level": "error",
            "message": "Could not find a handler for the vcs: %s" % app.config.get("gondor", "vcs"),
        })
        sys.exit(1)
    
    app.config.merge({
        "project": {
            "repo_root": packager.get_repo_root(os.getcwd()),
        }
    })
    
    app.render(dict(message=""))
    
    app.run()
