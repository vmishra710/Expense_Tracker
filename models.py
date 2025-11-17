import datetime
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy import Column, Integer, String, DateTime, Float, Date, ForeignKey, UniqueConstraint

def utcnow(Base):
    return datetime.datetime.now(datetime.timezone.utc)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String(50), default='user')  #admin/user
    # created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    # updated_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc), onupdate=datetime.datetime.now(datetime.timezone.utc))

    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    #Relationships
    expenses = relationship('Expense', back_populates='owner', cascade="all, delete-orphan")
    categories = relationship('Category', back_populates='owner', cascade="all, delete-orphan")


class Expense(Base):
    __tablename__ = 'expenses'

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    description = Column(String, nullable=True)
    date = Column(Date, default=datetime.date.today)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow,onupdate=utcnow)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Relationships
    owner = relationship('User', back_populates='expenses')
    category = relationship('Category', back_populates='expenses')



class Category(Base):
    __tablename__ = 'categories'
    __table_args__ = (
        UniqueConstraint('owner_id', 'name', name='uq_user_category'),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    #Relationships
    owner = relationship('User', back_populates='categories')
    expenses = relationship('Expense', back_populates='category', cascade="all, delete-orphan")