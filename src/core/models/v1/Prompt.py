from datetime import datetime
from typing import Any


class Prompt(dict):
    def __init__(self, record: dict[str, Any]) -> None:
        self.id: str = record["tweet_id"]
        self.date: datetime = datetime(
            record["date"].year, record["date"].month, record["date"].day
        )
        self.content: str = record["content"]
        self.word: str = record["word"]
        self.media: str | None = record["media"]
        self.media_alt_text: str | None = record["media_alt_text"]
        self.writer_id: str = record["uid"]
        self.writer_handle: str = record["writer_handle"]
        self.date_added: datetime = record["date_added"]
        self.previous: str | None = None
        self.next: str | None = None
        self.url: str = self.make_url(self.writer_handle, self.id)

        # Make the class JSON serializable
        super().__init__(self.__dict__)

    @staticmethod
    def make_url(handle: str, tweet_id: str) -> str:
        """Create a Twitter URL to the Prompt tweet."""
        return f"https://twitter.com/{handle}/status/{tweet_id}"
