import os
from notion_client import Client
from datetime import datetime
import csv
import sys
from dotenv import load_dotenv
load_dotenv()

notion = Client(auth=os.getenv('NOTION_API_SECRET'))
database_id = os.getenv('NOTION_DATABASE_ID')
goal_uuid = os.getenv('NOTION_GOAL_UUID')

date = None if 'START_DATE' not in os.environ else datetime.strptime(
    os.environ['START_DATE'], "%Y-%m-%d").isoformat()
# get date from cli
if len(sys.argv) > 1:
    date = sys.argv[1]

def get_pages(next_cursor=None):
    global date

    filters = [

        {
            "property": "Goal",
            "relation": {
                        "contains": goal_uuid
            }
        },
        {
            "property": "when",
            "date": {
                        "on_or_before": datetime.now().isoformat()
            }
        }
    ]

    if date:
        filters.append({
            "property": "when",
            "date": {
                "on_or_after": date
            }
        })

    response = notion.databases.query(
        database_id,
        start_cursor=next_cursor,
        filter={
            "and": filters
        }
    )
    pages = response['results']
    next_cursor = response.get('next_cursor')
    if next_cursor:
        pages += get_pages(next_cursor)
    return pages


def parse_pages(pages):
    parsed_pages = []
    for page in pages:
        title = page["properties"]["title"]["title"][0]["plain_text"]
        date = page["properties"]["when"]["date"]["start"]
        duration = float(page["properties"]["Duration"]
                         ["formula"]["string"].split(" ")[0].strip())

        # parsed date YYYY-MM-DD
        parsed_date = date.split("T")[0]

        parsed_page = {
            "title": title,
            "date": parsed_date,
            "duration": duration
        }
        parsed_pages.append(parsed_page)
    return parsed_pages


def group_by_date(pages):
    grouped_pages = {}
    for page in pages:
        if page["date"] in grouped_pages:
            oldGroup = grouped_pages[page["date"]]
            grouped_pages[page["date"]] = {
                "tasks": oldGroup["tasks"] + " - " + page["title"],
                "duration": oldGroup["duration"] + page["duration"]
            }
        else:
            grouped_pages[page["date"]] = {
                "tasks": page["title"],
                "duration": page["duration"]
            }
    return sorted(grouped_pages.items(), key=lambda x: x[0])


def export_to_csv(grouped_pages):
    with open('out.csv', mode='w') as csv_file:
        fieldnames = ['Date', 'Duration', 'Tasks']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()
        for date, group in grouped_pages:
            writer.writerow(
                {'Date': date, 'Duration': group['duration'], 'Tasks': group['tasks']})


print("getting pages")
pages = get_pages()
print("parsing pages")
parsed_pages = parse_pages(pages)
print("grouping pages")
grouped_pages = group_by_date(parsed_pages)
print("exporting to csv")
export_to_csv(grouped_pages)
print("CSV exported")
