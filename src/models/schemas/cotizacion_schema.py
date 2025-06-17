from pydantic import BaseModel, Field
from typing import Literal, Optional, Union
from enum import Enum
from src.core.constants import (
    EDAD_MINIMA_PARTICIPACION,
    EDAD_MAXIMA_PERMANENCIA,
    MINIMO_PERIODO_PAGO_PRIMAS,
    MINIMO_PERIODO_VIGENCIA,
    MINIMO_SUMAS_ASEGURADAS,
    MINIMO_PORCENTAJE_DEVOLUCION,
    MINIMO_PRIMA,
)
from src.models.schemas.expuestos_mes_schema import ProyeccionActuarialOutput
from src.models.schemas.gastos_schema import Gastos
from src.common.moneda import Moneda
from src.common.frecuencia_pago import FrecuenciaPago
from src.common.sexo import Sexo
from src.common.tipo_producto import TipoProducto
from src.models.schemas.flujo_resultado_schema import FlujoResultado


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
    moneda: Optional[Moneda] = Field(
        default=Moneda.SOLES, description="Moneda de la poliza"
    )
    periodo_vigencia: int = Field(
        ..., ge=MINIMO_PERIODO_VIGENCIA, description="Periodo de vigencia en años"
    )
    periodo_pago_primas: int = Field(
        ...,
        ge=MINIMO_PERIODO_PAGO_PRIMAS,
        description="Periodo de pago de primas en años",
    )
    suma_asegurada: Optional[float] = Field(
        default=0.01, gt=MINIMO_SUMAS_ASEGURADAS, description="Suma asegurada"
    )
    sexo: Sexo
    frecuencia_pago_primas: Optional[FrecuenciaPago] = Field(
        default=FrecuenciaPago.MENSUAL, description="Frecuencia de pago de primas"
    )
    fumador: Optional[bool] = Field(
        default=False, description="Indica si el asegurado es fumador"
    )
    # asistencia: Optional[bool] = Field(..., description="Indica si el asegurado tiene asistencia")
    porcentaje_devolucion: Optional[float] = Field(
        default=100, gt=MINIMO_PORCENTAJE_DEVOLUCION, description="Porcentaje de devolución"
    )


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
    moneda: str
    valor_dolar: float
    valor_soles: float
    tiene_asistencia: bool
    costo_mensual_asistencia_funeraria: float
    moneda_poliza: float
    fraccionamiento_primas: float
    comision: float
    costo_asistencia_funeraria: float
    impuesto_renta: float
    suma_asegurada_rumbo: float


class ParametrosCalculados(BaseModel):
    adquisicion_fijo_poliza: float
    mantenimiento_poliza: float
    tasa_costo_capital_mensual: float
    inflacion_mensual: float
    reserva: float
    tasa_interes_anual: float
    tasa_interes_mensual: float
    tasa_inversion: float
    tasa_costo_capital_mes: float
    factor_pago: float
    prima_para_redondeo: float
    tasa_frecuencia_seleccionada: float


# Salida común para todos los productos
class CotizacionOutput(BaseModel):
    producto: TipoProducto
    parametros_entrada: Union[ParametrosRumbo, ParametrosEndosos]
    parametros_almacenados: ParametrosAlmacenados
    parametros_calculados: ParametrosCalculados
    # expuestos_mes: ProyeccionActuarialOutput
    # gastos: Gastos
    # flujo_resultado: FlujoResultado
    # Campos opcionales específicos para cada producto
    # porcentaje_devolucion: Optional[str] = None  # Para RUMBO
    # prima: Optional[str] = None  # Para ENDOSOS
    rumbo: Optional[dict] = None  # Para RUMBO con porcentaje_devolucion y trea
    endosos: Optional[dict] = None  # Para ENDOSOS con porcentaje_devolucion y trea
