from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Path,
)

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models import User, Post
from src.core import get_db
from src.schemas import (
    UserCreate,
    UserUpdate,
    UserResponse,
    PostResponse,
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


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
)
async def update_user(
    user_id: Annotated[
        int,
        Path(
            ...,
            description="The ID of the user you want to update",
            examples=[1],
        ),
    ],
    user_update: UserUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    update_data = user_update.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data provided to update",
        )

    user_exists = await db.scalar(
        select(User.id).where(User.id == user_id),
    )

    if not user_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )

    if "username" in update_data:
        stmt = select(User.id).where(
            User.username == update_data["username"],
            User.id != user_id,
        )

        if await db.scalar(stmt):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with username '{update_data['username']}' already exists",
            )

    if "email" in update_data:
        stmt = select(User.id).where(
            User.email == update_data["email"],
            User.id != user_id,
        )

        if await db.scalar(stmt):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with email '{update_data['email']}' already exists",
            )

    stmt = update(User).where(User.id == user_id).values(**update_data).returning(User)

    updated_user = await db.scalar(stmt)
    await db.commit()
    return updated_user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(
    user_id: Annotated[
        int,
        Path(
            ...,
            description="The ID of the user you want to delete",
            examples=[1],
        ),
    ],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    existing_user = await db.scalar(
        select(User).where(User.id == user_id),
    )

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )

    await db.delete(existing_user)
    await db.commit()

@router.get(
    "/{user_id}/posts",
    response_model=list[PostResponse],
)
async def get_user_posts(
    user_id: Annotated[
        int,
        Path(
            ...,
            description="The ID of the user whose posts you want to retrieve",
            examples=[1],
        ),
    ],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[Post]:
    user_exists = await db.scalar(
        select(User.id).where(User.id == user_id),
    )

    if user_exists is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )

    result = await db.execute(
        select(Post).options(selectinload(Post.author)).where(Post.user_id == user_id),
    )
    posts = result.scalars().all()

    return posts
