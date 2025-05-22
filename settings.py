# settings.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    S3_BUCKET: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_DEFAULT_REGION: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
