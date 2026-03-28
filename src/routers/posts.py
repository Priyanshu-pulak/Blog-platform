from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Path,
)

from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Post
from src.core import get_db
from src.schemas import (
    PostCreate,
    PostUpdate,
    PostResponse,
)

from src.crud import (
    post_create,
    fetch_post_by_id,
    fetch_all_posts,
    full_post_update,
    partial_post_update,
    post_delete,
)

from src.dependencies import CurrentUser

router = APIRouter()


@router.post(
    "",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_post(
    post: PostCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Post:
    new_post = Post(
        title=post.title,
        content=post.content,
        author=current_user,
    )

    return await post_create(db, new_post)


@router.get(
    "",
    response_model=list[PostResponse],
)
async def get_all_posts(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[Post]:
    posts = await fetch_all_posts(db)

    return posts


@router.get(
    "/{post_id}",
    response_model=PostResponse,
)
async def get_post_by_id(
    post_id: Annotated[
        int,
        Path(
            description="The ID of the post you want to retrieve",
            examples=[1],
        ),
    ],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Post:
    post = await fetch_post_by_id(db, post_id)

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
            description="The ID of the post you want to update",
            examples=[1],
        ),
    ],
    post_data: PostCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Post:

    update_data = post_data.model_dump()
    updated_post = await full_post_update(db, post_id, update_data)

    if not updated_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {post_id} not found",
        )

    if updated_post.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this post",
        )

    return updated_post


@router.patch(
    "/{post_id}",
    response_model=PostResponse,
)
async def update_post_partial(
    post_id: Annotated[
        int,
        Path(
            description="The ID of the post you want to update",
            examples=[1],
        ),
    ],
    post_data: PostUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Post:
    update_data = post_data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data provided to update",
        )

    updated_post = await partial_post_update(db, post_id, update_data)

    if not updated_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {post_id} not found",
        )

    if updated_post.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this post",
        )

    return updated_post


@router.delete(
    "/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_post(
    post_id: Annotated[
        int,
        Path(
            description="The ID of the post you want to delete",
            examples=[1],
        ),
    ],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
) -> None:
    deleted = await post_delete(db, post_id, current_user.id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {post_id} not found",
        )
