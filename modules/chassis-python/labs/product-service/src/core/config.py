import os
import yaml
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    host: str = "127.0.0.1"
    port: int = 8000
    debug: bool = False
    database_url: str = ""

    class Config:
        env_prefix = ""  # optional, can prefix variables like APP_

def load_settings(path="settings.yaml") -> Settings:
    with open(path, "r") as f:
        cfg = yaml.safe_load(f)

    settings = Settings(
        host=cfg.get("app", {}).get("host"),
        port=cfg.get("app", {}).get("port"),
        debug=cfg.get("app", {}).get("debug"),
        database_url=cfg.get("database", {}).get("url"),
    )

    settings.host = os.getenv("HOST", settings.host)
    settings.port = int(os.getenv("PORT", settings.port))
    settings.debug = os.getenv("DEBUG", str(settings.debug)).lower() == "true"
    settings.database_url = os.getenv("DATABASE_URL", settings.database_url)

    return settings

settings = load_settings()
