from src.repositories.parametros_repository import JsonParametrosRepository
from src.services.flujo_resultado_service import FlujoResultadoService
from src.models.domain.margen_solvencia import MargenSolvencia
from src.services.reserva_service import ReservaService


class MargenSolvenciaService:
    """Servicio para calcular el margen de solvencia"""

    def __init__(self):
        self.flujo_resultado_service = FlujoResultadoService()
        self.margen_solvencia = MargenSolvencia()
        self.reserva_service = ReservaService()

    def calcular_reserva_fin_año(self, saldo_reserva: list[float], moce: list[float]):
        return self.reserva_service.calcular_moce_saldo_reserva(
            saldo_reserva=saldo_reserva,
            moce=moce,
        )

    def calcular_margen_solvencia(
        self, reserva_fin_año: float, margen_solvencia_reserva: float
    ):
        return self.margen_solvencia.calcular_margen_solvencia(
            reserva_fin_año=reserva_fin_año,
            margen_solvencia_reserva=margen_solvencia_reserva,
        )

    def calcular_varianza_margen_solvencia(self, margen_solvencia: list[float]):
        return self.margen_solvencia.calcular_varianza_margen_solvencia(
            margen_solvencia=margen_solvencia,
        )

    def calcular_ingreso_total_inversiones(
        self,
        ingreso_inversiones: list[float],
        ingresiones_inversiones_margen_solvencia: list[float],
    ):
        return self.margen_solvencia.calcular_ingreso_total_inversiones(
            ingreso_inversiones=ingreso_inversiones,
            ingresiones_inversiones_margen_solvencia=ingresiones_inversiones_margen_solvencia,
        )

    def calcular_ingreso_inversiones(
        self, reserva_fin_año: list[float], tasa_inversion: float
    ):
        return self.margen_solvencia.calcular_ingreso_inversiones(
            reserva_fin_año=reserva_fin_año,
            tasa_inversion=tasa_inversion,
        )

    def ingresiones_inversiones_margen_solvencia(
        self, margen_solvencia: list[float], tasa_inversion: float
    ):
        return self.margen_solvencia.ingresiones_inversiones_margen_solvencia(
            margen_solvencia=margen_solvencia,
            tasa_inversion=tasa_inversion,
        )

    def _formatear_resultados(self):
        pass
