import os

from pydantic_settings import BaseSettings

from pathlib import Path


class Settings(BaseSettings):
    """
    Class to store the configurations of the application
    """

    PROJECT_NAME: str
    PROJECT_VERSION: str
    PROJECT_DESCRIPTION: str

    # Database settings
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DATABASE_ECHO: bool

    # JWT settings
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    REFRESH_TOKEN_EXPIRES_IN: int
    ACCESS_TOKEN_EXPIRES_IN: int

    # OTP settings
    OTP_EXPIRED_TIME: int

    CLIENT_ORIGIN: str

    LOG_PATH: str

    # Email settings
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_PORT: int
    MAIL_FROM: str
    MAIL_SERVER: str
    MAIL_FROM_NAME: str

    DEBUG_MODE: bool

    BASE_URL: str

    ADMIN_SITE_REQUIRED: bool

    @property
    def MYSQL_DATABASE_URL(self):
        return f"mysql+aiomysql://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    IMAGE_PATH: str = os.path.join("static", "images")
    SAVE_IMAGE_PATH: str = os.path.join("app", IMAGE_PATH)

    IMAGE_URL: str = "/static/images"

    datetime_format: str = "%Y-%m-%d %H:%M:%S"
    date_format: str = "%Y-%m-%d"

    class Config:
        env_file = Path(".") / ".env"


settings = Settings()
