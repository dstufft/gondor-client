from cement2.core import controller


class Base(controller.CementBaseController):
    class meta:
        interface = controller.IController
        label = "base"
        description = "Effortless production Django hosting"
        
        defaults = {}
        arguments = []
    
    @controller.expose(hide=True)
    def default(self):
        print "display help text"
