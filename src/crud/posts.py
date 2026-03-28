from typing import Any

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models import Post

async def post_create(
    db: AsyncSession,
    post: Post,
) -> Post:
    db.add(post)
    await db.commit()

    return post

async def fetch_post_by_id(
    db: AsyncSession,
    post_id: int,
) -> Post | None:
    stmt = select(Post).where(Post.id == post_id).options(selectinload(Post.author))
    post = await db.scalar(stmt)

    return post


async def fetch_all_posts(
    db: AsyncSession,
) -> list[Post]:
    stmt = select(Post).options(selectinload(Post.author))
    result = await db.execute(stmt)

    return result.scalars().all()

async def full_post_update(
    db: AsyncSession,
    post_id: int,
    new_data: dict[str, Any],
) -> Post | None:
    stmt = (
        update(Post)
        .where(Post.id == post_id)
        .values(**new_data)
        .returning(Post)
        .options(selectinload(Post.author))
    )
    
    updated_post = await db.scalar(stmt)
    await db.commit()

    return updated_post

async def partial_post_update(
    db: AsyncSession,
    post_id: int,
    update_data: dict[str, Any],
) -> Post | None:
    stmt = (
        update(Post)
        .where(Post.id == post_id)
        .values(**update_data)
        .returning(Post)
        .options(selectinload(Post.author))
    )

    updated_post = await db.scalar(stmt)
    await db.commit()
    return updated_post

async def post_delete(
    db: AsyncSession,
    post_id: int,
    user_id: int,
) -> bool:
    stmt = delete(Post).where(
        Post.id == post_id,
        Post.user_id == user_id,
    )
    result = await db.execute(stmt)
    
    await db.commit()

    return result.rowcount > 0
