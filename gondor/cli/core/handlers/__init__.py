from gondor.cli.core import handler

from gondor.cli.core.handlers import outputs
from gondor.cli.core.handlers import packagers
from gondor.cli.core.handlers import plugins


def register():
    handler.register(outputs.StreamOutputHandler)
    handler.register(packagers.GitProjectPackager)
    handler.register(plugins.GondorPluginHandler)
