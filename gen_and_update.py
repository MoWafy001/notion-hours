import gspread
import re
from script import get_data
from update_timesheet import update_timesheet

gc = gspread.oauth()
sh = gc.open("Timesheet - Wafy").sheet1

# last cell with date at column A
exp = re.compile(r"\d{4}-\d{2}-\d{2}")
last_cell = sh.findall(exp, in_column=1)[-1]
start_date = last_cell.value

get_data(start_date)
update_timesheet(gc)
