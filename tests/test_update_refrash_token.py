import unittest
import threading

from utils import Logger
from main import ServerApp

import os

class TestUpdateRefreshToken(unittest.TestCase):

    def __init__(self, methodName = "runTest"):
        super().__init__(methodName)

        self.logger = Logger(self.__class__.__name__)


    def test_update_token(self):
        server_thread = threading.Thread(target=ServerApp().run, daemon=True)
        self.logger.info("Server starting...", )
        server_thread.start()
        self.logger.info("Server Done")
        
        test_token_date = os.getenv("FUNNNYTOKEN", None)

        