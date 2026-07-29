from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field


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
            examples=["priyanshu1@gmail.com"],
        ),
    ]


class UserCreate(UserBase):
    password: Annotated[
        str,
        Field(
            min_length=8,
            max_length=20,
            description="Password for the user must be between 8 and 20 characters",
            examples=["Password@123"],
        ),
    ]


class UserUpdate(BaseModel):
    username: Annotated[
        str | None,
        Field(
            default=None,
            min_length=1,
            max_length=50,
            description="Update username of the user",
            examples=["Priyanshu"],
        ),
    ]
    email: Annotated[
        EmailStr | None,
        Field(
            default=None,
            max_length=120,
            description="Update email address of the user",
            examples=["priyanshu1@gmail.com"],
        ),
    ]
    image_file: Annotated[
        str | None,
        Field(
            default=None,
            min_length=1,
            max_length=200,
            description="Update profile picture of the user",
        ),
    ]


class UserPublicResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )  # pydantic will read data from the attributes of the SQLAlchemy model instance
    id: Annotated[
        int,
        Field(
            description="ID of the user",
            examples=[1],
        ),
    ]
    username: Annotated[
        str,
        Field(
            description="Username of the user",
            examples=["Priyanshu"],
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


class UserPrivateResponse(UserPublicResponse):
    email: Annotated[
        EmailStr,
        Field(
            description="Email address of the user",
            examples=["priyanshu@gmail.com"],
        ),
    ]
