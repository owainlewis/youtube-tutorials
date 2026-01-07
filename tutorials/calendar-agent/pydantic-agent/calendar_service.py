"""Google Calendar API service."""

from datetime import datetime, timedelta
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from pydantic import BaseModel

SCOPES = ["https://www.googleapis.com/auth/calendar"]


class Event(BaseModel):
    id: str
    title: str
    start: str
    end: str


class CalendarService:
    """Google Calendar API wrapper with OAuth authentication."""

    def __init__(
        self,
        credentials_path: str = "credentials.json",
        token_path: str = "token.json",
    ):
        self.credentials_path = Path(credentials_path)
        self.token_path = Path(token_path)
        self.service = self._authenticate()

    def _authenticate(self):
        creds = None

        if self.token_path.exists():
            creds = Credentials.from_authorized_user_file(str(self.token_path), SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not self.credentials_path.exists():
                    raise FileNotFoundError(
                        f"credentials.json not found. Download from Google Cloud Console."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path), SCOPES
                )
                creds = flow.run_local_server(port=0)

            self.token_path.write_text(creds.to_json())

        return build("calendar", "v3", credentials=creds)

    def list_events(self, date: str) -> list[Event]:
        """List all events for a date (YYYY-MM-DD)."""
        start = datetime.fromisoformat(date)
        end = start + timedelta(days=1)

        result = (
            self.service.events()
            .list(
                calendarId="primary",
                timeMin=start.isoformat() + "Z",
                timeMax=end.isoformat() + "Z",
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        events = []
        for item in result.get("items", []):
            events.append(
                Event(
                    id=item["id"],
                    title=item.get("summary", "No title"),
                    start=item["start"].get("dateTime", item["start"].get("date")),
                    end=item["end"].get("dateTime", item["end"].get("date")),
                )
            )
        return events

    def create_event(
        self,
        title: str,
        date: str,
        start_time: str,
        duration_minutes: int = 30,
    ) -> Event:
        """Create a new event."""
        start_dt = datetime.fromisoformat(f"{date}T{start_time}:00")
        end_dt = start_dt + timedelta(minutes=duration_minutes)

        body = {
            "summary": title,
            "start": {"dateTime": start_dt.isoformat(), "timeZone": "UTC"},
            "end": {"dateTime": end_dt.isoformat(), "timeZone": "UTC"},
        }

        result = self.service.events().insert(calendarId="primary", body=body).execute()

        return Event(
            id=result["id"],
            title=result.get("summary", title),
            start=result["start"]["dateTime"],
            end=result["end"]["dateTime"],
        )

    def update_event(
        self,
        event_id: str,
        title: str | None = None,
        date: str | None = None,
        start_time: str | None = None,
        duration_minutes: int | None = None,
    ) -> Event:
        """Update an existing event."""
        existing = (
            self.service.events().get(calendarId="primary", eventId=event_id).execute()
        )

        if title:
            existing["summary"] = title

        if date or start_time or duration_minutes:
            current_start = datetime.fromisoformat(
                existing["start"]["dateTime"].replace("Z", "")
            )
            current_end = datetime.fromisoformat(
                existing["end"]["dateTime"].replace("Z", "")
            )
            current_duration = int((current_end - current_start).total_seconds() / 60)

            new_date = date or current_start.strftime("%Y-%m-%d")
            new_time = start_time or current_start.strftime("%H:%M")
            new_duration = duration_minutes or current_duration

            new_start = datetime.fromisoformat(f"{new_date}T{new_time}:00")
            new_end = new_start + timedelta(minutes=new_duration)

            existing["start"]["dateTime"] = new_start.isoformat()
            existing["end"]["dateTime"] = new_end.isoformat()

        result = (
            self.service.events()
            .update(calendarId="primary", eventId=event_id, body=existing)
            .execute()
        )

        return Event(
            id=result["id"],
            title=result.get("summary", "No title"),
            start=result["start"]["dateTime"],
            end=result["end"]["dateTime"],
        )

    def delete_event(self, event_id: str) -> None:
        """Delete an event."""
        self.service.events().delete(calendarId="primary", eventId=event_id).execute()
