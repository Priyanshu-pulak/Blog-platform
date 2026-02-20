from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Path,
)

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import User
from database import get_db
from src.schemas import (
    UserCreate,
    UserResponse,
)

router = APIRouter()


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:

    user_exists = await db.scalar(select(User.id).where(User.username == user.username))

    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with username '{user.username}' already exists",
        )

    email_exists = await db.scalar(select(User.id).where(User.email == user.email))

    if email_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email '{user.email}' already exists",
        )

    new_user = User(
        username=user.username,
        email=user.email,
    )

    db.add(new_user)
    await db.commit()

    return new_user


@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
async def get_user(
    user_id: Annotated[
        int,
        Path(
            ...,
            description="The ID of the user you want to retrieve",
            examples=[1],
        ),
    ],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    existing_user = await db.scalar(
        select(User).where(User.id == user_id),
    )

    if existing_user:
        return existing_user

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"User with id {user_id} not found",
    )
