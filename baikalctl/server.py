import logging
from typing import Annotated

from fastapi import FastAPI, Form
from pydantic import BaseModel

from .client import baikal

app = FastAPI()

logger = logging.getLogger("uvicorn")


class User(BaseModel):
    username: str
    displayname: str
    password: str


class AddressBook(BaseModel):
    username: str
    bookname: str
    description: str


@app.on_event("startup")
def startup_event():
    logger.info(baikal.header)


@app.get("/status/")
def get_status():
    return baikal.status()


@app.post("/reset/")
def post_reset():
    return baikal.reset()


@app.get("/users/")
def get_users():
    return baikal.list_users()


@app.post("/user/")
def post_user(user: Annotated[User, Form()]):
    return baikal.add_user(user.username, user.displayname, user.password)


@app.delete("/user/{username}/")
def delete_user(username: str):
    return baikal.delete_user(username)


@app.get("/addressbooks/{username}/")
def get_addressbooks(username: str):
    return baikal.list_address_books(username)


@app.post("/addressbook/")
def post_address_book(book: Annotated[AddressBook, Form()]):
    return baikal.add_address_book(book.username, book.bookname, book.description)


@app.delete("/addressbook/{username}/{bookname}/")
def delete_addressbooks(username: str, bookname: str):
    return baikal.delete_address_book(username, bookname)
