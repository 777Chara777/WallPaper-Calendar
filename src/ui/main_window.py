from PyQt5.QtCore import Qt, QTimer, QSettings
from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QListWidget, QDialog,
    QMenu
)

from src.core.calendar_manager import CalendarManager
from src.ui.settings_window import SettingsWindow

class DesktopWidget(QWidget):
    _drag_pos = None
    _is_movable = False
    """
    Прозрачный виджет, отображающий список событий и задач.
    Поддерживает сохранение позиции и количество событий из настроек.
    """

    def __init__(self, settings_window: SettingsWindow):
        super().__init__()
        self.settings = settings_window
        self._init_window()
        self._init_ui()
        self._init_timer()

    def _init_window(self):
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnBottomHint |
            Qt.Tool |
            Qt.X11BypassWindowManagerHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(self.settings.get_opacity())
        # self.setFixedSize(280, 520) # Халтура >:(
        self.resize(280, 520)
        
        # loads
        self._load_position()

    def _init_ui(self):
        self.setMouseTracking(True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        self.header = QLabel("Ближайшие события и задачи:")
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

        self.manager = CalendarManager(self.event_list, self._get_event_limit)

    def _update_ui(self):
        self.setWindowOpacity(self.settings.get_opacity())
        self.manager.update_events()

    def _init_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.manager.update_events)
        self.timer.start(5 * 60 * 1000)  # 5 минут
        self.manager.update_events()

    def _show_header_menu(self, pos):
        menu = QMenu(self)
        menu.addAction("Настройки", self._show_settings)
        menu.addSeparator()
        menu.addAction("Закрепить/Отпустить", self._toggle_pin)
        menu.addAction("Обновить", self.manager.update_events)
        menu.exec_(self.header.mapToGlobal(pos))

    def _show_settings(self):
        self.settings.exec_()  # <-- Ждёт закрытия окна
        self._update_ui()

    def _toggle_pin(self):
        flags = int(self.windowFlags())
        if flags & Qt.WindowStaysOnBottomHint:
            flags &= ~Qt.WindowStaysOnBottomHint
            self._is_movable = True
        else:
            flags |= Qt.WindowStaysOnBottomHint
            self._is_movable = False
        self.setWindowFlags(Qt.WindowFlags(flags))
        self.show()

    def _get_event_limit(self):
        return self.settings.get_event_limit()        

    def _load_position(self):
        settings = QSettings("Dorko", "WallpaperCalendar")
        pos = settings.value("window_pos")
        if pos:
            self.move(pos)

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
