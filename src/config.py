from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    retry_count: int = Field(alias="RETRY_COUNT")
    sent_file: str = Field(alias="SENT_FILE")


config = Config()
