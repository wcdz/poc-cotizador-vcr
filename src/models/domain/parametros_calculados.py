from dataclasses import dataclass, field
from src.core.constans import TASA_MENSUALIZACION, FACTOR_AJUSTE, FACTOR_RESERVA
from src.helpers.tasa_interes_reserva import tasa_interes_reserva
from src.common.frecuencia_pago import FrecuenciaPago
from typing import Dict


@dataclass
class ParametrosCalculados:
    """
    Modelo de dominio para los parámetros calculados.
    Contiene la lógica de negocio para realizar cálculos basados en parámetros de entrada.
    """

    # Parámetros de entrada
    prima: float
    gasto_adquisicion: float
    gasto_mantenimiento: float
    tasa_costo_capital_tir: float
    moce: float
    inflacion_anual: float
    margen_solvencia: float
    fondo_garantia: float
    periodo_vigencia: int
    tasas_interes_data: dict
    periodo_pago_primas: int
    frecuencia_pago_primas: FrecuenciaPago
    factores_pago: Dict[str, float]
    suma_asegurada: float

    # Constantes desde configuración
    tasa_mensualizacion: float = TASA_MENSUALIZACION
    factor_ajuste: float = FACTOR_AJUSTE
    factor_reserva: float = FACTOR_RESERVA

    # Valores calculados (inicializados en __post_init__)
    adquisicion_fijo_poliza: float = field(init=False)
    mantenimiento_poliza: float = field(init=False)
    tir_mensual: float = field(init=False)
    reserva: float = field(init=False)
    tasa_interes_anual: float = field(init=False)
    tasa_interes_mensual: float = field(init=False)
    tasa_inversion: float = field(init=False)
    inflacion_mensual: float = field(init=False)
    tasa_costo_capital_mes: float = field(init=False)
    factor_pago: float = field(init=False)
    prima_para_redondeo: float = field(init=False)
    tasa_frecuencia_seleccionada: float = field(init=False)

    def __post_init__(self):
        """
        Realiza todos los cálculos necesarios después de la inicialización.
        Aquí es donde implementamos la lógica de negocio.
        """
        # Cálculos principales
        self.adquisicion_fijo_poliza = self.calcular_adquisicion_fijo_poliza()
        self.mantenimiento_poliza = self.calcular_mantenimiento_poliza()
        self.tir_mensual = self.calcular_tir_mensual()
        self.reserva = self.calcular_reserva()
        self.tasa_interes_anual = self.calcular_tasa_interes_anual()
        self.tasa_interes_mensual = self.calcular_tasa_interes_mensual()
        self.tasa_inversion = self.calcular_tasa_inversion()
        self.inflacion_mensual = self.calcular_inflacion_mensual()
        self.tasa_costo_capital_mes = self.calcular_tasa_costo_capital_mes()
        self.factor_pago = self.calcular_factor_pago()
        self.prima_para_redondeo = self.calcular_prima_para_redondeo()
        self.tasa_frecuencia_seleccionada = self.calcular_tasa_frecuencia_seleccionada()

    def calcular_adquisicion_fijo_poliza(self) -> float:
        """Calcula el gasto de adquisición fijo por póliza"""
        return self.gasto_adquisicion / self.prima

    def calcular_mantenimiento_poliza(self) -> float:
        """Calcula el gasto de mantenimiento por póliza"""
        return self.gasto_mantenimiento / self.prima

    def calcular_tir_mensual(self) -> float:
        """Calcula la TIR mensual"""
        return (1 + self.moce) ** (self.tasa_mensualizacion) - 1

    def calcular_inflacion_mensual(self) -> float:
        """Calcula la inflación mensual a partir de la anual"""
        return (1 + self.inflacion_anual) ** (self.tasa_mensualizacion) - 1

    def calcular_reserva(self) -> float:
        """Calcula la reserva"""
        return self.margen_solvencia * (1 + self.fondo_garantia) * self.factor_ajuste

    def calcular_tasa_interes_anual(self) -> float:
        """Calcula la tasa de interés anual basada en la tabla de tasas de interés"""
        try:
            tasa_interes_anual = tasa_interes_reserva(self.tasas_interes_data)[
                str(self.periodo_vigencia)
            ]
            tasa_reserva = tasa_interes_anual["tasa_reserva"]
            return tasa_reserva
        except KeyError:
            raise ValueError(
                f"No se encontró una tasa para el periodo {self.periodo_vigencia}"
            )

    def calcular_tasa_interes_mensual(self) -> float:
        """Calcula la tasa de interés mensual"""
        tasa_interes_anual = self.calcular_tasa_interes_anual() / 100
        return (1 + tasa_interes_anual) ** (self.tasa_mensualizacion) - 1

    def calcular_tasa_inversion(self) -> float:
        """Calcula la tasa de inversión"""
        # Implementar fórmula específica según requerimiento
        tasa_interes_anual = tasa_interes_reserva(self.tasas_interes_data)[
            str(self.periodo_pago_primas)
        ]
        tasa_inversion = tasa_interes_anual["tasa_inversion"] / 100
        return tasa_inversion

    def calcular_tasa_costo_capital_mes(self) -> float:
        """Calcula la tasa de costo capital mensual"""
        return (1 + self.tasa_costo_capital_tir) ** (1 / 12) - 1

    def calcular_factor_pago(self) -> float:
        """
        Calcula el factor de pago según la frecuencia y el diccionario de factores.
        """
        clave = self.frecuencia_pago_primas.value.lower()  # "anual", "semestral", etc.
        return float(self.factores_pago.get(clave, 1.0))  # 1.0 por defecto si no existe

    def calcular_prima_para_redondeo(self) -> float:
        """Calcula la prima para redondeo"""
        return self.prima / self.factor_pago * self.factor_pago

    def calcular_tasa_frecuencia_seleccionada(self) -> float:
        """Calcula la tasa de frecuencia seleccionada"""
        return self.prima_para_redondeo / self.suma_asegurada
