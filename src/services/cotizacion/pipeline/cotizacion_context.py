from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from src.models.schemas.cotizacion_schema import (
    CotizacionInput,
    CotizacionOutput,
    ParametrosAlmacenados,
    ParametrosCalculados,
)


@dataclass
class CotizacionContext:
    """Contexto que contiene todos los datos del pipeline de cotización"""

    # Datos de entrada
    input: CotizacionInput

    # Parámetros
    parametros_almacenados: Optional[ParametrosAlmacenados] = None
    parametros_calculados: Optional[ParametrosCalculados] = None
    tasas_interes_data: Optional[Dict[str, Any]] = None
    factores_pago: Optional[List[float]] = None

    # Datos calculados - Actuariales
    prima: float = 0.0
    suma_asegurada: float = 0.0
    periodo_vigencia: int = 0
    periodo_pago_primas: int = 0
    expuestos_mes: Optional[List[float]] = None
    gastos: Optional[List[float]] = None

    # Datos calculados - Flujos
    primas_recurrentes: Optional[List[float]] = None
    siniestros: Optional[List[float]] = None
    rescate: Optional[List[float]] = None
    rescates_ajuste_devolucion: Optional[List[float]] = None
    gastos_mantenimiento: Optional[List[float]] = None
    gasto_adquisicion: Optional[List[float]] = None
    comision: Optional[List[float]] = None

    # Datos calculados - Reservas
    flujo_pasivo: Optional[List[float]] = None
    saldo_reserva: Optional[List[float]] = None
    moce: Optional[List[float]] = None
    moce_saldo_reserva: Optional[List[float]] = None
    reserva_fin_año: Optional[List[float]] = None
    tabla_devolucion: Optional[str] = None

    # Datos calculados - Márgenes
    margen_solvencia: Optional[List[float]] = None
    varianza_margen_solvencia: Optional[List[float]] = None
    ingreso_inversiones: Optional[List[float]] = None
    ingreso_inversiones_margen_solvencia: Optional[List[float]] = None
    ingreso_total_inversiones: Optional[List[float]] = None

    # Datos calculados - Finales
    varianza_moce: Optional[List[float]] = None
    varianza_reserva: Optional[List[float]] = None
    variacion_reserva: Optional[List[float]] = None
    utilidad_pre_pi_ms: Optional[List[float]] = None
    IR: Optional[List[float]] = None
    flujo_accionista: Optional[List[float]] = None
    auxiliar_vna: Optional[List[float]] = None

    # Datos específicos por producto
    porcentaje_devolucion_optimo: Optional[float] = None
    trea: Optional[float] = None
    aporte_total: Optional[float] = None
    devolucion_total: Optional[float] = None
    ganancia_total: Optional[float] = None
    tabla_devolucion: Optional[str] = None

    # Respuesta final
    output: Optional[CotizacionOutput] = None

    # Metadatos
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    debug_info: Dict[str, Any] = field(default_factory=dict)
