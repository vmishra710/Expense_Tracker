import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


SQLALCHEMY_DATABASE_URL =os.getenv(
    "DATABASE_URL", #Render will inject this
    "postgresql://postgres:Admin%401234@localhost/ExpenseTrackerDatabase" #local fallback
)

if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)


# SQLALCHEMY_DATABASE_URL = 'sqlite:///./exp_tracker.db'
# Engine = create_engine(SQLALCHEMY_DATABASE_URL,  connect_args={'check_same_thread':False})

Engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=Engine)

Base = declarative_base()