from fastapi import FastAPI

from routers import student as student_router
from configs.database import Base, engine
from routers import authentication as auth_router

app = FastAPI()

app.include_router(student_router.router)
app.include_router(auth_router.router)

Base.metadata.create_all(bind=engine)