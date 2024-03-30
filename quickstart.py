from datetime import datetime, timedelta
import os.path


from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pytz

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]


def get_calendar_service():
    """Log in to the Google Calendar API and return the service object."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("donnaClient.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    service = build("calendar", "v3", credentials=creds)
    return service


def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("donnaClient.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)

        # Call the Calendar API

        start_of_day = datetime.now()
        end_of_day = start_of_day + timedelta(days=1)
        print("Getting the upcoming 10 events")
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=start_of_day.isoformat() + "Z",
                timeMax=end_of_day.isoformat() + "Z",
                maxResults=10,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            print("No upcoming events found.")
            return

        # Prints the start and name of the next 10 events
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            print(start, event["summary"])

    except HttpError as error:
        print(f"An error occurred: {error}")


# def get_event(event_id):
#     """Retrieve an event by its ID from the user's primary calendar."""
#     try:
#         service = get_calendar_service()
#         event = service.events().get(calendarId="primary", eventId=event_id).execute()
#         print("Event found: %s" % (event.get("summary")))
#         return event
#     except HttpError as error:
#         print(f"An error occurred: {error}")
#         page_token = None
#         return None


def set_event(event_details):
    """Creates a new event with the given details."""
    try:
        service = get_calendar_service()
        event = (
            service.events().insert(calendarId="primary", body=event_details).execute()
        )
        print("Event created: %s" % (event.get("htmlLink")))
    except HttpError as error:
        print(f"An error occurred: {error}")


def get_events():
    """Retrieve the upcoming events of the current day from the user's primary calendar."""
    service = get_calendar_service()
    start_of_day = datetime.now()
    end_of_day = start_of_day + timedelta(days=1)
    print("Getting today's events...")
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=start_of_day.isoformat() + "Z",
            timeMax=end_of_day.isoformat() + "Z",
            maxResults=10,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])

    if not events:
        print("No upcoming events found.")
        return

    # Prints the start and name of today's events
    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        print(start, event["summary"])


def get_availability(date):
    """Check availability for a specific date and print free times."""
    try:
        # Define the whole day range
        service = get_calendar_service()
        datetime_format = "%Y-%m-%d"
        start_of_day = datetime.strptime(date, datetime_format)
        end_of_day = start_of_day + timedelta(days=1)

        # Prepare the request body for free/busy query
        body = {
            "timeMin": start_of_day.isoformat() + "Z",
            "timeMax": end_of_day.isoformat() + "Z",
            "items": [{"id": "primary"}],
        }

        # Query the free/busy info
        free_busy_result = service.freebusy().query(body=body).execute()
        busy_periods = free_busy_result.get("calendars").get("primary").get("busy")

        # Calculate and print the free times
        free_periods = calculate_free_periods(start_of_day, end_of_day, busy_periods)

        if not free_periods:
            print("Looks like the day is fully booked!")
        else:
            print("Free times:")
            for period in free_periods:
                print(f"{period[0]} to {period[1]}")
    except HttpError as error:
        print(f"An error occurred: {error}")


def convert_to_timezone(from_time, from_zone, to_zone):
    """
    Convert datetime from one timezone to another.

    :param from_time: The datetime to convert.
    :param from_zone: The timezone of the input datetime.
    :param to_zone: The timezone to convert the datetime to.
    :return: The converted datetime as a string in the format "Month day, Year Hour:Minute:Second AM/PM".
    """
    from_zone_tz = pytz.timezone(from_zone)
    to_zone_tz = pytz.timezone(to_zone)

    # Localize the datetime to the original timezone
    localized_datetime = from_zone_tz.localize(from_time)

    # Convert it to the new timezone
    target_time = localized_datetime.astimezone(to_zone_tz)

    # Format the datetime to the specified format
    return target_time.strftime("%B %d, %Y %I:%M:%S %p")


def calculate_free_periods(
    start_of_day, end_of_day, busy_periods, user_timezone="America/New_York"
):
    """Calculate free periods given the day's range and busy periods, and convert them to user's timezone."""
    free_periods = []

    # Convert start_of_day and end_of_day to the user's timezone and make them offset-aware
    user_tz = pytz.timezone(user_timezone)
    start_of_day = user_tz.localize(start_of_day)
    end_of_day = user_tz.localize(end_of_day)
    current_start = start_of_day

    for busy in busy_periods:
        busy_start_utc = datetime.fromisoformat(busy["start"].rstrip("Z")).replace(
            tzinfo=pytz.utc
        )
        busy_end_utc = datetime.fromisoformat(busy["end"].rstrip("Z")).replace(
            tzinfo=pytz.utc
        )

        busy_start_user_tz = busy_start_utc.astimezone(user_tz)
        busy_end_user_tz = busy_end_utc.astimezone(user_tz)

        if current_start < busy_start_user_tz:
            currStart = current_start.strftime("%B %d, %Y %I:%M:%S %p")
            busyStart = busy_start_user_tz.strftime("%B %d, %Y %I:%M:%S %p")
            free_periods.append((currStart, busyStart))
        current_start = max(current_start, busy_end_user_tz)

    if current_start < end_of_day:
        currStart = current_start.strftime("%B %d, %Y %I:%M:%S %p")
        end = end_of_day.strftime("%B %d, %Y %I:%M:%S %p")
        free_periods.append((currStart, end))

    return free_periods


if __name__ == "__main__":
    # get_events()
    # set_event(
    #     {
    #         "summary": "Test event",
    #         "location": "Test location",
    #         "description": "Test description",
    #         "start": {
    #             "dateTime": "2024-03-16T09:00:00",
    #             "timeZone": "Europe/Bucharest",
    #         },
    #         "end": {"dateTime": "2024-03-16T17:00:00", "timeZone": "Europe/Bucharest"},
    #     }
    # )
    get_availability("2024-3-16")
