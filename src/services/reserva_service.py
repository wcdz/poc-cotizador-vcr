from src.models.domain.reserva import Reserva
from src.models.domain.expuestos_mes import ExpuestosMes
from src.repositories.devolucion_repository import JsonDevolucionRepository


class ReservaService:

    def __init__(self) -> None:
        self.reserva = Reserva()
        self.devolucion_repository = JsonDevolucionRepository()

    def calcular_moce_saldo_reserva(
        self,
        saldo_reserva: list[float],
        moce: list[float],
    ):
        return self.reserva.calcular_moce_saldo_reserva(saldo_reserva, moce)

    def calcular_moce(
        self,
        tasa_costo_capital_mensual: float,
        tasa_interes_mensual: float,
        margen_reserva: float,
        saldo_reserva: list[float],
    ):
        return self.reserva.calcular_moce(
            tasa_costo_capital_mensual,
            tasa_interes_mensual,
            margen_reserva,
            saldo_reserva,
        )

    def calcular_ajuste_devolucion_anticipada(
        self,
        expuestos_mes: ExpuestosMes,
        rescate: list[float],
    ):
        return self.reserva.calcular_ajuste_devolucion_anticipada(
            expuestos_mes,
            rescate,
        )

    def calcular_flujo_pasivo(
        self,
        siniestros: list[float],
        rescates: list[float],
        gastos_mantenimiento: list[float],
        comision: list[float],
        gastos_adquisicion: float,
        primas_recurrentes: list[float],
    ):
        return self.reserva.calcular_flujo_pasivo(
            siniestros,
            list(map(lambda x: -x, rescates)),
            list(map(lambda x: -x, gastos_mantenimiento)),
            list(map(lambda x: -x, comision)),
            -gastos_adquisicion,
            primas_recurrentes,
        )

    def calcular_rescate(
        self,
        periodo_vigencia: int,
        prima: float,
        fraccionamiento_primas: float,
        porcentaje_devolucion: float,
    ):
        # Obtener los datos de devolución desde el repositorio
        devolucion = self.devolucion_repository.get_devolucion_data()
        return self.reserva.calcular_rescate(
            periodo_vigencia,
            prima,
            fraccionamiento_primas,
            devolucion,
            porcentaje_devolucion,
        )

    def calcular_saldo_reserva(
        self,
        flujo_pasivo: list[float],
        tasa_interes_mensual: float,
        rescate: list[float],
        expuestos_mes: ExpuestosMes,
    ):

        return self.reserva.calcular_saldo_reserva(
            flujo_pasivo,
            tasa_interes_mensual,
            rescate,
            vivos_inicio=[
                float(item["vivos_inicio"])
                for item in expuestos_mes.get("resultados_mensuales", [])
            ],
        )

    def calcular_varianza_moce(self, moce: list[float]):
        return self.reserva.calcular_varianza_moce(moce)

    def calcular_varianza_reserva(self, saldo_reserva: list[float]):
        return self.reserva.calcular_varianza_reserva(saldo_reserva)

    # TODO: Solo para RUMBO [Pendiente para Endosos y VCP]
    def calcular_tabla_devolucion(
        self, periodo_vigencia: int, porcentaje_devolucion_optimo: float
    ):
        # Obtener los datos de devolución desde el repositorio
        devolucion = self.devolucion_repository.get_devolucion_data()
        return self.reserva.calcular_porcentaje_devolucion_mensual_anual(
            periodo_vigencia,
            porcentaje_devolucion_optimo,
            devolucion,
        )
