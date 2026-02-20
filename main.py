from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, Request, HTTPException, status, Depends, Path
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models import Post, User
from database import Base, engine, get_db
from src.schemas import (
    PostCreate,
    PostResponse,
    PostUpdate,
)

from src.routers import users_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(users_router, prefix="/api/users", tags=["users"])

app.mount("/static", StaticFiles(directory="static"), name="static")

app.mount("/media", StaticFiles(directory="media"), name="media")
templates = Jinja2Templates(directory="templates")


def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_dict = {}
    for error in exc.errors():
        field = error["loc"][-1]
        message = error["msg"]
        error_dict[field] = message

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"errors": error_dict},
    )


app.add_exception_handler(RequestValidationError, validation_exception_handler)


@app.get("/", include_in_schema=False)
async def home(request: Request, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(Post).options(selectinload(Post.author)),
    )
    posts = result.scalars().all()

    return templates.TemplateResponse(
        request,
        "home.html",
        {"posts": posts, "title": "Home"},
    )


@app.post(
    "/api/posts",
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


@app.get(
    "/api/posts",
    response_model=list[PostResponse],
)
async def get_posts(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[Post]:
    stmt = select(Post).options(selectinload(Post.author))
    result = await db.execute(stmt)
    posts = result.scalars().all()

    return posts


@app.get("/api/posts/{post_id}", response_model=PostResponse)
async def get_post(
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


@app.put(
    "/api/posts/{post_id}",
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


@app.patch(
    "/api/posts/{post_id}",
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


@app.delete(
    "/api/posts/{post_id}",
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
