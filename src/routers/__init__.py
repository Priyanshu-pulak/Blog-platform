from .users import router as users_router
from .posts import router as post_router

__all__ = [
    "users_router",
    "post_router",
]
