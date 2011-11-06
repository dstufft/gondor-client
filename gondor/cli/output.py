import sys

from cement2.core import output


class StreamOutputHandler(object):
    class meta:
        interface = output.IOutput
        label = 'stream'
    
    def __init__(self, normal=None, error=None, **kwargs):
        self.streams = {
            "normal": normal if normal is not None else sys.stdout,
            "error": error if error is not None else sys.stderr
        }
        self.streams.update(kwargs)
        
        self.config = None
    
    def setup(self, config_obj):
        self.config = config_obj
    
    def render(self, data, template=None):
        stream = self.streams[data.get("level", "normal")]
        if "message" in data:
            msg = data["message"] if data.get("raw", False) else "%s\n" % data["message"]
            stream.write(msg)
