from utils import extract_page_content
from datetime import datetime


def parse_pages(notion_client, pages):
    parsed_pages = []
    for page in pages:
        details = extract_page_content(notion_client, page["id"])
        date = page["properties"]["Started At"]["date"]["start"]
        date_end = page["properties"]["Ended At"]["date"]["start"]

        # parsed date 2024-05-18T17:08:00.000+03:00 2024-05-18T20:08:00.000+03:00
        parsed_date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%f%z").strftime(
            "%Y-%m-%d"
        )
        duration = round(
            (
                datetime.strptime(date_end, "%Y-%m-%dT%H:%M:%S.%f%z")
                - datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%f%z")
            ).total_seconds()
            / 3600,
            2,
        )

        parsed_page = {"details": details, "date": parsed_date, "duration": duration}
        parsed_pages.append(parsed_page)
    return parsed_pages
