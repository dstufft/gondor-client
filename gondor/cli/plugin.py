from cement2.core import plugin
from cement2.core import util

from cement2.lib.ext_plugin import CementPluginHandler


class GondorPluginHandler(CementPluginHandler):
    class meta:
        interface = plugin.IPlugin
        label = "gondor_plugins"
    
    def setup(self, config_obj):
        self.config = config_obj
        
        plugins = dict([(x[0], x[1] if x[1] is not "" else True) for x in self.config.items("ext")])
        for plugin, status in plugins.iteritems():
            if util.is_true(status):
                self.enabled_plugins.append(plugin)
            else:
                self.disabled_plugins.append(plugin)
