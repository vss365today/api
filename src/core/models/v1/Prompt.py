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
        self.media_alt_text: Optional[str] = record["media_alt_text"]
        self.writer_id: str = record["uid"]
        self.writer_handle: str = record["writer_handle"]
        self.date_added: datetime = record["date_added"]
        self.previous: Optional[str] = None
        self.next: Optional[str] = None
        self.url: str = self.make_url(self.writer_handle, self.id)

        # Make the class JSON serializable
        super().__init__(self.__dict__)

    @staticmethod
    def make_url(handle: str, tweet_id: str) -> str:
        """Create a Twitter URL to the Prompt tweet."""
        return f"https://twitter.com/{handle}/status/{tweet_id}"
