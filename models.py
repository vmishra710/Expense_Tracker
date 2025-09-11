import datetime
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy import Column, Integer, String, DateTime, Float, Date, ForeignKey


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String(50), default='user')  #Admin/User
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc), onupdate=datetime.datetime.now(datetime.timezone.utc))

    #Relationships
    expenses = relationship('Expense', back_populates='owner', cascade="all, delete-orphan")
    categories = relationship('Category', back_populates='owner', cascade="all, delete-orphan")


class Expense(Base):
    __tablename__ = 'expenses'

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    description = Column(String, nullable=True)
    date = Column(Date, default=datetime.date.today)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc),onupdate=datetime.datetime.now(datetime.timezone.utc))
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Relationships
    owner = relationship('User', back_populates='expenses')
    category = relationship('Category', back_populates='expenses')



class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    owner_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc), onupdate=datetime.datetime.now(datetime.timezone.utc))

    #Relationships
    owner = relationship('User', back_populates='categories')
    expenses = relationship('Expense', back_populates='category', cascade="all, delete-orphan")