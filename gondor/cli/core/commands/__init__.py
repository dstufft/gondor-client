from cement2.core import handler

from gondor.cli.core.commands.base import Base
from gondor.cli.core.commands.create import Create
from gondor.cli.core.commands.deploy import Deploy
from gondor.cli.core.commands.init import Init


def register():
    handler.register(Base)
    handler.register(Create)
    handler.register(Deploy)
    handler.register(Init)
