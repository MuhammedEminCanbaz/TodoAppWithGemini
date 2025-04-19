from fastapi import FastAPI, Request
from starlette.responses import RedirectResponse
from starlette import status

from .models import Base, Todo
from .database import engine
from fastapi.staticfiles import StaticFiles

# router'ımızı buraya import ettik ve şimdi kullanabileceğiz.
from .routers.auth import router as auth_router
from .routers.todo import router as todo_router
import os

app = FastAPI()

script_dir = os.path.dirname(__file__)
st_abs_file_path = os.path.join(script_dir,"static/")
# static dosyaları entegre edilmesi için gerekli kod bloğu
app.mount("/static", StaticFiles(directory=st_abs_file_path),name="static")

#kullanıcı başlangıçta programı çalıştırdığında nereye gitsin'i belirtiyoruz. Ve burası todo sayfası
@app.get("/")
def read_root(request:Request):
    return RedirectResponse(url="/todo/todo-page",status_code=status.HTTP_302_FOUND)

app.include_router(auth_router) # auth router'ımızı bunun içerisine dahil ettik
app.include_router(todo_router)

Base.metadata.create_all(bind=engine)
