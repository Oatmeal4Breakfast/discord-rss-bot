from dataclasses import dataclass


@dataclass
class Entry:
    title: str
    link: str
    published: str
    summary: str
