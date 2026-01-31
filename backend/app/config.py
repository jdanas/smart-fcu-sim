from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "Smart FCU Simulator"
    database_url: str = "sqlite+aiosqlite:///./data/hvac.db"
    environment: str = "development"

    # Simulation settings
    sensor_update_interval: float = 5.0  # seconds
    prediction_horizon_minutes: int = 15
    discovery_check_interval: float = 30.0  # seconds

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
