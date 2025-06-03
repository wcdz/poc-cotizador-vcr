from src.models.domain.reserva import Reserva
from src.models.domain.expuestos_mes import ExpuestosMes
from src.repositories.devolucion_repository import JsonDevolucionRepository


class ReservaService:

    def __init__(self) -> None:
        self.reserva = Reserva()
        self.devolucion_repository = JsonDevolucionRepository()

    def calcular_moce_saldo_reserva(
        self,
        tasa_interes_mensual: float,
        periodo_vigencia: int,
        margen_reserva: float,
    ):
        # calcular_moce + saldo_reserva * periodo_vigencia * 12

        moce = self.reserva.calcular_moce(
            tasa_interes_mensual=tasa_interes_mensual,
            periodo_vigencia=periodo_vigencia,
            margen_reserva=margen_reserva,
        )

        print(
            "moce => ",
            tasa_interes_mensual,
            periodo_vigencia,
            margen_reserva,
        )

        return (
            "Parametros para Moce Saldo Reserva => : ",
            tasa_interes_mensual,
            periodo_vigencia,
            margen_reserva,
        )

    def calcular_ajuste_devolucion_anticipada(
        self,
        expuestos_mes: ExpuestosMes,
        periodo_vigencia: int,
        prima: float,
        fraccionamiento_primas: float,
        porcentaje_devolucion: float,
    ):
        # Obtener los datos de devolución desde el repositorio
        devolucion = self.devolucion_repository.get_devolucion_data()

        return self.reserva.calcular_ajuste_devolucion_anticipada(
            expuestos_mes,
            periodo_vigencia,
            prima,
            fraccionamiento_primas,
            devolucion,
            porcentaje_devolucion,
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
