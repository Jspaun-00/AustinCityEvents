from datetime import datetime, timedelta
import os.path
import sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def format_for_google_calendar(event_data):
    """
    Formats a scraped event dictionary into a Google Calendar API event resource.

    Args:
        event_data (dict): A dictionary containing the scraped event info.
                           Expected keys: 'title', 'start_time', 'end_time',
                           'location', 'description', 'source'.

    Returns:
        dict: A dictionary formatted for the Google Calendar API.
    """
    # The start_time and end_time from our scraper are already timezone-aware
    # We just need to format them into the structure Google Calendar expects.
    
    # The description will be a combination of the event's description and a link back to the source.
    full_description = (
        f"{event_data.get('description', 'No description provided.')}\n\n"
        f"Source: {event_data.get('source', 'No source URL available.')}"
    )

    google_event = {
        'summary': event_data['title'],
        'location': event_data.get('location', ''),
        'description': full_description,
        'start': {
            'dateTime': event_data['start_time'].isoformat(),
            'timeZone': str(event_data['start_time'].tzinfo),
        },
        'end': {
            'dateTime': event_data['end_time'].isoformat(),
            'timeZone': str(event_data['end_time'].tzinfo),
        },
    }
    return google_event

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    """
    Authenticates with the Google Calendar API and returns a service object.
    Handles the OAuth 2.0 flow and token storage.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    token_path = resource_path('token.json')
    credentials_path = resource_path('credentials.json')

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # This will use your credentials.json to open a browser window for you to
            # authorize the script.
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)
        print("Successfully connected to Google Calendar API.")
        return service
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None

def check_if_event_exists(service, calendar_id, event_summary, start_time):
    """Checks if an event with a similar title and start time already exists."""
    print(f"Checking for existing event: '{event_summary}'")
    # Search a 2-minute window around the start time to account for minor discrepancies.
    time_min = (start_time - timedelta(minutes=1)).isoformat()
    time_max = (start_time + timedelta(minutes=1)).isoformat()

    try:
        events_result = service.events().list(
            calendarId=calendar_id,
            q=event_summary,
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        existing_events = events_result.get('items', [])
        return len(existing_events) > 0
    except HttpError as error:
        print(f"An error occurred while checking for events: {error}")
        return False # Assume it doesn't exist to avoid halting on a check error

def add_event_to_calendar(service, calendar_id, event_body):
    """Adds a single event to the specified Google Calendar."""
    try:
        event = service.events().insert(calendarId=calendar_id, body=event_body).execute()
        print(f"  -> Event created: {event.get('htmlLink')}")
        return True
    except HttpError as error:
        print(f"An error occurred while creating event: {error}")
        return False

if __name__ == '__main__':
    print("--- Testing Google Calendar API Connection ---")
    # This will test your connection to the Google Calendar API.
    # The first time you run this, it will open a browser for you to log in.
    get_calendar_service()