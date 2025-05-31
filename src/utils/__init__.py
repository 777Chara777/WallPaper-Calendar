from .resource_path import resource_path
from .Logger.logger import Logger
import json
import os

__all__ = ("resource_path", "check_token", "get_token", "Logger", )

def check_token() -> bool:
    "check token"
    return os.path.isfile("token.json")

def get_token() -> dict | FileExistsError:
    assert check_token(), FileExistsError("No token.json file found to refresh token.")
    with open('token.json', "r", encoding="utf-8") as token:
        return json.load(token)