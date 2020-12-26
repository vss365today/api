from dataclasses import dataclass, InitVar
from datetime import datetime


@dataclass
class ApiKey:
    token: str
    desc: str
    date_created: datetime
    has_api_key: bool
    has_archive: bool
    has_broadcast: bool
    has_host: bool
    has_prompt: bool
    has_settings: bool
    has_subscription: bool

    # Do not expose the internal ID
    id: InitVar[int] = None
