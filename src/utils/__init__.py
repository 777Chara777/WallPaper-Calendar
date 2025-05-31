from .resource_path import resource_path
from .Logger.logger import Logger
import os

__all__ = ("resource_path", "check_token", "Logger", )

def check_token() -> bool:
    "check token"
    return os.path.isfile("token.json")