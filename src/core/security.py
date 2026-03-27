
from datetime import UTC, datetime, timedelta
import jwt
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from src.core.config import settings


# Creating a password hasher instance using argon2 with recommended settings
password_hasher = PasswordHash.recommended()
# tokenUrl is the endpoint where the client can obtain a token by providing username and password and it should be same as login url path in auth router
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hasher.verify(plain_password, hashed_password)


def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None,
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.access_token_expire_minutes
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key.get_secret_value(),
        algorithm=settings.algorithm,
    )

    return encoded_jwt


def verify_access_token(token: str) -> str | None:
    try:
        payload = jwt.decode(
            token,
            settings.secret_key.get_secret_value(),
            algorithms=[settings.algorithm],
            options={"require": ["exp"]},
        )
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
