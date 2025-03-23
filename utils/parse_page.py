from utils import extract_page_content
from utils.extract_page_content import DataBlock
from datetime import datetime, timedelta

class ParsedPage:
    def __init__(self, details: list[DataBlock], date: str, duration: float, is_continuation=False):
        self.details = details
        self.date = date
        self.duration = duration
        self.is_continuation = is_continuation

    def __repr__(self):
        return f"ParsedPage(details={self.details}, date={self.date}, duration={self.duration}, is_continuation={self.is_continuation})"

def parse_sessions_pages(notion_client, pages, dayEndHour=0) -> list[ParsedPage]:
    parsed_pages: list[ParsedPage] = []
    for page in pages:
        details = extract_page_content(notion_client, page["id"])
        date = page["properties"]["Started At"]["date"]["start"]
        date_end = page["properties"]["Ended At"]["date"]["start"]

        # Parse the start and end times
        start_datetime = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%f%z")
        end_datetime = datetime.strptime(date_end, "%Y-%m-%dT%H:%M:%S.%f%z")

        # Calculate the day boundary based on dayEndHour
        day_boundary = start_datetime.replace(hour=dayEndHour, minute=0, second=0, microsecond=0)
        if start_datetime > day_boundary:
            day_boundary += timedelta(days=1)

        # Check if the session spans across the day boundary
        if end_datetime > day_boundary:
            # Split the session into two parts
            duration_before_boundary = round((day_boundary - start_datetime).total_seconds() / 3600, 2)
            duration_after_boundary = round((end_datetime - day_boundary).total_seconds() / 3600, 2)

            # Add the first part of the session
            parsed_pages.append(ParsedPage(
                details,
                start_datetime.strftime("%Y-%m-%d"),
                duration_before_boundary
            ))

            # Add the second part of the session
            parsed_pages.append(ParsedPage(
                "",
                day_boundary.strftime("%Y-%m-%d"),
                duration_after_boundary,
                is_continuation=True
            ))
        else:
            # If the session does not span the boundary, add it as a single record
            duration = round((end_datetime - start_datetime).total_seconds() / 3600, 2)
            parsed_pages.append(ParsedPage(
                details,
                start_datetime.strftime("%Y-%m-%d"),
                duration
            ))

    return parsed_pages
