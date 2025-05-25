import threading
import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from typing import List, Any

# SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

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
    time = "%2d:%2d" % (date.hour, date.minute)
    if delta == 0:
        return f"сегодня в {time}"
    elif delta == 1:
        return f"завтра в {time}"
    elif delta == 2:
        return f"послезавтра в {time}"
    else:
        return f"через {delta} дней ({date.day} {date.strftime('%B')})"

color_map: dict[int, str] = {
    1: "#ff0000",
    4: "#ffc532"
}

class CalendarManager:
    def __init__(self, label_widgets: List[Any]):
        # Ожидаем список QLabel
        self.labels: List = label_widgets

    def get_events(self) -> list:
        try:
            service = self.get_google_service()
            now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
            events_result = service.events().list(
                calendarId='primary', timeMin=now,
                maxResults=len(self.labels), singleEvents=True,
                orderBy='startTime'
            ).execute()
            return events_result.get('items', [])
        except Exception as ex:
            print(f"Error (get_events) : {ex}" )
        return []        

    def update_events(self):
        def fetch():
            try:
                events = self.get_events()

                # Подготовить список текстов для меток
                texts = []
                for event in events:
                    start: str = event['start'].get('dateTime', event['start'].get('date'))
                    time = date_until(start)
                    texts.append([days_until(time), f"• {event['summary']} - {human_days_until(time)}"])

                # Если событий меньше, чем меток, заполняем оставшиеся пустыми строками
                while len(texts) < len(self.labels):
                    texts.append([None, ""])

                # Обновляем QLabel в основном потоке
                for lbl, (day, txt) in zip(self.labels, texts):
                    if day is not None:
                        for color in color_map:
                            if color >= day:
                                lbl.set_text_color( color_map[color] )
                                break
                    lbl.setText(txt or "Нет события")

            except Exception as ex:
                print(f"Error (update_events) : {ex}" )
                for lbl in self.labels:
                    lbl.setText("Ошибка загрузки событий.")

        threading.Thread(target=fetch, daemon=True).start()

    @staticmethod
    def add_event(title):
        print("addds")
        # now = datetime.utcnow()
        # end = now + timedelta(hours=1)
        # event = {
        #     'summary': title,
        #     'start': {'dateTime': now.isoformat() + 'Z'},
        #     'end': {'dateTime': end.isoformat() + 'Z'}
        # }
        # service = CalendarManager.get_google_service()
        # service.events().insert(calendarId='primary', body=event).execute()

    @staticmethod
    def get_google_service():
        try:
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        except:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        return build('calendar', 'v3', credentials=creds)

