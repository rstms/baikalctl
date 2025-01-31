import logging
from contextlib import asynccontextmanager

from arrow import Arrow
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from typing_extensions import Annotated, Dict, List

from . import settings
from .browser import BrowserException, Session
from .models import (
    Account,
    AddBookRequest,
    AddUserRequest,
    Book,
    DeleteBookRequest,
    DeleteUserRequest,
    User,
)
from .version import __version__

log = logging.getLogger("uvicorn")


async def read_security_headers(
    x_admin_username: Annotated[str, Header()],
    x_admin_password: Annotated[str, Header()],
    x_api_key: Annotated[str, Header()],
):
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="invalid API key")
    if not x_admin_username:
        raise HTTPException(status_code=401, detail="invalid username")
    if not x_admin_password:
        raise HTTPException(status_code=401, detail="missing password")
    app.state.account = Account(username=x_admin_username, password=x_admin_password)


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.setLevel(settings.LOG_LEVEL)
    log.info(f"baikalctl v{__version__} startup")
    app.state.startup_time = Arrow.now()
    app.state.session = Session()
    yield
    log.info("shutdown")
    app.state.session.shutdown()


app = FastAPI(dependencies=[Depends(read_security_headers)], lifespan=lifespan)


@app.exception_handler(BrowserException)
async def browser_exception_handler(request: Request, exc: BrowserException):
    return JSONResponse(
        status_code=500,
        content={exc.__class__.__name__: str(exc)},
    )


@app.middleware("http")
async def logout_after_request(request: Request, call_next):
    response = await call_next(request)
    app.state.session.logout()
    return response


@app.get("/status/")
async def get_status() -> Dict[str, str]:
    return app.state.session.status(app.state.account)


@app.post("/reset/")
async def post_reset() -> Dict[str, str]:
    return app.state.session.reset(app.state.account)


@app.post("/initialize/")
async def post_initialize() -> Dict[str, str]:
    return app.state.session.initialize(app.state.account)


@app.get("/users/")
async def get_users() -> List[User]:
    return app.state.session.users(app.state.account)


@app.post("/user/")
async def post_user(request: AddUserRequest) -> User:
    return app.state.session.add_user(app.state.account, request)


@app.delete("/user/")
async def delete_user(request: DeleteUserRequest) -> Dict[str, str]:
    return app.state.session.delete_user(app.state.account, request)


@app.get("/books/")
async def get_addressbooks_all() -> List[Book]:
    users = app.state.session.users(app.state.account)
    books = []
    for user in users:
        books.extend(app.state.session.books(app.state.account, user.username))
    return books


@app.get("/books/{username}/")
async def get_addressbooks_user(username: str) -> List[Book]:
    return app.state.session.books(app.state.account, username)


@app.post("/book/")
async def post_address_book(request: AddBookRequest) -> Book:
    return app.state.session.add_book(app.state.account, request)


@app.delete("/book/")
async def delete_book(request: DeleteBookRequest) -> Dict[str, str]:
    return app.state.session.delete_book(app.state.account, request)
