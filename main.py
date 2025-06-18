import os

from dotenv import load_dotenv
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from routers import student as student_router
from configs.database import Base, engine
from routers import authentication as auth_router
load_dotenv()
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_ORIGIN
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(student_router.router)
app.include_router(auth_router.router)

Base.metadata.create_all(bind=engine)