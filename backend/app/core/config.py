from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Union


class Settings(BaseSettings):
    gemini_api_key: str = ""
    cors_origins: Union[str, List[str]] = "http://localhost:5173"
    session_ttl_minutes: int = 30

    @property
    def cors_origins_list(self) -> List[str]:
        if isinstance(self.cors_origins, str):
            return [origin.strip() for origin in self.cors_origins.split(",")]
        return self.cors_origins

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
