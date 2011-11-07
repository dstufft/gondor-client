from gondor.cli.core import handler
from gondor.cli.core import hook
from gondor.cli.core.interfaces import packagers


def register():
    handler.define(packagers.ProjectPackager)
    
    hook.define("pre_compress_tarball")
