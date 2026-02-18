from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    retry_count: int = Field(alias="RETRY_COUNT")
    sent_file: str = Field(alias="SENT_FILE")
    feed_file: str = Field(alias="FEED_FILE")
    log_level: str = Field(alias="LOG_LEVEL")
    log_file: str = Field(alias="LOG_FILE")


def get_config() -> Config:
    return Config()
