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
    AJUSTE_MORTALIDAD_POR_DEFECTO,
)
from src.common.sexo import Sexo
from src.common.frecuencia_pago import FrecuenciaPago


class ProyeccionActuarialInput(BaseModel):
    edad_actuarial: int = Field(
        ...,
        ge=EDAD_MINIMA_PARTICIPACION,
        le=EDAD_MAXIMA_PERMANENCIA,
        description="Edad actuarial del asegurado",
    )
    sexo: Sexo = Field(..., description="Sexo del asegurado (M/F)")
    fumador: bool = Field(..., description="Si el asegurado es fumador o no")
    frecuencia_pago_primas: FrecuenciaPago = Field(
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
    ajuste_mortalidad: float = Field(
        AJUSTE_MORTALIDAD_POR_DEFECTO,
        gt=0,
        description="Factor de ajuste para la tabla de mortalidad",
    )


class ResultadoMensualOutput(BaseModel):
    mes: int
    anio_poliza: int
    edad_actual: int
    vivos_inicio: str
    fallecidos: str
    vivos_despues_fallecidos: str
    caducados: str
    vivos_final: str
    mortalidad_anual: str
    mortalidad_mensual: str
    mortalidad_ajustada: str
    tasa_caducidad: str


class ResumenAnioOutput(BaseModel):
    fallecidos: str
    caducados: str
    vivos_final: str


class ResumenOutput(BaseModel):
    vivos_inicial: str
    vivos_final: str
    fallecidos_total: str
    caducados_total: str
    meses_calculados: int
    por_anio: Dict[str, ResumenAnioOutput]


class ProyeccionActuarialOutput(BaseModel):
    resultados_mensuales: List[ResultadoMensualOutput]
    resumen: ResumenOutput
