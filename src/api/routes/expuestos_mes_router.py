from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import json
from decimal import Decimal

from src.services.expuestos_mes_service import expuestos_mes_service
from src.models.schemas.expuestos_mes_schema import (
    ProyeccionActuarialInput,
    ProyeccionActuarialOutput
)


# Clase personalizada para codificar números sin notación científica
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)


router = APIRouter()


@router.post("/expuestos_mes")
async def calcular_proyeccion_actuarial(datos: ProyeccionActuarialInput):
    """
    Calcula la proyección actuarial de expuestos para un conjunto de parámetros.

    Esta proyección utiliza la tabla de mortalidad y la tabla de caducidad para
    calcular los expuestos a lo largo del tiempo.

    Si no se especifica meses_proyeccion, se calculará automáticamente como
    periodo_vigencia * 12, garantizando que la proyección cubra toda la duración
    del seguro.

    Ejemplo:
    ```json
    {
        "edad_actuarial": 35,
        "sexo": "M",
        "fumador": false,
        "frecuencia_pago_primas": "ANUAL",
        "periodo_vigencia": 20,
        "periodo_pago_primas": 10,
        "ajuste_mortalidad": 1.0
    }
    ```
    """
    try:
        # Validar coherencia de parámetros
        if datos.periodo_pago_primas > datos.periodo_vigencia:
            raise HTTPException(
                status_code=400,
                detail="El período de pago no puede ser mayor al período de vigencia",
            )

        # Llamar al servicio
        resultado = expuestos_mes_service.calcular_proyeccion(
            edad_actuarial=datos.edad_actuarial,
            sexo=datos.sexo.value,
            fumador=datos.fumador,
            frecuencia_pago_primas=datos.frecuencia_pago_primas.value,
            periodo_vigencia=datos.periodo_vigencia,
            periodo_pago_primas=datos.periodo_pago_primas,
            ajuste_mortalidad=datos.ajuste_mortalidad
        )

        # Validar con el modelo Pydantic
        resultado_validado = ProyeccionActuarialOutput(**resultado)

        # Devolver como JSON formateado sin notación científica
        content = json.loads(resultado_validado.model_dump_json(indent=2))
        formatted_json = json.dumps(content, indent=2, cls=CustomJSONEncoder)
        
        return JSONResponse(
            content=json.loads(formatted_json),
            status_code=200,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al calcular proyección actuarial: {str(e)}"
        )
