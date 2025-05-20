from fastapi import APIRouter, Depends, HTTPException
from src.models.schemas.cotizacion_schema import (
    CotizacionInput,
    CotizacionOutput,
    TipoProducto,
)
from src.services.cotizacion_service import CotizadorService

router = APIRouter()


def get_cotizador_service():
    """Dependencia para obtener el servicio unificado de cotizaciones"""
    return CotizadorService()


@router.post("/cotizar", response_model=CotizacionOutput)
async def cotizar(
    cotizacion: CotizacionInput,
    service: CotizadorService = Depends(get_cotizador_service),
):
    """
    Cotiza un seguro basado en el producto y parámetros proporcionados.

    El endpoint determina automáticamente el tipo de cotización según el campo 'producto'.

    Productos soportados:
    - RUMBO: Requiere prima
    - ENDOSOS: Requiere porcentaje_devolucion

    Ejemplo para RUMBO:
    ```json
    {
        "producto": "RUMBO",
        "parametros": {
            "edad_actuarial": 23,
            "moneda": "PEN",
            "periodo_vigencia": 12,
            "periodo_pago_primas": 12,
            "suma_asegurada": 200000,
            "sexo": "M",
            "frecuencia_pago_primas": "ANUAL",
            "prima": 10000
        }
    }
    ```

    Ejemplo para ENDOSOS:
    ```json
    {
        "producto": "ENDOSOS",
        "parametros": {
            "edad_actuarial": 23,
            "moneda": "PEN",
            "periodo_vigencia": 12,
            "periodo_pago_primas": 12,
            "suma_asegurada": 200000,
            "sexo": "M",
            "frecuencia_pago_primas": "ANUAL",
            "porcentaje_devolucion": 10000
        }
    }
    ```
    """
    try:
        return service.cotizar(cotizacion)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al procesar la cotización: {str(e)}"
        )
