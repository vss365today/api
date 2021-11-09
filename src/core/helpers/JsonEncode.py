import dataclasses
from datetime import datetime
from flask.json import JSONEncoder


class JsonEncode(JSONEncoder):
    """Override the default Flask JSONEncoder to support more data types."""

    def default(self, o):
        # Convert datetime objects to ISO 8601 instead of RFC 1123
        if isinstance(o, datetime):
            return o.isoformat()

        # Convert Data Classes into dictionaries
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)

        # Use default encoder
        return super().default(o)
