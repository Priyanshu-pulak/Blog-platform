from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Path,
)

from sqlalchemy.ext.asyncio import AsyncSession

from src.models import User, Post
from src.core import get_db
from src.schemas import (
    UserCreate,
    UserUpdate,
    UserResponse,
    PostResponse,
)

from src.crud import (
    is_id_exists,
    is_username_taken,
    is_email_taken,
    get_user_by_id,
    user_create,
    user_update,
    user_delete,
    get_posts_by_user_id,
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

    username_exists = await is_username_taken(db, user.username)

    if username_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with username '{user.username}' already exists",
        )

    email_exists = await is_email_taken(db, user.email)

    if email_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email '{user.email}' already exists",
        )

    new_user = await user_create(db, user)

    return new_user


@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
async def get_user(
    user_id: Annotated[
        int,
        Path(
            description="The ID of the user you want to retrieve",
            examples=[1],
        ),
    ],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    existing_user = await get_user_by_id(db, user_id)

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
            description="The ID of the user you want to update",
            examples=[1],
        ),
    ],
    user_update_data: UserUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    update_data = user_update_data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data provided to update",
        )

    id_exists = await is_id_exists(db, user_id)

    if not id_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )

    if "username" in update_data:
        if await is_username_taken(db, update_data["username"], user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with username '{update_data['username']}' already exists",
            )

    if "email" in update_data:
        if await is_email_taken(db, update_data["email"], user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with email '{update_data['email']}' already exists",
            )

    updated_user = await user_update(db, user_id, update_data)

    return updated_user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(
    user_id: Annotated[
        int,
        Path(
            description="The ID of the user you want to delete",
            examples=[1],
        ),
    ],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    existing_user = await get_user_by_id(db, user_id)

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )

    return await user_delete(db, existing_user)


@router.get(
    "/{user_id}/posts",
    response_model=list[PostResponse],
)
async def get_user_posts(
    user_id: Annotated[
        int,
        Path(
            description="The ID of the user whose posts you want to retrieve",
            examples=[1],
        ),
    ],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[Post]:
    user_exists = await is_id_exists(db, user_id)

    if not user_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )

    posts = await get_posts_by_user_id(db, user_id)

    return posts
