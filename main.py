from fastapi import FastAPI, Request, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from schemas import PostCreate, PostResponse

app = FastAPI()

app.mount("/static", StaticFiles(directory = "static"), name = "static")

templates = Jinja2Templates(directory = "templates")

posts: list[dict] = [
    {
        "id": 1,
        "author": "Priyanshu Pulak",
        "title": "FastAPI is Awesome",
        "content": "This framework is really easy to use and super fast.",
        "date_posted": "31st Jan, 2026",
    },
    {
        "id": 2,
        "author": "Prabal",
        "title": "Python is Great for Web Development",
        "content": "Python is a great language for web development, and FastAPI makes it even better.",
        "date_posted": "31st Jan, 2026",
    },
]

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

@app.get("/", include_in_schema = False)
def home(request: Request):
    return templates.TemplateResponse(
        request,
        "home.html",
        {"posts" : posts, "title" : "Home"},
    )

@app.get("/api/posts", response_model=list[PostResponse])
def get_posts():
    return posts

@app.get("/api/posts/{post_id}", response_model=PostResponse)
def get_post(post_id: int):
    for post in posts:
        if post.get("id") == post_id:
            return post
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Post with id {post_id} not found",
    )

@app.post(
    "/api/posts",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_post(post: PostCreate):
    new_id = len(posts) + 1
    new_post = post.model_dump()
    new_post["id"] = new_id
    new_post["date_posted"] = "1st Feb, 2026"
    posts.append(new_post)
    return new_post