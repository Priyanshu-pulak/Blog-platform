from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base

intpk = Annotated[int, mapped_column(primary_key=True, index=True)]

timestamp = Annotated[
    datetime, mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
]

str50 = Annotated[str, mapped_column(String(50))]
str120 = Annotated[str, mapped_column(String(120))]
str200 = Annotated[str, mapped_column(String(200))]
text_content = Annotated[str, mapped_column(Text)]

user_fk = Annotated[int, mapped_column(ForeignKey("users.id"), index=True)]


class User(Base):
    __tablename__ = "users"

    id: Mapped[intpk]
    username: Mapped[str50] = mapped_column(unique=True)
    email: Mapped[str120] = mapped_column(unique=True)
    password_hash: Mapped[str200]
    image_file: Mapped[str200 | None] = mapped_column(default=None)

    posts: Mapped[list[Post]] = relationship(
        back_populates="author", cascade="all, delete-orphan"
    )

    @property
    def image_path(self) -> str:
        if self.image_file:
            return f"/media/profile_pics/{self.image_file}"
        return "/static/profile_pics/default.jpg"


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[intpk]
    title: Mapped[str120]
    content: Mapped[text_content]
    user_id: Mapped[user_fk]
    date_posted: Mapped[timestamp]

    author: Mapped[User] = relationship(back_populates="posts")
