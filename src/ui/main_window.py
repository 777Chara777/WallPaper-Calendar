from PyQt5.QtCore import Qt, QTimer, QSettings
from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QListWidget, QDialog,
    QMenu
)

from src.core.calendar_manager import CalendarManager
from src.utils import get_token, check_token, Logger
from src.ui.settings_window import SettingsWindow

class DesktopWidget(QWidget):
    _drag_pos = None
    _is_movable = False
    """
    Transparent widget displaying a list of events and tasks.
    Supports saving position and number of events from settings.
    """

    def __init__(self, settings_window: SettingsWindow):
        super().__init__()
        self.logger = Logger("DesktopWidget")
        self.settings = settings_window
        self._init_window()
        self._init_ui()
        self._init_timer()
        self._init_settings()

    def _init_window(self):
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnBottomHint |
            Qt.Tool |
            Qt.X11BypassWindowManagerHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(self.settings.get_opacity())
        self.resize(280, 520)
        
        self._load_position()

    def _init_ui(self):
        self.logger.info("Initializing UI...")
        self.setMouseTracking(True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        self.header = QLabel("Upcoming events and tasks:")
        self.header.setObjectName("header")
        self.header.setContextMenuPolicy(Qt.CustomContextMenu)
        self.header.customContextMenuRequested.connect(self._show_header_menu)
        layout.addWidget(self.header)

        self.event_list = QListWidget()
        self.event_list.setWordWrap(True)
        self.event_list.adjustSize()
        self.event_list.setSizePolicy(self.sizePolicy().Expanding, self.sizePolicy().Expanding)
        self.event_list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.event_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.event_list.setFocusPolicy(Qt.NoFocus)
        self.event_list.setSelectionMode(QListWidget.NoSelection)
        self.event_list.setObjectName("eventList")
        layout.addWidget(self.event_list, stretch=1)

        self.manager = CalendarManager(self.event_list, self._get_event_limit, self.settings.get_auth)
        auth_link = self.manager.get_auth()
        if auth_link != "":
            self.manager.client_network.set_server_url(auth_link)

    def _init_settings(self):
        self.logger.info("Applying settings...")
        self.event_list.clear()
        if not check_token():
            self.event_list.addItem("Please configure authorization in settings and restart the application.")
            self.manager.authorize()
        elif check_token() and "error" in get_token():
            self.event_list.addItem("Error in token.json. Please check its contents.")
        elif self.manager.client_network._check_server() != 200:
            self.event_list.addItem("The server is not responding!")

    def _update_ui(self):
        self.setWindowOpacity(self.settings.get_opacity())
        auth_link = self.manager.get_auth()
        if auth_link != "":
            self.manager.client_network.set_server_url(auth_link)
        self.manager.update_events()

    def _init_timer(self):
        self.logger.info("Initializing update timer...")
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.manager.update_events)
        self.timer.start(5 * 60 * 1000)  # every 5 minutes
        self.manager.update_events()

    def _show_header_menu(self, pos):
        menu = QMenu(self)
        menu.addAction("Settings", self._show_settings)
        menu.addSeparator()
        menu.addAction("Toggle Pin", self._toggle_pin)
        menu.addAction("Refresh", self.manager.update_events)
        menu.exec_(self.header.mapToGlobal(pos))

    def _show_settings(self):
        self.settings.exec_()  # Waits for the settings dialog to close
        self._update_ui()

    def _toggle_pin(self):
        flags = int(self.windowFlags())
        if flags & Qt.WindowStaysOnBottomHint:
            flags &= ~Qt.WindowStaysOnBottomHint
            self._is_movable = True
            self.logger.info("Widget unpinned and now movable.")
        else:
            flags |= Qt.WindowStaysOnBottomHint
            self._is_movable = False
            self.logger.info("Widget pinned to bottom and locked.")
        self.setWindowFlags(Qt.WindowFlags(flags))
        self.show()

    def _get_event_limit(self):
        return self.settings.get_event_limit()

    def _load_position(self):
        settings = QSettings("Dorko", "WallpaperCalendar")
        pos = settings.value("window_pos")
        if pos:
            self.move(pos)
            self.logger.info(f"Loaded saved position: {pos}")

    def _save_position(self):
        settings = QSettings("Dorko", "WallpaperCalendar")
        settings.setValue("window_pos", self.pos())

    def closeEvent(self, event):
        self._save_position()
        super().closeEvent(event)

    def enterEvent(self, event):
        self.setWindowOpacity(1.0)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setWindowOpacity(self.settings.get_opacity())
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if self._is_movable and event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._is_movable and event.buttons() & Qt.LeftButton and self._drag_pos:
            self.move(event.globalPos() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        self._save_position()
        super().mouseReleaseEvent(event)
