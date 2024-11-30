import gspread
import csv
import datetime
import re


def update_timesheet(_gc):
    # read the csv file
    rows = []
    with open("out.csv") as f:
        reader = csv.reader(f)
        for row in reader:
            rows.append(row)
    rows = rows[1:]

    def formatRow(row):
        # date
        row[0] = datetime.datetime.strptime(row[0], "%Y-%m-%d").strftime("%Y-%m-%d")

        # number
        row[1] = float(row[1])
        return row

    rows = list(map(formatRow, rows))
    gc = gspread.oauth() if not _gc else _gc

    # Open a sheet from a spreadsheet in one go
    sh = gc.open("Timesheet - Wafy").sheet1

    # first date in csv
    csv_start_date = rows[0][0]
    col_dates = sh.col_values(1)
    last_sheet_date = col_dates[-1]

    if csv_start_date == last_sheet_date:
        start_row = len(col_dates)
        rows = rows[1:]
    else:
        start_row = len(col_dates) + 1

    print("rows:", rows)
    print(rows[0])
    print(rows[0][0])

    # update the sheet
    sh.update(rows, f"A{start_row}:D{start_row + len(rows) - 1}", raw=False)
    print(f"Updated to row A{start_row}:D{start_row + len(rows) - 1}")


if __name__ == "__main__":
    update_timesheet(None)
