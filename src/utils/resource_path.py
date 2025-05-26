import os
import sys

def resource_path(relative_path):
    """Возвращает абсолютный путь до ресурса, работает и в PyInstaller, и при разработке"""
    if hasattr(sys, '_MEIPASS'):
        # В режиме сборки с PyInstaller
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)