from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from sqlalchemy import text
import models
from database import Engine
from dependencies import async_db_dependency
from middlewares.rate_limiter import rate_limiter
from routers import auth, users, expenses, admin, reports
from middlewares.middleware import log_requests
from middlewares.custom_header import add_process_time_header


app = FastAPI(title='Expense Tracker API')

models.Base.metadata.create_all(bind=Engine)

@app.get('/', include_in_schema=False)
def root():
    return RedirectResponse(url='/docs')

@app.get("/ping-db")
async def ping_db(db: async_db_dependency):
    result = await db.execute(text("SELECT 1"))
    return {"db_response": result.scalar_one()}

app.middleware("http")(rate_limiter)
app.middleware("http")(log_requests)
app.middleware("http")(add_process_time_header)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(expenses.router)
app.include_router(admin.router)
app.include_router(reports.router)
