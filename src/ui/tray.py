### ui/tray.py
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon, QCursor
from PyQt5.QtCore import Qt

from src.utils.resource_path import resource_path


class TrayIcon(QSystemTrayIcon):
    """
    Иконка в системном трее с меню управления приложением.
    Поддерживает левый клик для вызова меню.
    """

    def __init__(self, app, widget, settings_window):
        icon = QIcon(resource_path("assets/icon.png"))
        super().__init__(icon, app)

        self._widget = widget
        self._settings = settings_window

        # Создаем контекстное меню
        self.menu = QMenu()
        open_action = QAction("Open", self, triggered=self._widget.show)
        settings_action = QAction("Settings", self, triggered=self._settings.show)
        exit_action = QAction("Exit", self, triggered=self._exit)

        self.menu.addAction(open_action)
        self.menu.addAction(settings_action)
        self.menu.addSeparator()
        self.menu.addAction(exit_action)

        self.setContextMenu(self.menu)
        self.setToolTip("The calendar has been launched")

        # Обработка кликов на иконке
        self.activated.connect(self._on_activated)

    def _on_activated(self, reason):
        # При левой кнопке (Trigger) показываем меню
        if reason == QSystemTrayIcon.Trigger:
            # Показываем меню в позиции курсора
            self.menu.exec_(QCursor.pos())

    def _exit(self):
        self._widget.close()
        self._settings.close()
        self.hide()
        QApplication.quit()