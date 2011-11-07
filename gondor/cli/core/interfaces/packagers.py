from gondor.cli.core import interface


class ProjectPackager(interface.Interface):
    class imeta:
        label = "project_packager"
        
    # Must be provided by the implementation
    meta = interface.Attribute("Handler meta-data")
    
    def __init__(self, config):
        """
        This function takes a config option that represents the application config.
        """
        
    def get_repo_root(self, directory):
        """
        This function returns the repository root of the repo that contains the
        directory given by the directory arg.
        """
    
    def package_project(self, label, commit):
        """
        This function takes a label and a commit and generates on disk a
        suitable tarball of the project. It then returns the path to this
        tarball, a string representing the commit, and a string representing the
        sha or internal identifier of the commit.
        """
