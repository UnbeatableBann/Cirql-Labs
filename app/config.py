from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_PATH : str
    DEFAULT_INTERVAL : str
    FRONTEND_CONNECTION: str
    ALLOWED_HOSTS: List[str]

    model_config = SettingsConfigDict(
        env_file=".env", extra="ignore", str_strip_whitespace=True
    )

    @field_validator("*", mode="before") 
    def strip_quotes(cls, v: str):
        if isinstance(v, str) :
            v = v.strip()
            if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                return v[1:-1]
        return v
    
    def realfun():
        pass

settings = Settings()
