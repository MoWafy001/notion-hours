import os
from notion_client import Client
from datetime import datetime
import csv
import sys
from dotenv import load_dotenv

load_dotenv(override=True)


def get_data(start_date):
    notion = Client(auth=os.getenv("NOTION_API_SECRET"))
    database_id = os.getenv("NOTION_DATABASE_ID")

    date = (
        None
        if "START_DATE" not in os.environ
        else datetime.strptime(os.getenv("START_DATE"), "%Y-%m-%d").isoformat()
    )
# get date from cli
    if len(sys.argv) > 1:
        date = sys.argv[1]
        date = datetime.strptime(date, "%Y-%m-%d").isoformat()

    date = start_date if start_date else date

    def get_pages(next_cursor=None):
        filters = [
            {
                "property": "Tags",
                "rollup": {"any": {"multi_select": {"contains": "Accounting Project"}}},
            },
            {
                "property": "Started At",
                "date": {"on_or_before": datetime.now().isoformat()},
            },
            {"property": "Ended At", "date": {"is_not_empty": True}},
        ]

        if date:
            filters.append({"property": "Started At", "date": {"on_or_after": date}})

        response = notion.databases.query(
            database_id, start_cursor=next_cursor, filter={"and": filters}
        )
        pages = response["results"]
        next_cursor = response.get("next_cursor")
        if next_cursor:
            pages += get_pages(next_cursor)
        return pages

    def parse_pages(pages):
        parsed_pages = []
        for page in pages:
            descriptionArray = page["properties"]["Description"]["title"]
            if len(descriptionArray) == 0:
                title = ""
            else:
                title = page["properties"]["Description"]["title"][-1]["plain_text"]
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

            parsed_page = {"title": title, "date": parsed_date, "duration": duration}
            parsed_pages.append(parsed_page)
        return parsed_pages


    def group_by_date(pages):
        grouped_pages = {}
        for page in pages:
            if page["date"] in grouped_pages:
                oldGroup = grouped_pages[page["date"]]
                grouped_pages[page["date"]] = {
                    "tasks": oldGroup["tasks"] + " - " + page["title"],
                    "duration": oldGroup["duration"] + page["duration"],
                }
            else:
                grouped_pages[page["date"]] = {
                    "tasks": page["title"],
                    "duration": page["duration"],
                }

        # remove duplicate task names
        for date, group in grouped_pages.items():
            tasks = group["tasks"].replace(" | ", " - ").split(" - ")
            tasks = list(filter(lambda x: x.strip() != "", tasks))
            test_tasks = list(
                filter(lambda x: "test" in x.lower().strip(), tasks)
            )
            tasks = list(
                filter(lambda x: "test" not in x.lower().strip(), tasks)
            )
            tasks = list(set(tasks))
            grouped_pages[date] = {
                "tasks": " - ".join(tasks),
                "test_tasks": " - ".join(test_tasks),
                "duration": group["duration"],
            }

        return sorted(grouped_pages.items(), key=lambda x: x[0])


    def export_to_csv(grouped_pages):
        with open("out.csv", mode="w") as csv_file:
            fieldnames = ["Date", "Duration", "Tasks", "Test Tasks"]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            writer.writeheader()
            for date, group in grouped_pages:
                writer.writerow(
                    {
                        "Date": date,
                        "Duration": group["duration"],
                        "Tasks": group["tasks"],
                        "Test Tasks": group["test_tasks"],
                    }
                )


    print("getting pages")
    pages = get_pages()
    print("parsing pages")
    parsed_pages = parse_pages(pages)
    print("grouping pages")
    grouped_pages = group_by_date(parsed_pages)
    print("exporting to csv")
    export_to_csv(grouped_pages)
    print("CSV exported")


if __name__ == "__main__":
    get_data(None)
