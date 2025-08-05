from operator import contains
import re
from fastapi import Depends, FastAPI, Response, status, HTTPException
from fastapi.params import Body
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from sqlalchemy.orm import Session
from . import models, schemas, utils
from .database import engine, get_db
from .routers import post, user, auth, vote

models.Base.metadata.create_all(bind=engine)


app = FastAPI(title="My First FastAPI App",
              description="This is my first FastAPI app, I am learning fastapi and I am enjoying it", version="0.0.1")


@app.get("/")
def root():
    return {"message": "Welcome to my first FastAPI app, I am learning fastapi and I am enjoying it"}

app.include_router(user.router)
app.include_router(post.router)
app.include_router(auth.router)
app.include_router(vote.router)



