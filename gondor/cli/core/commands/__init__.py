from cement2.core import handler

from gondor.cli.core.commands.base import Base
from gondor.cli.core.commands.deploy import Deploy


def register():
    handler.register(Base)
    handler.register(Deploy)
