import re
import os

from gondor import utils
from gondor.cli.core.interfaces import ProjectPackager


class BaseProjectPackager(object):
    
    def __init__(self, config):
        self.config = config


class GitProjectPackager(BaseProjectPackager):
    class meta:
        interface = ProjectPackager
        label = "git"
    
    def get_repo_root(self, directory):
        try:
            return utils.find_nearest(directory, ".git")
        except OSError:
            return None
    
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
                # @@@ Do Something for the Error Condition Here
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


class MercurialProjectPackager(BaseProjectPackager):
    class meta:
        interface = ProjectPackager
        label = "hg"
    
    def get_repo_root(self, directory):
        try:
            return utils.find_nearest(directory, ".hg")
        except OSError:
            return None
    
    def package_project(self, label, commit):
        sha = None
        tar_path = None
        
        try:
            try:
                hg = utils.find_command("hg")
            except utils.BadCommand:
                raise  # @@@ Do Something for the Error Condition Here
            
            branches_stdout = utils.run_proc([hg, "branches"])[1]
            tags_stdout = utils.run_proc([hg, "tags"])[1]
            
            refs = {}
            for line in branches_stdout.splitlines() + tags_stdout.splitlines():
                m = re.search(r"([\w\d\.-]+)\s*([\d]+):([\w]+)$", line)
                if m:
                    refs[m.group(1)] = m.group(3)
            
            try:
                sha = refs[commit]
            except KeyError:
                raise  # @@@ Do Something for the Error Condition Here
            
            tar_path = os.path.abspath(os.path.join(self.config.get("project", "repo_root"), "%s-%s.tar" % (label, sha)))
            cmd = [hg, "archive", "-p", ".", "-t", "tar", "-r", commit, tar_path]
            
            check, output = utils.run_proc(cmd, cwd=self.config.get("project", "repo_root"))
            
            if check != 0:
                # @@@ Do Something for the error here
                print output
        except:
            if tar_path and os.path.exists(tar_path):
                os.unlink(tar_path)
            return None, commit, sha
        else:
            return tar_path, commit, sha
