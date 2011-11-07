from cement2.core import handler

from gondor.cli.core.commands import base
from gondor.cli.core.commands import deploy


def register():
    handler.register(base.Base)
    handler.register(deploy.Deploy)
