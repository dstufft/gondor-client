from cement2.core import controller

from gondor.cli.core.interfaces import BaseCommand


class Base(BaseCommand):
    class meta:
        interface = controller.IController
        label = "base"
        description = "Effortless production Django hosting"
        
        defaults = {}
        arguments = []
    
    @controller.expose(hide=True)
    def default(self):
        print "display help text"
