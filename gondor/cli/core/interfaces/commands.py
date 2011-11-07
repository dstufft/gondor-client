from cement2.core import controller

from gondor.api import Gondor


class BaseCommand(controller.CementBaseController):
    
    def setup(self, *args, **kwargs):
        super(BaseCommand, self).setup(*args, **kwargs)
        
        self.api = Gondor(
            username=self.config.get("auth", "username"),
            password=self.config.get("auth", "password") if self.config.has_key("auth", "password") else None,
            key=self.config.get("auth", "key") if self.config.has_key("auth", "key") else None,
            site_key=self.config.get("gondor", "site_key"),
        )
