import os
from notion_client import Client
import gspread
from datetime import datetime
import sys
from dotenv import load_dotenv
from utils import parse_pages, get_pages, group_pages_by_date, update_timesheet
import re


if __name__ == "__main__":
    # variables
    load_dotenv(override=True)
    NOTION_API_SECRET = os.getenv("NOTION_API_SECRET")
    NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
    SHEET_NAME = "Timesheet - Wafy"
    START_DATE = os.getenv("START_DATE")

    # initialize the clients
    notion = Client(auth=NOTION_API_SECRET)
    gc = gspread.oauth()
    sh = gc.open(SHEET_NAME).sheet1

    # getting the last row in the sheet
    exp = re.compile(r"\d{4}-\d{2}-\d{2}")
    last_cell = sh.findall(exp, in_column=1)[-1]

    # get default date
    date = None
    if last_cell:
        date = last_cell.value
    elif len(sys.argv) > 1:
        date = sys.argv[1]
    else:
        date = START_DATE
    date = datetime.strptime(date, "%Y-%m-%d").isoformat()

    # get pages and update timesheet
    pages = get_pages(notion, NOTION_DATABASE_ID, date)
    parsed_pages = parse_pages(notion, pages)
    grouped_pages = group_pages_by_date(parsed_pages)
    update_timesheet(sh, grouped_pages)
