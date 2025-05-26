
### main.py
from PyQt5.QtWidgets import QApplication
import sys

from src.ui.main_window import DesktopWidget
from src.ui.settings_window import SettingsWindow
from src.ui.tray import TrayIcon

class CalendarApp:
    def __init__(self):
        self.app = QApplication(sys.argv)

        # Загружаем стили QSS
        try:
            with open('assets/style.qss', 'r', encoding='utf-8') as f:
                self.app.setStyleSheet(f.read())
        except FileNotFoundError:
            print("Warning: style.qss not found, using default styles.")


        self.settings_window = SettingsWindow()
        self.main_widget = DesktopWidget(self.settings_window)
        self.tray_icon = TrayIcon(self.app, self.main_widget, self.settings_window)

    def run(self):
        self.main_widget.show()
        self.tray_icon.show()

        sys.exit(self.app.exec_())



if __name__ == "__main__":
    CalendarApp().run()
