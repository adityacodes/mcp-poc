import os
from pathlib import Path
from typing import Annotated
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.params import Depends
from sqlmodel import SQLModel, Session, create_engine, select
# ----------------------- DB Setup -----------------------
BASE_DIR: Path = Path(__file__)
sqlite_file_name = f"{BASE_DIR.resolve().parent}/database.db"
engine = create_engine(f"sqlite:///{sqlite_file_name}")

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

def CORS(app: FastAPI):
    BACKEND_CORS_ORIGINS = os.getenv("BACKEND_CORS_ORIGINS", "").split(",")

    if BACKEND_CORS_ORIGINS and BACKEND_CORS_ORIGINS != ['']:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=['*'],
            allow_headers=['*'],
        )
        