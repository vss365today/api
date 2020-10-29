import json
from pathlib import Path


__all__ = ["get", "update", "timer_get", "timer_update"]


def __get_content() -> Path:
    return json.loads((Path() / "settings" / "settings.json").resolve().read_text())


def get():
    """TK."""
    pass


def update():
    """TK."""
    pass


def timer_get():
    """TK."""
    pass


def timer_update():
    """TK."""
    pass
