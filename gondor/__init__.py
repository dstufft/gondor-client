from gondor.version import get_version

__version__ = get_version()

__import__("pkg_resources").declare_namespace(__name__)
