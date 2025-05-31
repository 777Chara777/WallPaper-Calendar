import os
import json
import time
import threading
import datetime
from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from src.core.client_manager import OAuthTokenReceiver
from src.utils import check_token
from src.utils import Logger

from PyQt5.QtWidgets import QListWidget, QListWidgetItem
from PyQt5.QtGui import QColor


SCOPES = ["https://www.googleapis.com/auth/calendar.readonly", "https://www.googleapis.com/auth/tasks.readonly"]

color_map: dict[int, str] = {
    1: "#ff0000",
    4: "#ffc532"
}
event_map = {
    "event": "[EVEN]",
    "task": "[TASK]"
}

def date_until(date_str: str):
    # Удалим пробелы после двоеточий (если есть)
    date_str = date_str.replace(": ", ":")

    # Попробуем сначала распарсить как datetime с временем
    try:
        target = datetime.datetime.fromisoformat(date_str)
    except ValueError:
        # Если не получилось — значит, это просто дата
        target = datetime.datetime.fromisoformat(date_str + "T00:00:00")

    return target

def days_until(date: datetime.datetime):
    return (date.date() - datetime.datetime.now().date()).days

def human_days_until(date: datetime.datetime):
    delta = days_until(date)
    time = "%02d:%02d" % (date.hour, date.minute)
    if delta == 0:
        return f"сегодня в {time}"
    elif delta == 1:
        return f"завтра в {time}"
    elif delta == 2:
        return f"послезавтра в {time}"
    else:
        return f"через {delta} дней ({date.day} {date.strftime('%B')})"


def get_color(date: datetime.datetime) -> str:
    delta = days_until(date)
    for color in color_map:
        if color >= delta:
            return color_map[color]
    return "#ffffff"


class CalendarManager:
    def __init__(self, list_widget: QListWidget, get_event_limit, get_auth):
        self.list_widget = list_widget
        self.get_event_limit = get_event_limit
        self.get_auth = get_auth

        self.logger = Logger("CalendarManager")
        self.client_network = OAuthTokenReceiver(None)

    def get_events(self) -> list:
        try:
            service_calendar, service_tasks = self.get_google_service()

            now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
            merged_items = []

            events_result = service_calendar.events().list(
                calendarId='primary', 
                timeMin=now,
                maxResults=self.get_event_limit(), 
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            calendar_events = events_result.get("items", [])
            # Преобразуем события в общий формат
            for event in calendar_events:
                start = event["start"].get("dateTime", event["start"].get("date"))
                merged_items.append({
                    "title": event.get("summary", "Без названия"),
                    "datetime": start,
                    "type": "event"
                })

            # Получаем задачи из всех списков
            tasklists = service_tasks.tasklists().list(maxResults=self.get_event_limit()).execute().get("items", [])
            for tasklist in tasklists:
                tasks = service_tasks.tasks().list(tasklist=tasklist["id"]).execute().get("items", [])
                for task in tasks:
                    if task.get("status") != "completed":
                        due = task.get("due")  # Может быть None
                        merged_items.append({
                            "title": task.get("title", "Без названия"),
                            "datetime": due if due else "9999-12-31T00:00:00Z",
                            "type": "task"
                        })

            # Сортировка по дате
            merged_items.sort(key=lambda x: x["datetime"])

            return merged_items
        except Exception as ex:
            self.logger.warm(f"Error (get_events) : {ex.__class__} {ex}" )
        return []        

    def update_events(self):
        if not check_token():
            self.logger.info("mmmmm no token.json")
            return
        def fetch():
            try:
                events = self.get_events()[:self.get_event_limit()]

                self.list_widget.clear()

                for event in events:
                    start_str = event['datetime']
                    type_event = event['type']
                    title = event['title']
                    icon = event_map.get(type_event, "❓")

                    dt = date_until(start_str)
                    label = f"• {icon} {title} — {human_days_until(dt)}"
                    label_color = get_color(dt)

                    item = QListWidgetItem(label)
                    item.setForeground(QColor(label_color))
                    self.list_widget.addItem(item)

            except Exception as ex:
                self.logger.warm(f"Error (update_events): {ex.__class__} {ex}")
                self.list_widget.clear()
                self.list_widget.addItem("• Ошибка загрузки событий.")

        threading.Thread(target=fetch, daemon=True).start()

    # @staticmethod
    # def get_google_service():
    #     creds = None
    #     if check_token():
    #         creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    #     return build('calendar', 'v3', credentials=creds), build("tasks", "v1", credentials=creds)
    
    def get_google_service(self):
        creds = None
        if check_token():
            token_data = json.load(open('token.json', 'r'))
            expires_at = token_data.get('expires_at', 0)
            if time.time() > expires_at - 300:  # Обновляем если истекает через 5 минут
                self.logger.info("refresh token")
                # Тут можно вызвать обновление токена# заглушки
                self.client_network.refresh_token()
                token_data = json.load(open('token.json', 'r'))

            creds = Credentials(
                token=token_data.get("access_token"),
                # refresh_token=token_data.get("refresh_token"),
                # token_uri="https://oauth2.googleapis.com/token",
                # client_id='ваш_client_id',
                # client_secret='ваш_client_secret',
                # scopes=SCOPES,
                # expiry=None if 'expires_at' not in token_data else datetime.datetime.fromtimestamp(token_data['expires_at'])
            )
        return build('calendar', 'v3', credentials=creds), build("tasks", "v1", credentials=creds)

    def authorize(self):
        auth_link = self.get_auth()
        if auth_link != "":
            self.logger.info("Autorize start...")
            creds = self.client_network.run(True)
            with open('token.json', 'w') as token:
                token.write(json.dumps(creds))