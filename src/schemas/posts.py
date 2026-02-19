from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import Annotated

from src.schemas.users import UserResponse


class PostBase(BaseModel):
    title: Annotated[
        str,
        Field(
            min_length=1,
            max_length=100,
            description="Title of the post",
            examples=["first post"],
        ),
    ]
    content: Annotated[
        str,
        Field(
            min_length=1,
            description="Content for the post",
            examples=["This is my first post content"],
        ),
    ]


class PostCreate(PostBase):
    user_id: Annotated[
        int,
        Field(
            description="ID of the author of the post",
            examples=[1],
        ),
    ]


class PostUpdate(PostBase):
    title: Annotated[
        str | None,
        Field(
            default=None,
            min_length=1,
            max_length=100,
            description="Title of the post",
            examples=["Updated title of the post"],
        ),
    ]
    content: Annotated[
        str | None,
        Field(
            default=None,
            min_length=1,
            description="Content for the post",
            examples=["Updated content for the post"],
        ),
    ]


class PostResponse(PostBase):
    model_config = ConfigDict(from_attributes=True)

    post_id: Annotated[
        int,
        Field(
            validation_alias="id",
            description="ID of the post",
            examples=[1],
        ),
    ]
    user_id: Annotated[
        int,
        Field(
            description="ID of the author of the post",
            examples=[1],
        ),
    ]
    date_posted: Annotated[
        datetime,
        Field(
            description="Date and time when the post was created",
            examples=["2024-06-01T12:00:00Z"],
        ),
    ]
    author: Annotated[
        UserResponse,
        Field(
            description="Author of the post",
        ),
    ]
