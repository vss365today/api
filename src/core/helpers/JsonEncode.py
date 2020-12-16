from datetime import datetime
from flask.json import JSONEncoder


class JsonEncode(JSONEncoder):
    """Override the default Flask JSONEncoder.
    By default, Flask converts datetime objects to RFC 1123 dates.
    Override this behavior to convert them to ISO 8601 format instead.
    """

    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        return super().default(o)
