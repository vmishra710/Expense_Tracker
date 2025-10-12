from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import models
from database import Engine
from routers import auth, users, expenses
from middlewares.middleware import log_requests
from middlewares.custom_header import add_process_time_header


app = FastAPI(title='Expense Tracker API')

models.Base.metadata.create_all(bind=Engine)

@app.get('/', include_in_schema=False)
def root():
    return RedirectResponse(url='/docs')

app.middleware("http")(log_requests)
app.middleware("http")(add_process_time_header)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(expenses.router)
