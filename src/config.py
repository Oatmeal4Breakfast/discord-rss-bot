from pydantic import Field
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator
from typing_extensions import Self


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    retry_count: int = Field(alias="RETRY_COUNT")
    sent_file: str = Field(alias="SENT_FILE")
    feed_file: str = Field(alias="FEED_FILE")
    log_level: str = Field(alias="LOG_LEVEL")
    log_file: str = Field(alias="LOG_FILE")

    @model_validator(mode="after")
    def _update_sent_file(self) -> Self:
        self.sent_file: str = str(Path.cwd() / self.sent_file)
        return self


def get_config() -> Config:
    return Config()
