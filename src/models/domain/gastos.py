from dataclasses import dataclass
from src.models.domain.expuestos_mes import ExpuestosMes
from src.models.domain.parametros_calculados import ParametrosCalculados
from src.common.frecuencia_pago import FrecuenciaPago


@dataclass
class Gastos:
    """
    Modelo de dominio para los gastos.
    """

    # Atributos de entrada desde endpoint o cotizadorService
    periodo_vigencia: int

    # Atributos calculados
    mantenimiento_poliza: float  # viene desde parametros_calculados
    inflacion_mensual: float  # viene desde parametros_calculados

    # Atributos almacenados
    moneda: str
    valor_dolar: float
    valor_soles: float
    tiene_asistencia: bool  # Entendemos que no se usa
    costo_mensual_asistencia_funeraria: float  # Entendemos que no se usa
    moneda_poliza: float  # constante para todo los meses

    # Atributos para flujo y resultado
    periodo_pago_primas: int
    frecuencia_pago_primas: FrecuenciaPago  # Usar la enumeración
    prima: float
    expuestos_mes: ExpuestosMes  # (vivos_inicio)
