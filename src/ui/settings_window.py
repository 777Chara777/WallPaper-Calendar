from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt, QSettings


class SettingsWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Настройки")
        self.setWindowFlags(self.windowFlags() | Qt.Window)
        self.setFixedSize(300, 200)

        main_layout = QVBoxLayout()

        self.settings = QSettings("Dorko", "WallpaperCalendar")

        # Горизонтальный layout для count_input
        count_layout = QHBoxLayout()
        count_layout.addWidget(QLabel("Сколько событий показывать:"))
        self.count_input = QLineEdit()
        self.count_input.setPlaceholderText("По умолчанию 5")
        count_layout.addWidget(self.count_input)
        main_layout.addLayout(count_layout)

        # Горизонтальный layout для opacity
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(QLabel("Прозрачность (0.0 - 1.0):"))
        self.opacity_input = QLineEdit()
        self.opacity_input.setPlaceholderText("По умолчанию 0.3")
        opacity_layout.addWidget(self.opacity_input)
        main_layout.addLayout(opacity_layout)

        # Горизонтальный layout для кнопок
        buttons_layout = QHBoxLayout()
        self.ok_button = QPushButton("Готово")
        self.cancel_button = QPushButton("Отмена")
        buttons_layout.addStretch(1)  # Отодвинет кнопки вправо
        buttons_layout.addWidget(self.ok_button)
        buttons_layout.addWidget(self.cancel_button)
        main_layout.addLayout(buttons_layout)

        self.setLayout(main_layout)

        # Подключаем слоты
        self.ok_button.clicked.connect(self._accept)
        self.cancel_button.clicked.connect(self._reject)

    def _accept(self, event):
        # opacity
        opacity = self.settings.value("window_opacity")
        try:
            opacity = float(self.opacity_input.text())
        except ValueError:
            pass
        if opacity:
            self.settings.setValue("window_opacity", opacity)
        
        # event limit
        event_limit = self.settings.value("window_event_limit")
        try:
            event_limit = float(self.count_input.text())
        except ValueError:
            pass
        if event_limit:
            self.settings.setValue("window_event_limit", event_limit)

        self.hide()

    def _reject(self, event):
        self.hide()

    def get_event_limit(self) -> int:
        try:
            event_limit = int(self.settings.value("window_event_limit"))
            if event_limit:
                return event_limit
        except (ValueError, TypeError):
            pass
        return 5

    def get_opacity(self) -> float:
        try:
            opacity = float(self.settings.value("window_opacity"))
            if opacity:
                return opacity
        except (ValueError, TypeError):
            pass
        return 0.3


    def closeEvent(self, event):
        event.ignore()
        self.hide()