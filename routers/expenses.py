from fastapi import APIRouter

router = APIRouter(
    prefix='/expenses',
    tags=['expenses']
)