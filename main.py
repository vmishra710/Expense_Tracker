from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import models
from database import Engine, Base
from routers import auth, users, expenses

app = FastAPI(title='Expense Tracker API')

models.Base.metadata.create_all(bind=Engine)

@app.get('/', include_in_schema=False)
def root():
    return RedirectResponse(url='/docs')

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(expenses.router)
