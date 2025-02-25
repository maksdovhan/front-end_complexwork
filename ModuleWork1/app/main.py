from fastapi import FastAPI, HTTPException, Response, status
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from .api import api
from .logic import find_url, count_redirect


def init():
    from pydantic import AnyHttpUrl
    from .models import CreateUserModel, CreateURLModel
    from .logic import create_user, create_url
    import random

    files = [
        "app/main.py",
        "app/api.py",
        "app/dependencies.py",
        "app/models.py",
        "app/logic.py",
    ]
    users = [
        create_user(CreateUserModel(username=f"user_{i+1}", password="12345678"))
        for i in range(3)
    ]
    urls = [
        create_url(
            CreateURLModel(
                url=AnyHttpUrl(
                    f"https://github.com/KPI-FICT-FrontEnd/shortener/tree/main/{random.choice(files)}"
                )
            ),
            owner=random.choice(users),
        )
        for _ in range(10)
    ]
    for _ in range(100):
        count_redirect(random.choice(urls))
    return


init()


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api, prefix="/api", tags=["api"])


@app.get("/", response_class=HTMLResponse)
async def root():
    return """
        <html><head><title>URL Shortener</title></head>
        <body><h1>URL Shortener</h1>
        <p><a href="/docs">Swagger UI</a></p>
        <p><a href="/redoc">Redoc</a></p>
        <p><a href="/openapi.json">OpenAPI Schema</a></p>
        </body></html>
    """


@app.get(
    "/{short}",
    response_class=HTMLResponse,
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
)
async def redirect(short: str, response: Response):
    url = find_url(short)
    if url is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    count_redirect(url)
    response.headers["Location"] = url.url.unicode_string()
    return f"""
        <!DOCTYPE html>
        <html>
          <head>
            <meta http-equiv="refresh" content="0; url={url.url}" />
            <meta charset="utf-8" />
          </head>
          <body>
            <a href="{url.url}">Click here if not redirected</a>
          </body>
        </html>
    """
