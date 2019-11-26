__all__ = [
    "make_error_response"
]


def make_error_response(msg: str, status: int) -> tuple:
    return ({"error_msg": msg}, status)
