from gspread_formatting import batch_updater, TextFormatRun, TextFormat, set_text_format_runs
from pprint import pprint
from utils.extract_page_content import DataBlock
from utils.group_pages_by_date import DayDetails


def update_timesheet(sh, days: list[DayDetails]):
    days_start_date = days[0].date if days else None
    col_dates = sh.col_values(1)
    last_sheet_date = col_dates[-1]

    if days_start_date == last_sheet_date:
        days = days[1:]
        if not days:
            print("No new data to update")
            return
    start_row = len(col_dates) + 1

    def get_text_format_runs(blocks: list[DataBlock]):
        text_format_runs = []
        total_length = sum([len(segment["plain_text"]) for block in blocks for segment in block.segments])
        total_length += len(blocks) - 1

        start_index = 0
        for block in blocks:
            for segIndex, segment in enumerate(block.segments):
                if(start_index > total_length-1):
                    break

                format_run = TextFormatRun(
                    startIndex=start_index,
                    format=TextFormat(
                        **segment["textFormat"],
                    ),
                )
                text_format_runs.append(format_run)
                start_index += len(segment["plain_text"])
            start_index += 1  # for the newline character

        return text_format_runs

    plain_rows = []
    for day in days:
        plain_tasks = "\n".join(list(map(lambda x: x.plain_text, day.tasks)))
        plain_tests = "\n".join(
            list(map(lambda x: x.plain_text, day.test_tasks))
        )
        plain_rows.append(
            [
                day.date,
                day.duration,
                plain_tasks,
                plain_tests,
            ]
        )

    sh.update(plain_rows, f"A{start_row}:D{start_row + len(plain_rows) - 1}", raw=False)

    for index, day in enumerate(days):
        if day.tasks:
            set_text_format_runs(
                sh,
                f"C{start_row + index}",
                get_text_format_runs(day.tasks),
            )
        if day.test_tasks:
            set_text_format_runs(
                sh,
                f"D{start_row + index}",
                get_text_format_runs(day.test_tasks),
            )

    print(f"Updated to row A{start_row}:D{start_row + len(plain_rows) - 1}")
