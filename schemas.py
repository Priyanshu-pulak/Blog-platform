from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, EmailStr
from typing import Annotated


class UserBase(BaseModel):
    username: Annotated[
        str,
        Field(
            min_length=1,
            max_length=50,
            description="Username of the author",
            examples=["Priyanshu"],
        ),
    ]
    email: Annotated[
        EmailStr,
        Field(
            max_length=120,
            description="Email address of the author",
            examples=["priyanshu1@gamil.com"],
        ),
    ]

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True) # pydantic will read data from the attributes of the SQLAlchemy model instance
    id: Annotated[
        int,
        Field(
            description="ID of the user",
            examples=[1],
        ),
    ]
    image_file: Annotated[
        str | None,
        Field(
            description="Profile picture of the user",
        ),
    ]
    image_path: Annotated[
        str,
        Field(
            description="URL path to the profile picture of the user",
        ),
    ]

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

