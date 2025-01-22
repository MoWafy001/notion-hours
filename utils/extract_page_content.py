ACCEPTABLE_BLOCK_TYPES = [
    "paragraph",
    "heading_1",
    "heading_2",
    "heading_3",
    "bulleted_list_item",
    "numbered_list_item",
    "to_do",
    "toggle",
]

DEFAULT_FONT_SIZE = 10
HEADINGS_FONT_SIZE_MAP = {
    "heading_1": 13,
    "heading_2": 12,
    "heading_3": 11,
}


def extract_page_content(notion_client, page_id):
    blocks = []
    next_cursor = None
    while True:
        response = notion_client.blocks.children.list(
            block_id=page_id, start_cursor=next_cursor
        )
        blocks.extend(response.get("results", []))
        next_cursor = response.get("next_cursor")
        if not next_cursor:
            break

    content = []
    for block in blocks:
        # Skip unsupported block types
        block_type = block["type"]
        if block_type not in ACCEPTABLE_BLOCK_TYPES:
            continue

        # Skip empty blocks
        rich_text = block[block_type]["rich_text"]
        if type(rich_text) is list:
            if len(rich_text) == 0:
                continue
        else:
            rich_text = [rich_text]

        # if to-do, the first rich_text to include the checked status
        if block_type == "to_do":
            is_checked = block[block_type]["checked"]
            rich_text[0]["plain_text"] = (
                "☑ " if is_checked else "☐ "
            ) + rich_text[0]["plain_text"]

        # if bulleted_list_item, the first rich_text to include the bullet
        if block_type == "bulleted_list_item":
            rich_text[0]["plain_text"] = "• " + rich_text[0]["plain_text"]

        # if numbered_list_item, the first rich_text to include the number
        if block_type == "numbered_list_item":
            rich_text[0]["plain_text"] = (
                f"{block[block_type]['number']}. " + rich_text[0]["plain_text"]
            )

        plain_text = "".join([text["plain_text"] for text in rich_text])
        segments = []
        for segment in rich_text:
            annotation = segment.get("annotations", {})
            href = segment.get("href", None)
            is_heading = block_type.startswith("heading")
            segments.append(
                {
                    "plain_text": segment["plain_text"],
                    "textFormat": {
                        "bold": is_heading or annotation.get("bold", False),
                        "italic": annotation.get("italic", False),
                        "underline": annotation.get("underline", False),
                        "strikethrough": annotation.get("strikethrough", False),
                        "fontSize": HEADINGS_FONT_SIZE_MAP.get(
                            block_type, DEFAULT_FONT_SIZE
                        ),
                        "link": (
                            {
                                "url": href,
                            }
                            if href
                            else None
                        ),
                    },
                    "hyperlinkDisplayType": "LINKED" if href else "PLAIN_TEXT",
                }
            )

        data = {  # Google CellFormat
            "type": block_type,
            "plain_text": plain_text,
            "segments": segments,
        }
        content.append(data)

    return content
