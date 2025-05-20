from pydantic import BaseModel, Field
from typing import Literal, Optional, Union
from enum import Enum


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
        ..., ge=18, le=80, description="Edad actuarial del asegurado"
    )
    moneda: Moneda
    periodo_vigencia: int = Field(..., ge=1, description="Periodo de vigencia en años")
    periodo_pago_primas: int = Field(
        ..., ge=1, description="Periodo de pago de primas en años"
    )
    suma_asegurada: float = Field(..., gt=0, description="Suma asegurada")
    sexo: Sexo
    frecuencia_pago_primas: FrecuenciaPago


# Parámetros específicos para RUMBO
class ParametrosRumbo(ParametrosBase):
    prima: float = Field(..., gt=0, description="Prima a pagar")


# Parámetros específicos para ENDOSOS
class ParametrosEndosos(ParametrosBase):
    porcentaje_devolucion: float = Field(
        ..., gt=0, description="Porcentaje de devolución"
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
    gastos_adquisicion: float
    gastos_mantenimiento: float
    tir: float
    moce: float
    inflacion_anual: float
    margen_solvencia: float
    fondo_garantia: float


class ParametrosCalculados(BaseModel):
    adquisicion_fijo_poliza: float
    mantenimiento_poliza: float
    tir_mensual: float
    reserva: float
    tasa_interes_anual: float
    tasa_interes_mensual: float
    tasa_inversion: float
    tasa_reserva: float


# Salida común para todos los productos
class CotizacionOutput(BaseModel):
    producto: TipoProducto
    parametros_entrada: Union[ParametrosRumbo, ParametrosEndosos]
    parametros_almacenados: ParametrosAlmacenados
    parametros_calculados: ParametrosCalculados

    # Campos opcionales específicos para cada producto
    porcentaje_devolucion: Optional[str] = None  # Para RUMBO
    prima: Optional[str] = None  # Para ENDOSOS
