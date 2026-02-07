# ruff: noqa F401
from .python4cpm import Python4CPM
from importlib.metadata import version as __version

__version__ = __version(__name__)
