from dataclasses import dataclass


@dataclass
class EmailTemplate:
    text: str
    html: str
