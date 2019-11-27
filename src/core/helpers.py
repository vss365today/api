__all__ = [
    "make_response",
    "make_error_response"
]


def make_response(data: dict, status: int) -> tuple:
    return (data, status)


def make_error_response(msg: str, status: int) -> tuple:
    return make_response({"error_msg": msg}, status)
