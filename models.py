import datetime
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy import Column, Integer, String, DateTime, Float, Date, ForeignKey


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))

    expenses = relationship('Expense', back_populates='owner')

class Expense(Base):
    __tablename__ = 'expenses'

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float)
    category = Column(String)
    description = Column(String, nullable=True)
    date = Column(Date, default=datetime.date.today)

    owner_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship('User', back_populates='expenses')