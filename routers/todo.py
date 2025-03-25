from fastapi import APIRouter, Depends, Path, HTTPException, Request
from pydantic import BaseModel, Field
from starlette import status
from starlette.responses import RedirectResponse
from models import Base, Todo
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from typing import Annotated
from routers.auth import get_current_user
from fastapi.templating import Jinja2Templates


# router'ımızı buraya import ettik ve şimdi kullanabileceğiz.
from routers.auth import router as auth_router

router = APIRouter(
    prefix="/todo", # path başına isim ekler
    tags=["todo"], # isim olarak belirtir
)

templates = Jinja2Templates(directory="templates")

#bir request sınıfı oluşturmamız gerekiyor body olarak post için
class TodoRequest(BaseModel):
    title:str = Field(min_length=3)
    description : str=Field(min_length=3,max_length=200)
    priority :int =Field(gt=0,lt=6)
    complete:bool


# diğer fonksiyonların bağlı olduğu, database ile session vasıtasıyla bağlantı kuran fonksiyon
def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

# annotated ile bağımlı değişkenimizi gösterme biçimini her seferinde yapmamak için bir değişkene atadık
db_dependency = Annotated[Session,Depends(get_db)]
# kullanıcının tokenını decode ettiğimiz fonksiyondan depend etmeliyiz
user_dependency = Annotated[dict,Depends(get_current_user)]

def redirect_to_login():
    redirect_response = RedirectResponse(url="/auth/login-page",status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie('access_token')
    return redirect_response


# ------------------------------------------------------------------------------------------------------------------
#token kontrolü yapıp ona göre todoları gösteren sayfa
@router.get("/todo-page")
async def render_todo_page(request:Request, db:db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()
        todos = db.query(Todo).filter(Todo.owner_id == user.get('id')).all()
        return templates.TemplateResponse("todo.html",{"request":request, "todos":todos,"user":user})
    except:
        return redirect_to_login()

@router.get("/add-todo-page")
async def render_add_todo_page(request:Request):
    try:
        user = await get_current_user(request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()
        return templates.TemplateResponse("add-todo.html",{"request":request,"user":user})
    except:
        return redirect_to_login()

@router.get("/edit-todo-page/{todo_id}")
async def render_todo_page(request:Request,todo_id:int,db:db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()
        todo = db.query(Todo).filter(Todo.id == todo_id).first()
        return templates.TemplateResponse("edit-todo.html",{"request":request,"todo":todo,"user":user})
    except:
        return redirect_to_login()
# ------------------------------------------------------------------------------------------------------------------

@router.get("/")
async def read_all(user:user_dependency, db: db_dependency): # user ve dbyi depend ettik
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return db.query(Todo).filter(Todo.owner_id == user.get('id')).all()

@router.get("/todo/{todo_id}",status_code=status.HTTP_200_OK)
async def read_by_id(user:user_dependency, db:db_dependency, todo_id :int=Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    todo = db.query(Todo).filter(Todo.id == todo_id).filter(Todo.owner_id==user.get('id')).first()
    # hem todo id hem de user id üzerinden filtreleme yaptık
    if todo is not None:
        return todo
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="todo not found")

@router.post("/todo",status_code=status.HTTP_200_OK)
async def create_todo(user:user_dependency, db:db_dependency,todo_request:TodoRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    todo=Todo(**todo_request.model_dump(), owner_id = user.get('id')) # classı oluşturuourz. Hepsini tek tek söylemek yerine, ** ve request body
    #i verdiğimizde yetiyor.
    db.add(todo)
    db.commit()

@router.put("/todo/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user:user_dependency, db:db_dependency,todo_request:TodoRequest,todo_id:int = Path(gt=0)):

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    todo=db.query(Todo).filter(Todo.id==todo_id).filter(Todo.owner_id==user.get('id')).first()
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    todo.title=todo_request.title
    todo.description=todo_request.description
    todo.priority=todo_request.priority
    todo.complete=todo_request.complete

    db.add(todo)
    db.commit()

"""
@app.delete("/delete_todo/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db:db_dependency,todo_id:int = Path(gt=0)):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='todo not found')
    #db.query(Todo).filter(Todo.id == todo_id).delete() # piyasada bazen deleteden emin olmak için kontrol 2 kez yapılır
    db.delete(todo)
    db.commit()
"""

@router.delete("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def delete_todo(user:user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    todo = db.query(Todo).filter(Todo.id == todo_id).filter(Todo.owner_id == user.get('id')).first()
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

    db.delete(todo)
    db.commit()

    return {"message": "Todo successfully deleted"}