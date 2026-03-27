from typing import Any
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models import User, Post
from src.schemas import UserCreate
from src.core import hash_password


async def is_id_exists(
    db: AsyncSession,
    user_id: int,
) -> bool:
    result = await db.scalar(
        select(User.id).where(User.id == user_id),
    )

    return result is not None


async def is_username_taken(
    db: AsyncSession,
    username: str,
    exclude_user_id: int | None = None,
) -> bool:
    stmt = select(User.id).where(func.lower(User.username) == username.lower())
    if exclude_user_id is not None:
        stmt = stmt.where(User.id != exclude_user_id)

    result = await db.scalar(stmt)

    return result is not None


async def is_email_taken(
    db: AsyncSession,
    email: str,
    exclude_user_id: int | None = None,
) -> bool:
    stmt = select(User.id).where(func.lower(User.email) == email.lower())

    if exclude_user_id is not None:
        stmt = stmt.where(User.id != exclude_user_id)
    result = await db.scalar(stmt)

    return result is not None


async def fetch_user_by_id(
    db: AsyncSession,
    user_id: int,
) -> User | None:
    return await db.scalar(
        select(User).where(User.id == user_id),
    )


async def fetch_user_by_email(
    db: AsyncSession,
    email: str,
) -> User | None:
    return await db.scalar(
        select(User).where(func.lower(User.email) == email.lower()),
    )


async def user_create(
    db: AsyncSession,
    user: UserCreate,
) -> User:
    new_user = User(
        username=user.username,
        email=user.email.lower(),
        password_hash=hash_password(user.password),
    )

    db.add(new_user)
    await db.commit()

    return new_user


async def user_update(
    db: AsyncSession,
    user_id: int,
    update_data: dict[str, Any],
) -> User:
    stmt = update(User).where(User.id == user_id).values(**update_data).returning(User)

    updated_user = await db.scalar(stmt)

    await db.commit()
    return updated_user


async def user_delete(db: AsyncSession, user: User) -> None:
    await db.delete(user)
    await db.commit()


async def fetch_posts_by_user_id(
    db: AsyncSession,
    user_id: int,
) -> list[Post]:
    stmt = (
        select(Post).options(selectinload(Post.author)).where(Post.user_id == user_id)
    )
    result = await db.execute(stmt)
    posts = result.scalars().all()

    return posts
