from dataclasses import dataclass
from typing import List, Dict


type FeedEntries = List[Dict[str, str]]


@dataclass
class Entry:
    title: str
    link: str
    published: str
    summary: str


@dataclass
class Config:
    default_webhook: str
    rate_limit_delay: float
    batch_size: int
    filter_by_today: bool
