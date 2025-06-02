from src.models.schemas.expuestos_mes_schema import ProyeccionActuarialOutput
from src.models.domain.flujo_resultado import FlujoResultado
from src.repositories.parametros_repository import JsonParametrosRepository
from src.common.frecuencia_pago import FrecuenciaPago
from typing import List


class FlujoResultadoService:
    def __init__(self):
        self.flujo_resultado = FlujoResultado()
        self.parametros_repository = JsonParametrosRepository()
        self.parametros_dict = self.parametros_repository.get_parametros_by_producto(
            "rumbo"
        )

    # Orquestacion para gastos
    def calcular_primas_recurrentes(
        self,
        expuestos_mes: ProyeccionActuarialOutput,
        periodo_pago_primas: int,
        frecuencia_pago_primas: FrecuenciaPago,
        prima: float,
    ):

        fraccionamiento_primas = self.parametros_dict.get(
            "fraccionamiento_primas", 0.01
        )

        return self.flujo_resultado.calcular_primas_recurrentes(
            expuestos_mes,
            periodo_pago_primas,
            frecuencia_pago_primas,
            prima,
            fraccionamiento_primas,
        )

    def calcular_siniestros(
        self, expuestos_mes: ProyeccionActuarialOutput, suma_asegurada: float
    ) -> List[float]:
        return self.flujo_resultado.calcular_siniestros(expuestos_mes, suma_asegurada)

    def calcular_gastos_mantenimiento(self, gastos_mantenimiento: float) -> List[float]:
        return self.flujo_resultado.calcular_gastos_mantenimiento(gastos_mantenimiento)

    def _formatear_resultados(self, resultados: list[float]) -> list[str]:
        return [str(resultado) for resultado in resultados]
