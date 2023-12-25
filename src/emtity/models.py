import enum

from sqlalchemy import Column, String, Integer, Date, ForeignKey, DateTime, func
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class Contact(Base):
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    phone_number = Column(String)
    birthday = Column(Date)
    created_at = Column('created_at', DateTime, default=func.now(), nullable=True)
    updated_at = Column('updated_at', DateTime, default=func.now(), onupdate=func.now(), nullable=True)
    additional_data = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    user = relationship("User", backref="contacts", lazy='joined')


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50))
    email = Column(String(150), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    refresh_token = Column(String(255), nullable=True)
    created_at = Column('created_at', DateTime, default=func.now())
    updated_at = Column('updated_at', DateTime, default=func.now(), onupdate=func.now())
    contacts = relationship("Contact", backref="user")


