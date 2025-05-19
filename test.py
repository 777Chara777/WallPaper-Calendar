import datetime
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)


service = build("calendar", "v3", credentials=creds)

# Call the Calendar API
now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
print("Getting the upcoming 10 events")
events_result = (
    service.events()
    .list(
        calendarId="primary",
        timeMin=now,
        maxResults=10,
        singleEvents=True,
        orderBy="startTime",
    ).execute()
)
events = events_result.get("items", [])


# Prints the start and name of the next 10 events
for event in events:
    start = event["start"].get("dateTime", event["start"].get("date"))
    print(start, event["summary"])