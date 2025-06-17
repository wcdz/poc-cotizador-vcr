from fastapi import APIRouter, HTTPException, Depends
from src.services.cotizacion import CotizadorService

router = APIRouter()


def get_coleccion_cotizacion():
    return CotizadorService()


@router.post("/coleccion-cotizacion")
async def get_coleccion_cotizacion(
    service: CotizadorService = Depends(get_coleccion_cotizacion),
):
    try:
        return {"message": "ok, funciona :)"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al procesar la cotización: {str(e)}"
        )
