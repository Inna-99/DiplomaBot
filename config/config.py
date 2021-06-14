TOKEN = None

DATABASE = None
USER = None
PASSWORD = None
HOST = None
PORT = None

DEFAULT_LANGUAGE = None

try:
    from .local_config import *
except ImportError:
    pass
