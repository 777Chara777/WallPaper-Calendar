
### main.py
from PyQt5.QtWidgets import QApplication
import threading
import argparse
import sys

from src.utils.resource_path import resource_path
from src.utils import Logger
from src.ui.main_window import DesktopWidget
from src.ui.settings_window import SettingsWindow
from src.ui.tray import TrayIcon

import server as flask_app



class CalendarApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.logger = Logger("CalendarApp")

        # Загружаем стили QSS
        try:
            with open(resource_path('assets/style.qss'), 'r', encoding='utf-8') as f:
                self.app.setStyleSheet(f.read())
        except FileNotFoundError:
            print("Warning: style.qss not found, using default styles.")


        self.settings_window = SettingsWindow()
        self.main_widget = DesktopWidget(self.settings_window)
        self.tray_icon = TrayIcon(self.app, self.main_widget, self.settings_window)

    def run(self):
        self.logger.info("Run..")
        self.main_widget.show()
        self.tray_icon.show()

        sys.exit(self.app.exec_())

class ServerApp:
    def __init__(self, ip: str = "127.0.0.1", port: int = 5000):
        self.logger = Logger("ServerApp")
        self.ip = ip
        self.port = port

    def run(self):
        self.logger.info("Run..")
        flask_app.app.run(host=self.ip, port=self.port)

def main():
    parser = argparse.ArgumentParser(description="Google Calendar App with optional server.")
    parser.add_argument(
        "--mode",
        choices=["calendar", "server", "all"],
        default="calendar",
        help="Run mode: calendar GUI, Flask server, or both",
    )
    parser.add_argument("--ip", default="127.0.0.1", help="Server IP address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=5000, help="Server port (default: 5000)")

    args = parser.parse_args()

    if args.mode == "calendar":
        CalendarApp().run()
    elif args.mode == "server":
        ServerApp(args.ip, args.port).run()
    elif args.mode == "all":
        # Запускаем Flask-сервер в отдельном потоке
        server_thread = threading.Thread(target=ServerApp(args.ip, args.port).run, daemon=True)
        server_thread.start()

        # Запускаем календарь
        CalendarApp().run()

if __name__ == "__main__":
    main()