from cement2.core import handler

from gondor.cli.core.handlers.outputs import StreamOutputHandler
from gondor.cli.core.handlers.packagers import GitProjectPackager
from gondor.cli.core.handlers.packagers import MercurialProjectPackager
from gondor.cli.core.handlers.plugins import GondorPluginHandler


def register():
    handler.register(StreamOutputHandler)
    handler.register(GitProjectPackager)
    handler.register(MercurialProjectPackager)
    handler.register(GondorPluginHandler)
