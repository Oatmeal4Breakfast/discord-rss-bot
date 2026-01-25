from dataclasses import dataclass


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
