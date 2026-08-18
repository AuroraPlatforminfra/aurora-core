"""Configuration management"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings from environment"""

    app_name: str = "Aurora Core"
    app_version: str = "0.0.1"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000

    database_url: str = "postgresql://aurora:aurora@localhost/aurora"
    
    github_token: str = ""
    github_org: str = "aurora-mlops"
    
    k8s_config_path: Optional[str] = None
    
    otel_enabled: bool = True
    otel_jaeger_agent_host: str = "localhost"
    otel_jaeger_agent_port: int = 6831
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
