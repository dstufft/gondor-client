from gondor.cli.core import handler

from gondor.cli.core.commands import base
from gondor.cli.core.commands import deploy


def register():
    handler.register(base.Command)
    handler.register(deploy.Command)
