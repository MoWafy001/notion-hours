from datetime import datetime


def group_pages_by_date(pages):
    grouped_pages = {}
    for page in pages:
        if page["date"] in grouped_pages:
            oldGroup = grouped_pages[page["date"]]
            grouped_pages[page["date"]] = {
                "tasks": [*oldGroup["tasks"], *page["details"]],
                "duration": oldGroup["duration"] + page["duration"],
            }
        else:
            grouped_pages[page["date"]] = {
                "tasks": page["details"],
                "duration": page["duration"],
            }

    # remove duplicate task names
    for date, group in grouped_pages.items():
        tasks = group["tasks"]
        test_tasks = list(filter(lambda x: "test" in x["plain_text"].lower(), tasks))
        tasks = list(filter(lambda x: "test" not in x["plain_text"].lower(), tasks))
        grouped_pages[date] = {
            "tasks": tasks,
            "test_tasks": test_tasks,
            "duration": group["duration"],
        }

    # convert from dict to list
    groups = []
    for date, group in grouped_pages.items():
        groups.append(
            {
                "date": date,
                "duration": group["duration"],
                "tasks": group["tasks"],
                "test_tasks": group["test_tasks"],
            }
        )

    # sort by date
    groups = sorted(groups, key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d"))
    return groups
