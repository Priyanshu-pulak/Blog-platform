from typing import Annotated

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core import (
    get_db,
    lifespan,
    validation_exception_handler,
)
from src.models import Post
from src.routers import auth_router, post_router, users_router

app = FastAPI(lifespan=lifespan)

app.include_router(users_router, prefix="/api/users", tags=["Users"])
app.include_router(post_router, prefix="/api/posts", tags=["Posts"])
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])

app.mount("/static", StaticFiles(directory="static"), name="static")

app.mount("/media", StaticFiles(directory="media"), name="media")
templates = Jinja2Templates(directory="templates")

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
