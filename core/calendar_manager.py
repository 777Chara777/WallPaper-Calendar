import threading
import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

class CalendarManager:
    def __init__(self, label_widgets):
        # Ожидаем список QLabel
        self.labels = label_widgets

    def update_events(self):
        def fetch():
            try:
                service = self.get_google_service()
                now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
                events_result = service.events().list(
                    calendarId='primary', timeMin=now,
                    maxResults=len(self.labels), singleEvents=True,
                    orderBy='startTime'
                ).execute()
                events = events_result.get('items', [])

                # Подготовить список текстов для меток
                texts = []
                for event in events:
                    start = event['start'].get('dateTime', event['start'].get('date'))
                    texts.append(f"• {event['summary']} ({start})")

                # Если событий меньше, чем меток, заполняем оставшиеся пустыми строками
                while len(texts) < len(self.labels):
                    texts.append("")

                # Обновляем QLabel в основном потоке
                for lbl, txt in zip(self.labels, texts):
                    lbl.setText(txt or "Нет события")

            except Exception:
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

