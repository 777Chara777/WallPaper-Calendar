import time
from dataclasses import dataclass

from .utils._dop import getframe

__all__ = ("Logger", )

@dataclass
class LoggerLevel:
    level: str
    wight: int
    debug: bool = False

class Logger():
    __version__: str = "0.2"
    _config = {
        "message_format": "[{time}:{level}] ({name}:{func}:{line}): {message}",
        "print_wight": -1,
        "out_put_print": None
    }

    def __init__(self, name: str, out_print: str = None) -> None:
        self.name = name
        if out_print is not None:
            Logger.set_outprint(out_print)
        
        
    @classmethod
    def set_format(cls, format: str):
        cls._config["message_format"] = format

    @classmethod
    def set_wight(cls, wight: int):
        cls._config["print_wight"] = wight
    
    @classmethod
    def set_outprint(cls, path: str):
        cls._config["out_put_print"] = path


    def _getformat(self, messages: str, level: str) -> str:
        _, func, line = getframe(0)
        return Logger._config["message_format"].replace("{time}", time.strftime("%H:%M:%S", time.gmtime(time.time()))) \
                    .replace("{name}", self.name) \
                    .replace("{message}", "".join([str(message) for message in messages])) \
                    .replace("{level}", level) \
                    .replace("{func}", func) \
                    .replace("{line}", str(line)) 

    def _log(self, message: str, options: LoggerLevel, **kwargs):
        send_message = self._getformat(message, options.level)
        if Logger._config['print_wight'] < options.wight:
            print( send_message, **kwargs )

        if Logger._config['out_put_print'] is not None:
            with open(Logger._config['out_put_print'],  "a", encoding="utf-8") as logger:
                logger.write( send_message + ("\n" if kwargs.get("end", "") != "\r" else " -> " ) )

        if options.debug:
            return send_message

    def debug(self, *message: str, **kwargs) -> None:
        self._log( message, LoggerLevel("DEBUG", 0), **kwargs )

    def info(self, *message: str, **kwargs) -> None:
        self._log( message, LoggerLevel("INFO", 1), **kwargs )

    def warm(self, *message: str, **kwargs) -> None:
        self._log( message, LoggerLevel("WARNUNG", 2), **kwargs )

    def error(self, *message: str, **kwargs) -> None:
        self._log( message, LoggerLevel("ERROR", 3), **kwargs )

    @classmethod
    def reset(cls):
        cls._config = { "message_format": "[{time}:{level}] ({name}): {message}", "print_wight": -1, "out_put_print": None}