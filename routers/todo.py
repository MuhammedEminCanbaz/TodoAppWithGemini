from fastapi import APIRouter, Depends, Path, HTTPException
from pydantic import BaseModel, Field
from starlette import status
from models import Base, Todo
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from typing import Annotated

# router'ımızı buraya import ettik ve şimdi kullanabileceğiz.
from routers.auth import router as auth_router

router = APIRouter(
    prefix="/todo", # path başına isim ekler
    tags=["todo"], # isim olarak belirtir
)

#bir request sınıfı oluşturmamız gerekiyor body olarak post için
class TodoRequest(BaseModel):
    title:str = Field(min_length=3)
    description : str=Field(min_length=3,max_length=200)
    priority :int =Field(gt=0,lt=6)
    completed:bool


# diğer fonksiyonların bağlı olduğu, database ile session vasıtasıyla bağlantı kuran fonksiyon
def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

# annotated ile bağımlı değişkenimizi gösterme biçimini her seferinde yapmamak için bir değişkene atadık
db_dependency = Annotated[Session,Depends(get_db)]

@router.get("/read_all")
async def read_all(db: db_dependency): # dependency'mi böyle rahatça belirttik
    return db.query(Todo).all()

@router.get("/get_by_id/{todo_id}",status_code=status.HTTP_200_OK)
async def read_by_id(db:db_dependency, todo_id :int=Path(gt=0)):
    todo = db.query(Todo).filter(Todo.id == todo_id).first() # bu filtrelemeyi yaptığımız blok, liste döndürdüğü için
    # ilk elemanı almak adına first() yazdık.
    if todo is not None:
        return todo
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="todo not found")

@router.post("/create_todo",status_code=status.HTTP_200_OK)
async def create_todo(db:db_dependency,todo_request:TodoRequest):
    todo=Todo(**todo_request.model_dump()) # classı oluşturuourz. Hepsini tek tek söylemek yerine, ** ve request body
    #i verdiğimizde yetiyor.
    db.add(todo)
    db.commit()

@router.put("/update_todo/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db:db_dependency,todo_request:TodoRequest,todo_id:int = Path(gt=0)):
    todo=db.query(Todo).filter(Todo.id==todo_id).first()
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    todo.title=todo_request.title
    todo.description=todo_request.description
    todo.priority=todo_request.priority
    todo.completed=todo_request.completed

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

@router.delete("/delete_todo/{todo_id}", status_code=status.HTTP_200_OK)
async def delete_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

    db.delete(todo)
    db.commit()

    return {"message": "Todo successfully deleted"}


