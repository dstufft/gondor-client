from cement2.core import handler
from cement2.core import hook

from gondor.cli.core.interfaces.commands import BaseCommand
from gondor.cli.core.interfaces.packagers import ProjectPackager


def register():
    handler.define(ProjectPackager)
    
    hook.define("pre_compress_tarball")
