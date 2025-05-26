# import datetime
# import os

# from google.auth.transport.requests import Request
# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
# from googleapiclient.discovery import build
# from googleapiclient.errors import HttpError

# # SCOPES = ["https://www.googleapis.com/auth/calendar.events"]
# # SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
# SCOPES = ["https://www.googleapis.com/auth/calendar.readonly", "https://www.googleapis.com/auth/tasks.readonly"]

# if os.path.exists("token.json"):
#     creds = Credentials.from_authorized_user_file("token.json", SCOPES)


# service_calendar = build("calendar", "v3", credentials=creds)
# service_tasks = build("tasks", "v1", credentials=creds)

# # Call the Calendar API
# now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
# print("Getting the upcoming 10 events")
# events_result = (
#     service_tasks.events()
#     .list(
#         calendarId="primary",
#         timeMin=now,
#         maxResults=10,
#         singleEvents=True,
#         orderBy="startTime",
#     ).execute()
# )
# events = events_result.get("items", [])


# # Prints the start and name of the next 10 events
# for event in events:
#     start = event["start"].get("dateTime", event["start"].get("date"))
#     print(start, event["summary"])

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import datetime
import os

SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/tasks.readonly"
]

if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)

# Инициализация API
service_calendar = build("calendar", "v3", credentials=creds)
service_tasks = build("tasks", "v1", credentials=creds)

now = datetime.datetime.utcnow().isoformat() + 'Z'  # Время в ISO формате

# Получаем события из календаря
events_result = service_calendar.events().list(
    calendarId='primary',
    timeMin=now,
    maxResults=10,
    singleEvents=True,
    orderBy='startTime'
).execute()
calendar_events = events_result.get("items", [])

# Преобразуем события в общий формат
merged_items = []
for event in calendar_events:
    start = event["start"].get("dateTime", event["start"].get("date"))
    merged_items.append({
        "title": event.get("summary", "Без названия"),
        "datetime": start,
        "type": "event"
    })

# Получаем задачи из всех списков
tasklists = service_tasks.tasklists().list(maxResults=10).execute().get("items", [])
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

print(merged_items)

# Вывод
for item in merged_items:
    print(f"[{item['type'].upper()}] {item['datetime']} - {item['title']}")
