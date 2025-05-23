from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import json

from src.services.expuestos_mes_service import expuestos_mes_service
from src.models.schemas.expuestos_mes_schema import (
    ProyeccionActuarialInput,
    ProyeccionActuarialOutput
)


router = APIRouter()


@router.post("/proyeccion")
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

        # Calcular meses_proyeccion automáticamente si no se proporciona
        meses_proyeccion = datos.meses_proyeccion
        if meses_proyeccion is None:
            meses_proyeccion = datos.periodo_vigencia * 12
            # Asegurar que no exceda el límite máximo
            meses_proyeccion = min(meses_proyeccion, 600)

        # Llamar al servicio
        resultado = expuestos_mes_service.calcular_proyeccion(
            edad_actuarial=datos.edad_actuarial,
            sexo=datos.sexo.value,
            fumador=datos.fumador,
            frecuencia_pago_primas=datos.frecuencia_pago_primas.value,
            periodo_vigencia=datos.periodo_vigencia,
            periodo_pago_primas=datos.periodo_pago_primas,
            ajuste_mortalidad=datos.ajuste_mortalidad,
            meses_proyeccion=meses_proyeccion,
        )

        # Validar con el modelo Pydantic
        resultado_validado = ProyeccionActuarialOutput(**resultado)

        # Devolver como JSON formateado
        return JSONResponse(
            content=json.loads(resultado_validado.model_dump_json(indent=2)),
            status_code=200,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al calcular proyección actuarial: {str(e)}"
        )
