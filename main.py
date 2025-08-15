from fastapi import FastAPI
import models
from database import Engine, Base
from routers import auth, users, expenses

app = FastAPI(title='Expense Tracker API')

models.Base.metadata.create_all(bind=Engine)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(expenses.router)