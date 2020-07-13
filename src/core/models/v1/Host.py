from datetime import datetime
from records import Record


class Host(dict):
    def __init__(self, record: Record):
        self.id: str = record["uid"]
        self.handle: str = record["handle"]
        self.date: datetime = datetime(
            record["date"].year, record["date"].month, record["date"].day
        )
        self.url: str = str(self)

        # Make the class JSON serializable
        super().__init__(self.__dict__)

    def __str__(self):
        return self.make_url(self.handle)

    @staticmethod
    def make_url(writer_handle: str) -> str:
        return f"https://twitter.com/{writer_handle}"
