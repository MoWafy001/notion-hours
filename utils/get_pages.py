from datetime import datetime


def get_pages(notion_client, database_id, project_id, date, next_cursor=None):
    print("Getting pages...", project_id, date)
    filters = [
        {
            "property": "Project",
            "rollup": {"any": {
                "relation": {
                    "contains": project_id,
                },
            }},
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
        pages += get_pages(notion_client, database_id, project_id, date, next_cursor)
        
    return pages
