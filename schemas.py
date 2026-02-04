from pydantic import BaseModel, ConfigDict, Field
from typing import Annotated


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
    author: Annotated[
        str,
        Field(min_length=1, description="Author of the post", examples=["Priyanshu"]),
    ]


class PostCreate(PostBase):
    pass


class PostResponse(PostBase):
    id: int
    date_posted: str

    model_config = ConfigDict(from_attributes=True)
