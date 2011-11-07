from cement2.core import controller

from gondor.api import Gondor


class BaseCommand(controller.CementBaseController):
    
    def setup(self, *args, **kwargs):
        super(BaseCommand, self).setup(*args, **kwargs)
        
        key = self.config.get("auth", "key") if "key" in self.config.keys("auth") else None
        password = self.config.get("auth", "password") if "password" in self.config.keys("auth") else None
        
        api_url = self.config.get("gondor", "endpoint") if "endpoint" in self.config.keys("gondor") else None
        
        self.api = Gondor(
            username=self.config.get("auth", "username"),
            password=password,
            key=key,
            site_key=self.config.get("gondor", "site_key"),
            api_url=api_url,
        )
