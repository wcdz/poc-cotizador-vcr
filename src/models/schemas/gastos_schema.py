from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from src.common.frecuencia_pago import FrecuenciaPago
from src.common.moneda import Moneda

class GastosInput(BaseModel):
    """
    Modelo de entrada para cálculo de gastos
    """

    periodo_vigencia: int = Field(..., description="Periodo de vigencia en años")
    periodo_pago_primas: int = Field(
        ..., description="Periodo de pago de primas en años"
    )
    moneda: Moneda = Field(..., description="Moneda (SOLES o DOLARES)")
    frecuencia_pago_primas: FrecuenciaPago = Field(
        ..., description="Frecuencia de pago de primas"
    )
    prima: float = Field(..., description="Prima del seguro")

    class Config:
        json_schema_extra = {
            "example": {
                "periodo_vigencia": 20,
                "periodo_pago_primas": 10,
                "moneda": "SOLES",
                "frecuencia_pago_primas": "ANUAL",
                "prima": 1000.0,
            }
        }


class ResultadoMensualGastos(BaseModel):
    """
    Resultado mensual del cálculo de gastos
    """

    mes: int
    anio_poliza: int
    gasto_mantenimiento_prima_co: str
    gastos_mantenimiento_moneda_poliza: str
    gasto_mantenimiento_fijo_poliza_anual: str
    factor_inflacion: str
    gasto_mantenimiento_total: str


class Gastos(BaseModel):
    """
    Modelo de salida para gastos
    """

    resultados_mensuales: List[ResultadoMensualGastos]
