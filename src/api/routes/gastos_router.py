from fastapi import APIRouter
from src.services.gastos_service import gastos_service

router = APIRouter()


@router.post("/gastos")
async def calcular_gastos():
    """
    Endpoint sencillo para gastos
    """
    return {"message": "ok, funciona :)"}
