from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Path,
)

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models import User, Post
from database import get_db
from src.schemas import (
    PostCreate,
    PostUpdate,
    PostResponse,
)

router = APIRouter()


@router.post(
    "",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_post(
    post: PostCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Post:
    existing_user = await db.scalar(
        select(User).where(User.id == post.user_id),
    )

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {post.user_id} not found",
        )

    new_post = Post(
        title=post.title,
        content=post.content,
        author=existing_user,
    )

    db.add(new_post)
    await db.commit()

    return new_post


@router.get(
    "",
    response_model=list[PostResponse],
)
async def get_all_posts(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[Post]:
    stmt = select(Post).options(selectinload(Post.author))

    result = await db.execute(stmt)
    posts = result.scalars().all()

    return posts


@router.get(
    "/{post_id}",
    response_model=PostResponse,
)
async def get_post_by_id(
    post_id: Annotated[
        int,
        Path(
            ...,
            description="The ID of the post you want to retrieve",
            examples=[1],
        ),
    ],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Post:
    stmt = select(Post).options(selectinload(Post.author)).where(Post.id == post_id)
    post = await db.scalar(stmt)

    if post:
        return post

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Post with id {post_id} not found",
    )


@router.put(
    "/{post_id}",
    response_model=PostResponse,
)
async def update_post_full(
    post_id: Annotated[
        int,
        Path(
            ...,
            description="The ID of the post you want to update",
            examples=[1],
        ),
    ],
    post_data: PostCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Post:
    user_exists = await db.scalar(
        select(User.id).where(User.id == post_data.user_id),
    )

    if not user_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {post_data.user_id} not found",
        )

    stmt = (
        update(Post)
        .where(Post.id == post_id)
        .values(**post_data.model_dump())
        .returning(Post)
        .options(selectinload(Post.author))
    )

    updated_post = await db.scalar(stmt)

    if not updated_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {post_id} not found",
        )

    await db.commit()
    return updated_post


@router.patch(
    "/{post_id}",
    response_model=PostResponse,
)
async def update_post_partial(
    post_id: Annotated[
        int,
        Path(
            ...,
            description="The ID of the post you want to update",
            examples=[1],
        ),
    ],
    post_data: PostUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Post:
    update_data = post_data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data provided to update",
        )

    stmt = (
        update(Post)
        .where(Post.id == post_id)
        .values(**update_data)
        .returning(Post)
        .options(selectinload(Post.author))
    )

    updated_post = await db.scalar(stmt)

    if not updated_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {post_id} not found",
        )

    await db.commit()
    return updated_post


@router.delete(
    "/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_post(
    post_id: Annotated[
        int,
        Path(
            ...,
            description="The ID of the post you want to delete",
            examples=[1],
        ),
    ],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    stmt = delete(Post).where(Post.id == post_id)
    result = await db.execute(stmt)

    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {post_id} not found",
        )

    await db.commit()
