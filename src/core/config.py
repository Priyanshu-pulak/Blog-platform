from typing import Annotated
from pydantic import SecretStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    secret_key: Annotated[
        SecretStr,
        Field(
            description="Secret key used for hashing the password and signing the JWT tokens",
            examples=["mysecretkey"],
        ),
    ]
    algorithm: Annotated[
        str,
        Field(
            default="HS256",
            description="Algorithm used for signing the JWT tokens",
            examples=["HS256", "HS512"],
        ),
    ]
    access_token_expire_minutes: Annotated[
        int,
        Field(
            default=30,
            description="Expiration time for the JWT access token in minutes",
            examples=[30],
        ),
    ]


# Loaded from the .env file and available as settings object
settings = Settings()
