from datetime import datetime
from records import Record


class Host(dict):
    def __init__(self, record: Record):
        self.id: str = record["uid"]
        self.handle: str = record["handle"]
        self.date: datetime = datetime(
            record["date"].year, record["date"].month, record["date"].day
        )

        # Make the class JSON serializable
        super().__init__(self.__dict__)
