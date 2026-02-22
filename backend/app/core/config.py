import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List, Union, Any

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "API Riset Jurnal (Sequential Agent)"
    DEBUG: bool = False
    PORT: int = 8080
    
    # Google Cloud Settings
    GOOGLE_CLOUD_PROJECT: str = "" # Harap isi di .env
    LOCATION: str = "global"
    
    # Security
    API_KEY: str = ""  
    # ALLOWED_ORIGINS bisa diisi string dipisah koma di .env, atau JSON list
    ALLOWED_ORIGINS: Union[List[str], str] = ["http://localhost:3000", "http://localhost:8080"]
    
    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        return v
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
