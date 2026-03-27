from typing import Annotated
from pydantic import BaseModel, Field

class Token(BaseModel):
    access_token: Annotated[
        str,
        Field(
            description="JWT access token to authenticate the user for protected routes",
        )
    ]
    token_type: Annotated[
        str,
        Field(
            description="Type of the token"
        )
    ]


