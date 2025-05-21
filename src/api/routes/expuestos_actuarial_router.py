from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import json
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from enum import Enum

from src.services.expuestos_actuarial_service import expuestos_actuarial_service


class SexoEnum(str, Enum):
    MASCULINO = "M"
    FEMENINO = "F"


class FrecuenciaPagoEnum(str, Enum):
    ANUAL = "ANUAL"
    SEMESTRAL = "SEMESTRAL"
    TRIMESTRAL = "TRIMESTRAL"
    MENSUAL = "MENSUAL"


class ProyeccionActuarialInput(BaseModel):
    edad_actuarial: int = Field(..., ge=18, le=70, description="Edad actuarial del asegurado")
    sexo: SexoEnum = Field(..., description="Sexo del asegurado (M/F)")
    fumador: bool = Field(..., description="Si el asegurado es fumador o no")
    frecuencia_pago_primas: FrecuenciaPagoEnum = Field(..., description="Frecuencia de pago de primas")
    periodo_vigencia: int = Field(..., ge=1, le=50, description="Período de vigencia en años")
    periodo_pago_primas: int = Field(..., ge=1, le=50, description="Período de pago de primas en años")
    meses_proyeccion: Optional[int] = Field(None, ge=1, le=600, description="Número de meses a proyectar (opcional, por defecto se calcula como periodo_vigencia * 12)")
    ajuste_mortalidad: float = Field(1.0, gt=0, description="Factor de ajuste para la tabla de mortalidad")


class ResultadoMensualOutput(BaseModel):
    mes: int
    anio_poliza: int
    edad_actual: int
    vivos_inicio: float
    fallecidos: float
    vivos_despues_fallecidos: float
    caducados: float
    vivos_final: float
    mortalidad_anual: float
    mortalidad_mensual: float
    mortalidad_ajustada: float
    tasa_caducidad: float


class ResumenAnioOutput(BaseModel):
    fallecidos: float
    caducados: float
    vivos_final: float


class ResumenOutput(BaseModel):
    vivos_inicial: float
    vivos_final: float
    fallecidos_total: float
    caducados_total: float
    meses_calculados: int
    por_anio: Dict[str, ResumenAnioOutput]


class ProyeccionActuarialOutput(BaseModel):
    resultados_mensuales: List[ResultadoMensualOutput]
    resumen: ResumenOutput


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
                detail="El período de pago no puede ser mayor al período de vigencia"
            )
        
        # Calcular meses_proyeccion automáticamente si no se proporciona
        meses_proyeccion = datos.meses_proyeccion
        if meses_proyeccion is None:
            meses_proyeccion = datos.periodo_vigencia * 12
            # Asegurar que no exceda el límite máximo
            meses_proyeccion = min(meses_proyeccion, 600)
        
        # Llamar al servicio
        resultado = expuestos_actuarial_service.calcular_proyeccion(
            edad_actuarial=datos.edad_actuarial,
            sexo=datos.sexo.value,
            fumador=datos.fumador,
            frecuencia_pago_primas=datos.frecuencia_pago_primas.value,
            periodo_vigencia=datos.periodo_vigencia,
            periodo_pago_primas=datos.periodo_pago_primas,
            meses_proyeccion=meses_proyeccion,
            ajuste_mortalidad=datos.ajuste_mortalidad
        )
        
        # Validar con el modelo Pydantic
        resultado_validado = ProyeccionActuarialOutput(**resultado)
        
        # Devolver como JSON formateado
        return JSONResponse(
            content=json.loads(resultado_validado.model_dump_json(indent=2)),
            status_code=200
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error al calcular proyección actuarial: {str(e)}"
        ) 