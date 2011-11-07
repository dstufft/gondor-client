from cement2.core import handler
from cement2.core import hook

from gondor.cli.core.interfaces import packagers


def register():
    handler.define(packagers.ProjectPackager)
    
    hook.define("pre_compress_tarball")
