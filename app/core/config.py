import os
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Notes Application"
    API_V1_STR: str = "/api/v1"
    
    # Standard Database settings
    POSTGRES_SERVER: str = os.environ.get("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.environ.get("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.environ.get("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.environ.get("POSTGRES_DB", "notes_db")
    
    # AWS Aurora settings
    USE_AURORA: bool = os.environ.get("USE_AURORA", "false").lower() == "true"
    AURORA_WRITER_ENDPOINT: str = os.environ.get("AURORA_WRITER_ENDPOINT", "")
    AURORA_READER_ENDPOINT: str = os.environ.get("AURORA_READER_ENDPOINT", "")
    AURORA_PORT: str = os.environ.get("AURORA_PORT", "5432")
    AURORA_USER: str = os.environ.get("AURORA_USER", POSTGRES_USER)
    AURORA_PASSWORD: str = os.environ.get("AURORA_PASSWORD", POSTGRES_PASSWORD)
    AURORA_DB: str = os.environ.get("AURORA_DB", POSTGRES_DB)
    
    # Database URIs
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """Returns the primary database URI (writer endpoint if Aurora is enabled)"""
        if self.USE_AURORA and self.AURORA_WRITER_ENDPOINT:
            return f"postgresql://{self.AURORA_USER}:{self.AURORA_PASSWORD}@{self.AURORA_WRITER_ENDPOINT}:{self.AURORA_PORT}/{self.AURORA_DB}"
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
    
    @property
    def SQLALCHEMY_READER_URI(self) -> str:
        """Returns the reader database URI if Aurora is enabled, otherwise same as primary URI"""
        if self.USE_AURORA and self.AURORA_READER_ENDPOINT:
            return f"postgresql://{self.AURORA_USER}:{self.AURORA_PASSWORD}@{self.AURORA_READER_ENDPOINT}:{self.AURORA_PORT}/{self.AURORA_DB}"
        return self.SQLALCHEMY_DATABASE_URI
    
    # JWT settings
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "your-secret-key-for-jwt")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS settings
    ALLOWED_ORIGINS: List[str] = ["*"]  # Allow any origin including localhost with any port
    
    # Model config using newer pydantic v2 syntax
    model_config = SettingsConfigDict(case_sensitive=True)


# Create settings instance
settings = Settings()