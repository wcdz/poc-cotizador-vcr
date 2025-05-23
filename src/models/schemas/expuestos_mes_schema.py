from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from enum import Enum
from src.core.constans import (
    PERIODO_VIGENCIA_MAXIMO,
    PERIODO_PAGO_PRIMAS_MAXIMO,
    EDAD_MINIMA_PARTICIPACION,
    EDAD_MAXIMA_PERMANENCIA,
    PERIODO_VIGENCIA_MINIMO,
    PERIODO_PAGO_PRIMAS_MINIMO,
    MESES_PROYECCION_MINIMO,
    MESES_PROYECCION_MAXIMO,
    AJUSTE_MORTALIDAD_POR_DEFECTO,
)


class SexoEnum(str, Enum):
    MASCULINO = "M"
    FEMENINO = "F"


class FrecuenciaPagoEnum(str, Enum):
    ANUAL = "ANUAL"
    SEMESTRAL = "SEMESTRAL"
    TRIMESTRAL = "TRIMESTRAL"
    MENSUAL = "MENSUAL"


class ProyeccionActuarialInput(BaseModel):
    edad_actuarial: int = Field(
        ...,
        ge=EDAD_MINIMA_PARTICIPACION,
        le=EDAD_MAXIMA_PERMANENCIA,
        description="Edad actuarial del asegurado",
    )
    sexo: SexoEnum = Field(..., description="Sexo del asegurado (M/F)")
    fumador: bool = Field(..., description="Si el asegurado es fumador o no")
    frecuencia_pago_primas: FrecuenciaPagoEnum = Field(
        ..., description="Frecuencia de pago de primas"
    )
    periodo_vigencia: int = Field(
        ...,
        ge=PERIODO_VIGENCIA_MINIMO,
        le=PERIODO_VIGENCIA_MAXIMO,
        description="Período de vigencia en años",
    )
    periodo_pago_primas: int = Field(
        ...,
        ge=PERIODO_PAGO_PRIMAS_MINIMO,
        le=PERIODO_PAGO_PRIMAS_MAXIMO,
        description="Período de pago de primas en años",
    )
    meses_proyeccion: Optional[int] = Field(
        None,
        ge=MESES_PROYECCION_MINIMO,
        le=MESES_PROYECCION_MAXIMO,
        description="Número de meses a proyectar (opcional, por defecto se calcula como periodo_vigencia * 12)",
    )
    ajuste_mortalidad: float = Field(
        AJUSTE_MORTALIDAD_POR_DEFECTO,
        gt=0,
        description="Factor de ajuste para la tabla de mortalidad",
    )


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
