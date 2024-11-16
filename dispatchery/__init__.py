# Author: Soufian Salim <soufian.salim@gmail.com>

"""
Dispatchery package.
"""

from importlib.metadata import version, PackageNotFoundError

from .main import dispatchery

try:
    __version__ = version("dispatchery")
except PackageNotFoundError:
    __version__ = "unknown"
