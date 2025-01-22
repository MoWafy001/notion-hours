from gspread_formatting import batch_updater, TextFormatRun, TextFormat, set_text_format_runs
from pprint import pprint


def update_timesheet(sh, groups: list):
    groups_start_date = groups[0]["date"] if groups else None
    col_dates = sh.col_values(1)
    last_sheet_date = col_dates[-1]

    if groups_start_date == last_sheet_date:
        groups = groups[1:]
        if not groups:
            print("No new data to update")
            return
    start_row = len(col_dates) + 1

    def get_text_format_runs(tasks):
        text_format_runs = []

        start_index = 0
        for task in tasks:
            for segIndex, segment in enumerate(task["segments"]):
                format_run = TextFormatRun(
                    startIndex=start_index,
                    format=TextFormat(
                        **segment["textFormat"],
                    ),
                )
                text_format_runs.append(format_run)
                start_index += len(segment["plain_text"]) + 1

        return text_format_runs

    plain_rows = []
    for group in groups:
        plain_tasks = "\n".join(list(map(lambda x: x["plain_text"], group["tasks"])))
        plain_tests = "\n".join(
            list(map(lambda x: x["plain_text"], group["test_tasks"]))
        )
        plain_rows.append(
            [
                group["date"],
                group["duration"],
                plain_tasks,
                plain_tests,
            ]
        )

    sh.update(plain_rows, f"A{start_row}:D{start_row + len(plain_rows) - 1}", raw=False)

    for index, group in enumerate(groups):
        if group["tasks"]:
            set_text_format_runs(
                sh,
                f"C{start_row + index}",
                get_text_format_runs(group["tasks"]),
            )
        if group["test_tasks"]:
            set_text_format_runs(
                sh,
                f"D{start_row + index}",
                get_text_format_runs(group["test_tasks"]),
            )

    print(f"Updated to row A{start_row}:D{start_row + len(plain_rows) - 1}")
