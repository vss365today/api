__all__ = [
    "date_iso_format",
    "make_response",
    "make_error_response"
]


def date_iso_format(dt) -> str:
    return dt.strftime("%Y-%m-%d")


def make_response(data: dict, status: int) -> tuple:
    return (data, status)


def make_error_response(msg: str, status: int) -> tuple:
    return make_response({"error_msg": msg}, status)
