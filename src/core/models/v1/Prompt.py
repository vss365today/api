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
        self.date_added: datetime = record["date_added"]
        self.previous_day: Optional[str] = None
        self.next_day: Optional[str] = None
        self.url: str = self.make_url(self.writer_handle, self.id)

        # Make the class JSON serializable
        super().__init__(self.__dict__)

    @staticmethod
    def make_url(writer_handle: str, tweet_id: str) -> str:
        return f"https://twitter.com/{writer_handle}/status/{tweet_id}"
