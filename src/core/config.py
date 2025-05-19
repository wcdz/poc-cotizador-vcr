from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any
from functools import lru_cache


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Cotizador VCR API"
    DESCRIPTION: str = "API para gestionar cotizaciones"
    VERSION: str = "0.1.0"
    DEBUG: bool = True
    
    # Configuraciones adicionales aquí
    # DB_URL: str = "sqlite:///./sql_app.db"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
