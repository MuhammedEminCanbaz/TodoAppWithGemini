from fastapi import FastAPI
from models import Base, Todo
from database import engine

# router'ımızı buraya import ettik ve şimdi kullanabileceğiz.
from routers.auth import router as auth_router
from routers.todo import router as todo_router

app = FastAPI()
app.include_router(auth_router) # auth router'ımızı bunun içerisine dahil ettik
app.include_router(todo_router)

Base.metadata.create_all(bind=engine)
