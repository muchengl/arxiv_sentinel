import math

from ics import Calendar, Event
from datetime import datetime

def estimate_reading_time(text):
    """
    Estimate the reading time based on the number of characters in the text.
    Assumes an average reading speed of 200 words per minute and 5 characters per word.
    """
    words = len(text) / 5
    reading_time_minutes = words / 200
    return math.ceil(reading_time_minutes)

def create_ics_file(event_name, start_time, end_time, description="", location="", file_name="event.ics"):
    """
    Creates an .ics file with a single event.

    Parameters:
        event_name (str): The name or title of the event.
        start_time (datetime): The starting time of the event (as a datetime object).
        end_time (datetime): The ending time of the event (as a datetime object).
        description (str, optional): A description of the event. Default is an empty string.
        location (str, optional): The location where the event will take place. Default is an empty string.
        file_name (str, optional): The name of the .ics file to be created. Default is "event.ics".

    Returns:
        None
    """
    # Create a calendar instance
    calendar = Calendar()

    # Create an event instance and set properties
    event = Event()
    event.name = event_name
    event.begin = start_time
    event.end = end_time
    event.description = description
    event.location = location

    # Add the event to the calendar
    calendar.events.add(event)

    # Write the calendar to a .ics file
    with open(file_name, 'w', encoding='utf-8') as f:
        f.writelines(calendar)

    print(f"ICS file '{file_name}' created successfully.")

# Example usage
# if __name__ == "__main__":
#     # Define event details
#     event_name = "Team Meeting"
#     start_time = datetime(2024, 11, 5, 14, 0)  # 2:00 PM on Nov 5, 2024
#     end_time = datetime(2024, 11, 5, 15, 0)    # 3:00 PM on Nov 5, 2024
#     description = "Discussing project milestones and deadlines."
#     location = "Conference Room 101"
#
#     # Create an .ics file
#     create_ics_file(event_name, start_time, end_time, description, location, "team_meeting.ics")
