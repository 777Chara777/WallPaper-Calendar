### ui/main_window.py
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QMenu, QAction, QDialog, QPushButton, QHBoxLayout, QListWidget
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPoint
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from src.core.calendar_manager import CalendarManager

# Диалог карточки события
class EventCardDialog(QDialog):
    def __init__(self, event_text, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Событие")
        self.setFixedSize(300, 150)
        layout = QVBoxLayout()
        layout.addWidget(QLabel(event_text))
        btn_layout = QHBoxLayout()
        edit_btn = QPushButton("Изменить")
        delete_btn = QPushButton("Удалить")
        edit_btn.clicked.connect(self.edit_event)
        delete_btn.clicked.connect(self.delete_event)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def edit_event(self):
        # TODO: добавить логику редактирования
        self.accept()

    def delete_event(self):
        # TODO: добавить логику удаления через CalendarManager
        self.accept()

# Клик- и hover-метка для события
class ReminderLabel(QLabel):
    hovered = pyqtSignal()
    clicked = pyqtSignal(str)

    def __init__(self, text=''):
        super().__init__(text)
        self.default_color: str="#ffffff"
        self.setStyleSheet(f"color: {self.default_color}; padding: 2px;")
        self.setAttribute(Qt.WA_Hover)

    def enterEvent(self, event):
        # подсветка при наведении
        self.setStyleSheet(f"color: {self.default_color}; background-color: rgba(255, 255, 255, 50); padding: 2px;")
        super().enterEvent(event)

    def leaveEvent(self, event):
        # отменить подсветку
        self.setStyleSheet(f"color: {self.default_color}; padding: 2px;")
        super().leaveEvent(event)

    def set_text_color(self, color: str):
        self.default_color = color
        self.setStyleSheet(f"color: {color}; padding: 2px;")

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.text())
        super().mouseReleaseEvent(event)

class DesktopWidget(QWidget):
    def __init__(self, settings_window):
        super().__init__()
        self.settings_window = settings_window
        # self.screen_geometry = self.geometry()
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnBottomHint |
            Qt.Tool |
            Qt.X11BypassWindowManagerHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(0.3)
        # self.setStyleSheet("""
        #     background-color: rgba(30, 30, 30, 200);
        #     color: white;
        #     font-size: 14px;
        #     border-radius: 10px;
        # """)
        self.event_list = QListWidget()
        self.event_list.setMouseTracking(True)
        self.event_list.setStyleSheet("""
            QListWidget {
                background: transparent;
                border: none;
            }
            QListWidget::item {
                padding: 8px;
                margin: 2px 0;
                border-radius: 6px;
            }
            QListWidget::item:hover {
                background: rgba(255, 255, 255, 30);
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        # Заголовок с меню
        self.header = QLabel("Ближайшие события:")
        self.header.setContextMenuPolicy(Qt.CustomContextMenu)
        self.header.customContextMenuRequested.connect(self.show_header_menu)
        layout.addWidget(self.header)

        self.reminder_labels = []
        for _ in range(5):
            lbl = ReminderLabel("Загрузка...")
            lbl.clicked.connect(self.open_event_card)
            layout.addWidget(lbl)
            self.reminder_labels.append(lbl)

        self.setLayout(layout)
        self.resize(200, 200)
        # screen_width = self.screen_geometry.width()
        # screen_height = self.screen_geometry.height()
        self.move(50, 50)

        self.manager = CalendarManager(self.reminder_labels)
        self.timer = QTimer()
        self.timer.timeout.connect(self.manager.update_events)
        self.timer.start(300000) # 5 MIN
        self.manager.update_events()

    def show_header_menu(self, pos):
        menu = QMenu()
        menu.addAction(QAction("Настройки", self, triggered=self.settings_window.show))
        menu.addSeparator()
        pin = QAction("Закрепить/Отпустить", self, triggered=self.toggle_pin)
        menu.addAction(pin)
        menu.addAction(QAction("Изменить размер", self, triggered=self.settings_window.show))
        menu.addAction(QAction("Opacity", self, triggered=self.settings_window.show))
        menu.exec_(self.header.mapToGlobal(pos))

    def toggle_pin(self):
        flags = self.windowFlags()
        if flags & Qt.WindowStaysOnBottomHint:
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.X11BypassWindowManagerHint)
        else:
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.show()

    def enterEvent(self, event):
        self.setWindowOpacity(1.0)

    def leaveEvent(self, event):
        self.setWindowOpacity(0.3)

    def open_event_card(self, text):
        dlg = EventCardDialog(text, self)
        dlg.exec_()
