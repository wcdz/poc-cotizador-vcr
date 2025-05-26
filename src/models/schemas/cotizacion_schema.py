from pydantic import BaseModel, Field
from typing import Literal, Optional, Union
from enum import Enum
from src.core.constans import (
    EDAD_MINIMA_PARTICIPACION,
    EDAD_MAXIMA_PERMANENCIA,
    MINIMO_PERIODO_PAGO_PRIMAS,
    MINIMO_PERIODO_VIGENCIA,
    MINIMO_SUMAS_ASEGURADAS,
    MINIMO_PORCENTAJE_DEVOLUCION,
    MINIMO_PRIMA,
)
from src.models.schemas.expuestos_mes_schema import ProyeccionActuarialOutput


class Moneda(str, Enum):
    PEN = "PEN"
    USD = "USD"


class Sexo(str, Enum):
    MASCULINO = "M"
    FEMENINO = "F"


class FrecuenciaPago(str, Enum):
    ANUAL = "ANUAL"
    SEMESTRAL = "SEMESTRAL"
    TRIMESTRAL = "TRIMESTRAL"
    MENSUAL = "MENSUAL"


class TipoProducto(str, Enum):
    RUMBO = "RUMBO"
    ENDOSOS = "ENDOSOS"


# Parámetros base compartidos entre productos
class ParametrosBase(BaseModel):
    # ... : Es un campo obligatorio y debera de colocar el usuario el valor
    # ge: greater than or equal to value, debe ser mayor o igual a 18
    # le: less than or equal to value, debe ser menor o igual a 80
    edad_actuarial: int = Field(
        ...,
        ge=EDAD_MINIMA_PARTICIPACION,
        le=EDAD_MAXIMA_PERMANENCIA,
        description="Edad actuarial del asegurado",
    )
    moneda: Moneda
    periodo_vigencia: int = Field(
        ..., ge=MINIMO_PERIODO_VIGENCIA, description="Periodo de vigencia en años"
    )
    periodo_pago_primas: int = Field(
        ...,
        ge=MINIMO_PERIODO_PAGO_PRIMAS,
        description="Periodo de pago de primas en años",
    )
    suma_asegurada: float = Field(
        ..., gt=MINIMO_SUMAS_ASEGURADAS, description="Suma asegurada"
    )
    sexo: Sexo
    frecuencia_pago_primas: FrecuenciaPago
    fumador: bool = Field(..., description="Indica si el asegurado es fumador")


# Parámetros específicos para RUMBO
class ParametrosRumbo(ParametrosBase):
    prima: float = Field(..., gt=MINIMO_PRIMA, description="Prima a pagar")


# Parámetros específicos para ENDOSOS
class ParametrosEndosos(ParametrosBase):
    porcentaje_devolucion: float = Field(
        ..., gt=MINIMO_PORCENTAJE_DEVOLUCION, description="Porcentaje de devolución"
    )


# Entrada unificada que maneja ambos tipos de productos
class CotizacionInput(BaseModel):
    producto: TipoProducto
    parametros: Union[ParametrosRumbo, ParametrosEndosos]

    # Validador para asegurar que los parámetros correspondan al producto
    def validate_product_parameters(self):
        if self.producto == TipoProducto.RUMBO and not isinstance(
            self.parametros, ParametrosRumbo
        ):
            raise ValueError(
                "Para el producto RUMBO, se deben proporcionar parámetros de tipo ParametrosRumbo"
            )
        elif self.producto == TipoProducto.ENDOSOS and not isinstance(
            self.parametros, ParametrosEndosos
        ):
            raise ValueError(
                "Para el producto ENDOSOS, se deben proporcionar parámetros de tipo ParametrosEndosos"
            )
        return True


class ParametrosAlmacenados(BaseModel):
    gasto_adquisicion: float
    gasto_mantenimiento: float
    tir: float
    moce: float
    inflacion_anual: float
    margen_solvencia: float
    fondo_garantia: float
    ajuste_mortalidad: float


class ParametrosCalculados(BaseModel):
    adquisicion_fijo_poliza: float
    mantenimiento_poliza: float
    tir_mensual: float
    inflacion_mensual: float
    reserva: float
    tasa_interes_anual: float
    tasa_interes_mensual: float
    tasa_inversion: float


# Salida común para todos los productos
class CotizacionOutput(BaseModel):
    producto: TipoProducto
    parametros_entrada: Union[ParametrosRumbo, ParametrosEndosos]
    parametros_almacenados: ParametrosAlmacenados
    parametros_calculados: ParametrosCalculados
    expuestos_mes: ProyeccionActuarialOutput

    # Campos opcionales específicos para cada producto
    porcentaje_devolucion: Optional[str] = None  # Para RUMBO
    prima: Optional[str] = None  # Para ENDOSOS
