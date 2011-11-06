import os

from gondor import utils
from gondor.interfaces import ProjectPackager


class BaseProjectPackager(object):
    
    def __init__(self, config):
        self.config = config


class GitProjectPackager(BaseProjectPackager):
    class meta:
        interface = ProjectPackager
        label = "git"
    
    def get_repo_root(self, directory):
        return utils.find_nearest(directory, ".git")
    
    def package_project(self, label, commit):
        sha = None
        tar_path = None
        
        try:
            try:
                git = utils.find_command("git")
            except utils.BadCommand:
                raise  # @@@ Do Something for the Error Condition Here
            
            check, sha = utils.run_proc([git, "rev-parse", commit])
            
            if check != 0:
                print "could not map '%s' to a SHA\n" % commit
            
            if commit == "HEAD":
                commit = sha
            
            tar_path = os.path.abspath(os.path.join(self.config.get("project", "repo_root"), "%s-%s.tar" % (label, sha)))
            cmd = [git, "archive", "--format=tar", commit, "-o", tar_path]
            
            check, output = utils.run_proc(cmd, cwd=self.config.get("project", "repo_root"))
            
            if check != 0:
                print output
        except:
            if tar_path and os.path.exists(tar_path):
                os.unlink(tar_path)
            return None, commit, sha
        else:
            return tar_path, commit, sha
