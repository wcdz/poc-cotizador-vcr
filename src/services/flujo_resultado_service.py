from src.models.schemas.expuestos_mes_schema import ProyeccionActuarialOutput
from src.models.domain.flujo_resultado import FlujoResultado
from src.repositories.parametros_repository import JsonParametrosRepository
from src.repositories.devolucion_repository import JsonDevolucionRepository
from src.common.frecuencia_pago import FrecuenciaPago
from typing import List
from src.services.reserva_service import ReservaService


class FlujoResultadoService:
    def __init__(self):
        self.flujo_resultado = FlujoResultado()
        self.parametros_repository = JsonParametrosRepository()
        self.devolucion_repository = JsonDevolucionRepository()
        self.parametros_dict = self.parametros_repository.get_parametros_by_producto(
            "rumbo"
        )
        self.reserva = ReservaService()

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

    def calcular_rescates(
        self,
        expuestos_mes: ProyeccionActuarialOutput,
        rescate: list[float],
    ) -> List[float]:
        # Ya no necesitamos obtener los datos de devolución aquí
        # Ya que ReservaService lo hace internamente
        return self.reserva.calcular_ajuste_devolucion_anticipada(
            expuestos_mes,
            rescate,
        )

    def calcular_gastos_mantenimiento(self, gastos_mantenimiento: float) -> List[float]:
        return self.flujo_resultado.calcular_gastos_mantenimiento(gastos_mantenimiento)

    def calcular_comision(
        self,
        primas_recurrentes: List[float],
        asistencia: bool,
        frecuencia_pago_primas: FrecuenciaPago,
        costo_asistencia_funeraria: float,
        expuestos_mes: ProyeccionActuarialOutput,
        comision: float,
    ) -> List[float]:
        return self.flujo_resultado.calcular_comision(
            primas_recurrentes,
            asistencia,
            frecuencia_pago_primas,
            costo_asistencia_funeraria,
            expuestos_mes,
            comision,
        )

    def calcular_gasto_adquisicion(self, gasto_adquisicion: float):
        return self.flujo_resultado.calcular_gastos_adquisicion(gasto_adquisicion)

    def _formatear_resultados(self, resultados: list[float]) -> list[str]:
        return [str(resultado) for resultado in resultados]
