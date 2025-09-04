from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "backend"
    secret_key: str
    database_url: str
    redis_url: str
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    class Config:
        env_file = ".env"


settings = Settings()
