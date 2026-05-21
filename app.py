import datetime
import json
import os
from openai import OpenAI
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

def get_calendar_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)

def parse_multiple_events_with_ai(user_text):
    """Asks LM Studio to extract ONE or MORE events into a list of JSON items."""
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    system_prompt = (
        f"You are a scheduling assistant. Extract all events from the user's text. "
        f"Today's date and time is {current_time}. "
        f"The user might mention one event or multiple events. "
        f"Respond ONLY with a raw JSON array of objects (even if there is only 1 event). "
        f"Each object must contain keys: 'summary', 'start_time', and 'end_time'. "
        f"Use 'YYYY-MM-DDTHH:MM:SS' format for dates. If no end time is mentioned, set it 1 hour after start time.\n\n"
        f"Example output format:\n"
        f"[{{\"summary\": \"Event 1\", \"start_time\": \"2026-05-22T14:00:00\", \"end_time\": \"2026-05-22T15:00:00\"}}]"
    )
    
    print("\n🤖 Chat2Cal is processing your text locally...")
    
    try:
        completion = client.chat.completions.create(
            model="local-model",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text}
            ],
            temperature=0.1
        )
        
        raw_response = completion.choices[0].message.content.strip()
        if raw_response.startswith("```json"):
            raw_response = raw_response.replace("```json", "").replace("```", "").strip()
            
        return json.loads(raw_response)
    except Exception as e:
        print(f"❌ Failed to parse data. Ensure LM Studio outputs a valid JSON array. Error: {e}")
        return []

def create_calendar_event(event_data):
    """Pushes a single event to Google Calendar."""
    try:
        service = get_calendar_service()
        event = {
            'summary': event_data['summary'],
            'start': {'dateTime': event_data['start_time'], 'timeZone': 'UTC'},
            'end': {'dateTime': event_data['end_time'], 'timeZone': 'UTC'},
        }
        event = service.events().insert(calendarId='primary', body=event).execute()
        print(f"🎉 Created: '{event_data['summary']}' -> {event_data['start_time']}")
    except Exception as e:
        print(f"❌ Failed to create event '{event_data.get('summary')}': {e}")

def delete_upcoming_events():
    """Fetches upcoming events and lets you select one to delete."""
    try:
        service = get_calendar_service()
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        
        print("\nRetrieving your next 10 events...")
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print("No upcoming events found.")
            return

        print("\n--- Upcoming Events ---")
        for i, event in enumerate(events, start=1):
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(f"[{i}] {event['summary']} ({start})")
            
        choice = input("\nEnter the number of the event to delete (or press Enter to cancel): ")
        if choice.isdigit() and 1 <= int(choice) <= len(events):
            event_to_delete = events[int(choice) - 1]
            service.events().delete(calendarId='primary', eventId=event_to_delete['id']).execute()
            print(f"🗑️ Successfully deleted: '{event_to_delete['summary']}'")
        else:
            print("Deletion canceled.")
    except Exception as e:
        print(f"❌ Error during deletion: {e}")

# Main Interface Loop
if __name__ == '__main__':
    print("=========================================")
    print("       Chat2Cal App Initialized          ")
    print("=========================================")
    print("Commands: 'delete' to remove events | 'exit' to quit\n")
    
    while True:
        user_input = input("Enter calendar details or command: ").strip()
        
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break
        elif user_input.lower() == 'delete':
            delete_upcoming_events()
            print("\n-----------------------------------------")
            continue
            
        if not user_input:
            continue
            
        # AI splits and handles multiple items inside the sentence
        events_list = parse_multiple_events_with_ai(user_input)
        
        if isinstance(events_list, list) and len(events_list) > 0:
            print(f"📍 Found {len(events_list)} separate event(s). Uploading...")
            for event_data in events_list:
                create_calendar_event(event_data)
        else:
            print("❌ No events could be safely extracted. Check your prompt or model settings.")
            
        print("\n-----------------------------------------")