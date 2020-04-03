from datetime import datetime
from records import Record
from typing import Optional


class Prompt(dict):
    def __init__(self, record: Record) -> None:
        self.id: str = record["tweet_id"]
        self.date: datetime = datetime(
            record["date"].year, record["date"].month, record["date"].day
        )
        self.content: str = record["content"]
        self.word: str = record["word"]
        self.media: Optional[str] = record["media"]
        self.writer_id: str = record["uid"]
        self.writer_handle: str = record["writer_handle"]
        self.previous_day: Optional[str] = None
        self.next_day: Optional[str] = None

        # Make the class JSON serializable
        super().__init__(self.__dict__)

    def __str__(self):
        return f"https://twitter.com/{self.writer_handle}/status/{self.id}"
