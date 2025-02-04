from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "James-AI-Assistant"
    database_url: str

    class Config:
        env_file = ".env"

settings = Settings()
