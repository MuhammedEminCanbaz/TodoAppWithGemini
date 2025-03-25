from pickle import FALSE

from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey


class Todo(Base):
    __tablename__ ='todos'

    id = Column(Integer,primary_key=True,index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean,default=False)
    owner_id = Column(Integer,ForeignKey('users.id')) # users adlı tablodaki id değerinden oluşuyor bu kolon

# iki tablo arasında bir ilişki kurmalıyız, kimin todosu kimin diye bakmamız gerekecek
# her iki tabloda da id değerleri unique ve kullanıcıya özel, id ile eşleyceğiz.
# one to many ilişki, bir kişinin birden fazla todosu olabilir, her bir todonun birden çok sahibi olabilir.

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean,default=True)
    role = Column(String)
    phone_number = Column(String)