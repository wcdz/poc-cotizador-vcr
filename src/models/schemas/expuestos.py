from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import date


class ExpuestoMensualData(BaseModel):
    """Modelo Pydantic para datos de entrada de un expuesto mensual"""
    fecha: str = Field(..., description="Fecha en formato YYYY-MM-DD")
    cantidad: int = Field(..., gt=0, description="Cantidad de expuestos")
    monto: float = Field(..., gt=0, description="Monto total expuesto")


class ConfiguracionExpuestos(BaseModel):
    """Configuración para cálculos de expuestos"""
    factor_crecimiento: float = Field(0.0, description="Factor de crecimiento mensual")
    factor_inflacion: float = Field(0.0, description="Factor de inflación mensual")


class ExpuestosInput(BaseModel):
    """Modelo Pydantic para datos de entrada de expuestos"""
    fecha_inicio: str = Field(..., description="Fecha de inicio en formato YYYY-MM-DD")
    fecha_fin: str = Field(..., description="Fecha de fin en formato YYYY-MM-DD")
    configuracion: Optional[ConfiguracionExpuestos] = Field(
        default_factory=ConfiguracionExpuestos,
        description="Configuración para cálculos"
    )
    datos_historicos: List[ExpuestoMensualData] = Field(
        ..., min_items=1, description="Datos históricos de expuestos mensuales"
    )


class ProyeccionInput(BaseModel):
    """Modelo Pydantic para solicitar una proyección"""
    datos_expuestos: ExpuestosInput
    meses_proyeccion: int = Field(..., gt=0, le=60, description="Meses a proyectar")


class ExpuestoMensualOutput(BaseModel):
    """Modelo Pydantic para datos de salida de un expuesto mensual"""
    cantidad: int
    monto: float
    monto_ajustado: float


class TotalesOutput(BaseModel):
    """Modelo Pydantic para totales de expuestos"""
    cantidad_total: int
    monto_total: float
    monto_ajustado_total: float


class ExpuestosOutput(BaseModel):
    """Modelo Pydantic para datos de salida de expuestos"""
    expuestos_por_mes: Dict[str, ExpuestoMensualOutput]
    totales: TotalesOutput


class ProyeccionOutput(BaseModel):
    """Modelo Pydantic para resultado de proyección"""
    historicos: Dict[str, ExpuestoMensualOutput]
    proyectados: Dict[str, ExpuestoMensualOutput]
    totales: TotalesOutput 