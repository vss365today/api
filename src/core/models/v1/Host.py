from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class Host:
    uid: str
    handle: str
    url: str = field(default="")

    def __post_init__(self):
        self.url = self.make_url(self.handle)

    @staticmethod
    def make_url(handle: str) -> str:
        """Create a Twitter URL to the Host's profile."""
        return f"https://twitter.com/{handle}"

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
