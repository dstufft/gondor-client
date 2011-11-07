from gondor.cli.core import controller


class Command(controller.CementBaseController):
    class meta:
        interface = controller.IController
        label = "base"
        description = "Effortless production Django hosting"
        
        defaults = {}
        arguments = []
    
    @controller.expose(hide=True)
    def default(self):
        print "display help text"
