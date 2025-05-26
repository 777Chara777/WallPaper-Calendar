from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton
from core.calendar_manager import CalendarManager


class SettingsWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Настройки")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout()
        self.event_input = QLineEdit()
        self.event_input.setPlaceholderText("Название события")

        self.add_button = QPushButton("Добавить событие")
        self.add_button.clicked.connect(self.add_event)

        layout.addWidget(QLabel("Добавить событие в календарь:"))
        layout.addWidget(self.event_input)
        layout.addWidget(self.add_button)
        self.setLayout(layout)

    def add_event(self):
        title = self.event_input.text()
        if title:
            CalendarManager.add_event(title)
            self.event_input.clear()

