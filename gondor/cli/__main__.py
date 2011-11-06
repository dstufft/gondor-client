import os

from cement2.core import backend, foundation, handler, hook
from cement2.core.exc import CementRuntimeError

from gondor import controllers
from gondor import interfaces
from gondor import handlers
from gondor import utils


from gondor.cli.output import StreamOutputHandler
from gondor.cli.plugin import GondorPluginHandler

# Gondor Config Directory
# @@@ Handle Error Here
GONDOR_CONFIG_DIRECTORY = os.path.join(utils.find_nearest(os.getcwd(), ".gondor"), ".gondor")

# set default config options
defaults = backend.defaults("gondor")

defaults["base"]["debug"] = False
defaults["base"]["config_files"] = [os.path.expanduser("~/.gondor"), os.path.join(GONDOR_CONFIG_DIRECTORY, "config")]

defaults["base"]["output_handler"] = "stream"

defaults["base"]["plugin_handler"] = "gondor_plugins"
defaults["base"]["plugin_bootstrap_module"] = "gondor.cli.ext"

defaults["project"] = {
    "config_dir": GONDOR_CONFIG_DIRECTORY,
    "repo_root": None,
}

defaults["auth"] = {
    "username": None,
    "password": None,
}

defaults["gondor"] = {}
defaults["gondor"]["vcs"] = None

# create an application
app = foundation.lay_cement("gondor", defaults=defaults)

# define application hooks
hook.define("pre_compress_tarball")

# define handlers
handler.define(interfaces.ProjectPackager)

# register the handlers
handler.register(controllers.Base)
handler.register(controllers.Deploy)

handler.register(handlers.GitProjectPackager)
handler.register(StreamOutputHandler)

handler.register(GondorPluginHandler)

# setup the application
app.setup()

# Add Local Environment Settings to the Config
try:
    packager = handler.get("project_packager", app.config.get("gondor", "vcs"))(app.config)
except CementRuntimeError:
    raise  # @@@ Print an error message

app.config.merge({
    "project": {
        "repo_root": packager.get_repo_root(os.getcwd()),
        "root": utils.find_nearest(os.getcwd(), ".gondor"),
    }
})


def main():
    app.run()
