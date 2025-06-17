from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from src.services.cotizacion import CotizadorService
from src.models.schemas.cotizacion_schema import CotizacionInput

router = APIRouter()


def get_coleccion_cotizacion():
    return CotizadorService()


@router.post("/coleccion-cotizacion")
async def get_coleccion_cotizacion(
    cotizacion: CotizacionInput,
    service: CotizadorService = Depends(get_coleccion_cotizacion),
):
    """
    🚀 ENDPOINT REFACTORIZADO SIGUIENDO EL PATRÓN STRATEGY
    
    Obtiene una colección de cotizaciones para diferentes períodos.
    Usa validación automática de Pydantic y delega la lógica a las estrategias.
    
    Args:
        cotizacion: Datos de cotización validados automáticamente por Pydantic
        service: Servicio de cotización inyectado
        
    Returns:
        Colección de cotizaciones según el producto especificado
    """
    try:
        return service.get_coleccion_cotizacion(cotizacion)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al procesar la cotización: {str(e)}"
        )
