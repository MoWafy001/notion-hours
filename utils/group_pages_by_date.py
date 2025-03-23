from datetime import datetime
from utils.extract_page_content import DataBlock
from utils.parse_page import ParsedPage

class DayDetails:
    def __init__(self, date: str, duration: int, details: list[DataBlock], continuation_hours=0):
        self.date = date
        self.duration = duration
        self.details = details
        self.continuation_hours = continuation_hours
        self.tasks = []
        self.test_tasks = []

        if continuation_hours > 0:
            self.__prepend_continuation_hours()

        self.__get_tasks_and_test_tasks()

    def __prepend_continuation_hours(self): 
        newBlock = DataBlock(
            type="paragraph",
            plain_text=f"Continuation from previous day: {self.continuation_hours} hours",
            segments=[{"plain_text": f"Continuation from previous day: {self.continuation_hours} hours"}]
        )
        self.details.insert(0, newBlock)

    def __get_tasks_and_test_tasks(self):
        # if heading, add all below until empty line, or higher or equal heading
        current_is_test = False
        current_header_number = 4
        header_number_map = {
            "heading_1": 1,
            "heading_2": 2,
            "heading_3": 3
        }

        for block in self.details:
            header_number = header_number_map.get(block.type, 4)
            if header_number <= current_header_number or block.plain_text == "":
                current_is_test = "test" in block.plain_text.lower()
                current_header_number = header_number

            if current_is_test:
                self.test_tasks.append(block)
            else:
                self.tasks.append(block)

def group_sessions_by_date(sessions: list[ParsedPage]) -> list[DayDetails]:
    grouped_pages: dict[str, DayDetails] = {}
    for session in sessions:
        if session.date in grouped_pages:
            oldGroup = grouped_pages[session.date]
            grouped_pages[session.date] = DayDetails(
                date=session.date,
                duration=oldGroup.duration + session.duration,
                details=[*oldGroup.details, *session.details],
                continuation_hours=oldGroup.continuation_hours + (session.duration if session.is_continuation else 0)
            )
        else:
            grouped_pages[session.date] = DayDetails(
                date=session.date,
                duration=session.duration,
                details=session.details,
                continuation_hours = session.duration if session.is_continuation else 0
            )

    # convert from dict to list
    days = list(grouped_pages.values())

    # sort by date
    days = sorted(days, key=lambda x: datetime.strptime(x.date, "%Y-%m-%d"))
    return days
