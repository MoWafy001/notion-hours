from datetime import datetime


def get_pages(notion_client, database_id, date, next_cursor=None):
    filters = [
        {
            "property": "Tag",
            "rollup": {"any": {"select": {"equals": "Accounting Project"}}},
        },
        {
            "property": "Started At",
            "date": {"on_or_before": datetime.now().isoformat()},
        },
        {"property": "Ended At", "date": {"is_not_empty": True}},
    ]

    if date:
        filters.append({"property": "Started At", "date": {"on_or_after": date}})

    response = notion_client.databases.query(
        database_id, start_cursor=next_cursor, filter={"and": filters}
    )
    pages = response["results"]
    next_cursor = response.get("next_cursor")
    if next_cursor:
        pages += get_pages(notion_client, database_id, date, next_cursor)
    return pages
