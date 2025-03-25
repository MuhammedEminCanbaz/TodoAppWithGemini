from passlib.context import CryptContext
from fastapi import APIRouter, Depends, HTTPException, Request

# farklı işlemleri farklı yerlerde yapmak için apiden sürekli farklı instance'lar oluşturmak yerine
# router yapısı kullanılır, farklı dağılımlar yapmış oluruz.

from pydantic import BaseModel
from typing import Annotated
from starlette import status
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer #kullanıcıdan username ve pasword almak
from jose import jwt,JWTError # jwt ile token oluşturmak için kullanıldı
from datetime import timedelta, datetime, timezone
from fastapi.templating import Jinja2Templates

# router vasıtası ile api'den bir yol çıkarmış oluyoruz.
router = APIRouter(
    prefix="/auth", # path başına isim ekler
    tags=["Authentication"], # tag olarak belirtir
)
#template klasörünü tanıtmak için yazdık
templates = Jinja2Templates(directory="templates")

SECRET_KEY = "psjqywıel123udkcmxn7803u4tx7bn19psjqywıel123udkcmxn7803u4tx7bn19"
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=["bcrypt"],deprecated="auto") # bcrypt algoritması ile şifreleyeceğiz.
oauth2bearer= OAuth2PasswordBearer(tokenUrl="/auth/token")

# diğer fonksiyonların bağlı olduğu, database ile session vasıtasıyla bağlantı kuran fonksiyon
def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        #session'u kapatmalıyız.
        db.close()

# annotated ile bağımlı değişkenimizi gösterme biçimini her seferinde yapmamak için bir değişkene atadık, veri tipimiz de session
db_dependency = Annotated[Session,Depends(get_db)]

# client yeni bir kullanıcı oluşturmak için veriyi nasıl vericek, bunun temelini atıyoruz.
class CreateUserRequest(BaseModel):
    username : str
    email : str
    first_name : str
    last_name : str
    password : str
    role : str
    phone_number :str

class Token(BaseModel):
    access_token :str
    token_type : str

#jwt ile token oluşturmak için gerekli fonksiyon
def create_acces_token(username:str,user_id:int,role:str,expires_delta:timedelta):
    payload = {"sub":username,"id":user_id,"role":role}
    expires = datetime.now(timezone.utc) + expires_delta
    payload.update({"exp":expires})
    return jwt.encode(payload,SECRET_KEY,algorithm=ALGORITHM)


# kullanıcının girdiği değerlerin uyuşup uyuşmadını kontrol eden fonksiyon
def authenticate_user(username: str, pasword:str, db):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(pasword, user.hashed_password): # yeni girilenle hashli olanı kontrol ediyoruz.
        return False
    return user

async def get_current_user(token:Annotated[str,Depends(oauth2bearer)]):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        username = payload.get("sub")
        user_id = payload.get("id")
        user_role = payload.get("role")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="username or ID is invalid")
        return {"username":username,"id":user_id,"user_role":user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="token is invalid")

@router.get("/login-page")
def render_login_page(request:Request):
    return templates.TemplateResponse("login.html",{"request":request})

@router.get("/register-page")
def render_register_page(request:Request):
    return templates.TemplateResponse("register.html",{"request":request})


@router.post("/",status_code=status.HTTP_201_CREATED)
async def create_user(db:db_dependency, create_user_request : CreateUserRequest): # oluşturduğumuz temeli depends olarak alıyoruz.
    user = User(
        username = create_user_request.username,
        email = create_user_request.email,
        first_name = create_user_request.first_name,
        last_name = create_user_request.last_name,
        role = create_user_request.role,
        is_active = True,
        hashed_password = bcrypt_context.hash(create_user_request.password), # şifreleme algoritması ile şifreledik
        phone_number = create_user_request.phone_number
    ) # models içindeki User sınıfından bir instance oluşturuyoruz.
    db.add(user)
    db.commit()

# kullanıcıya bir token verilir ve bu metin üzerinden kendi görmesi gerekenleri görür.
@router.post("/token", response_model=Token )
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm,Depends()],
                                 db:db_dependency):
    user = authenticate_user(form_data.username,form_data.password,db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="incorrect username or pasword")
    token = create_acces_token(user.username,user.id,user.role,timedelta(minutes=60))
    return {"access_token":token,"token_type":"bearer"}