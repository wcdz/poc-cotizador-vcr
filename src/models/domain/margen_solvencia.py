from dataclasses import dataclass
from src.helpers.redondeo_mensual import redondeo_mensual


@dataclass
class MargenSolvencia:
    """Modelo de dominio para el margen de solvencia"""

    # Definicion de atributos

    def calcular_margen_solvencia(
        self, reserva_fin_año: list[float], margen_solvencia_reserva: float
    ):
        return [reserva * margen_solvencia_reserva for reserva in reserva_fin_año]

    def calcular_varianza_margen_solvencia(
        self, margen_solvencia: list[float]
    ) -> list[float]:
        varianza_margen_solvencia = [margen_solvencia[0]] + [
            actual - anterior
            for anterior, actual in zip(margen_solvencia, margen_solvencia[1:])
        ]
        varianza_margen_solvencia.append(-margen_solvencia[-1])
        return varianza_margen_solvencia

    def calcular_ingreso_inversiones(
        self, reserva_fin_año: list[float], tasa_inversion: float
    ):
        _redondeo_mensual = redondeo_mensual(tasa_inversion)
        return [
            reserva_fin_año[i] * _redondeo_mensual for i in range(len(reserva_fin_año))
        ]

    def ingresiones_inversiones_margen_solvencia(
        self, margen_solvencia: list[float], tasa_inversion: float
    ):
        _redondeo_mensual = redondeo_mensual(tasa_inversion)
        return [
            margen_solvencia[i] * _redondeo_mensual
            for i in range(len(margen_solvencia))
        ]

    def calcular_ingreso_total_inversiones(
        self,
        ingreso_inversiones: list[float],
        ingresiones_inversiones_margen_solvencia: list[float],
    ):
        return [
            ingreso_inversiones[i] + ingresiones_inversiones_margen_solvencia[i]
            for i in range(len(ingreso_inversiones))
        ]
