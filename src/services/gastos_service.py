from src.repositories.parametros_repository import JsonParametrosRepository
from src.services.expuestos_mes_service import ExpuestosMesService
from src.models.schemas.expuestos_mes_schema import ProyeccionActuarialOutput
from src.models.schemas.gastos_schema import (
    Gastos as GastosSchema,
    ResultadoMensualGastos,
)
from src.models.domain.gastos import Gastos
from decimal import Decimal
from typing import Dict, List, Any
from src.services.flujo_resultado_service import FlujoResultadoService
from src.common.frecuencia_pago import FrecuenciaPago

"""
Servicio para cálculos de gastos
"""


class GastosService:
    """Servicio para realizar cálculos de gastos"""

    def __init__(self):
        self.parametros_repository = JsonParametrosRepository()
        self.parametros_dict = self.parametros_repository.get_parametros_by_producto(
            "rumbo"
        )
        self.flujo_resultado_service = FlujoResultadoService()

    def calcular_gastos(
        self,
        periodo_vigencia: int,
        periodo_pago_primas: int,
        prima: float,
        expuestos_mes: ProyeccionActuarialOutput,
        frecuencia_pago_primas: FrecuenciaPago = FrecuenciaPago.ANUAL,
        mantenimiento_poliza: float = 0.0,
        inflacion_mensual: float = 0.0,
        moneda: str = "SOLES",
        valor_dolar: float = 0.0,
        valor_soles: float = 0.0,
        tiene_asistencia: bool = False,
        costo_mensual_asistencia_funeraria: float = 0.0,
        moneda_poliza: float = 0.0,
    ) -> Dict:
        """
        Método para calcular gastos
        """

        # Crear objeto del dominio
        gastos_domain = Gastos(
            periodo_vigencia=periodo_vigencia,
            periodo_pago_primas=periodo_pago_primas,
            frecuencia_pago_primas=frecuencia_pago_primas,
            prima=prima,
            mantenimiento_poliza=mantenimiento_poliza,
            inflacion_mensual=inflacion_mensual,
            moneda=moneda,
            valor_dolar=valor_dolar,
            valor_soles=valor_soles,
            tiene_asistencia=tiene_asistencia,
            costo_mensual_asistencia_funeraria=costo_mensual_asistencia_funeraria,
            moneda_poliza=moneda_poliza,
            expuestos_mes=expuestos_mes,
        )

        primas_recurrentes = self.flujo_resultado_service.calcular_primas_recurrentes(
            expuestos_mes, periodo_pago_primas, frecuencia_pago_primas, prima
        )

        # print("primas_recurrentes => ", primas_recurrentes) # * OK

        # F2 OK
        gasto_mantenimiento_prima_co = (
            gastos_domain.calcular_gasto_mantenimiento_prima_co(
                primas_recurrentes, mantenimiento_poliza
            )
        )

        # print("gasto_mantenimiento_prima_co => ", gasto_mantenimiento_prima_co) # * OK

        # * G2 - requiere
        gastos_mantenimiento_moneda_poliza = (
            gastos_domain.calcular_gastos_mantenimiento_moneda_poliza(
                moneda,
                valor_dolar,
                valor_soles,
                tiene_asistencia,
                costo_mensual_asistencia_funeraria,
            )
        )

        # print(
        #     "gastos_mantenimiento_moneda_poliza => ", gastos_mantenimiento_moneda_poliza
        # )

        # * G2 - final
        gasto_mantenimiento_fijo_poliza_anual = (
            gastos_domain.calcular_gastos_mantenimiento_fijo_poliza_anual(
                expuestos_mes, gastos_mantenimiento_moneda_poliza
            )
        )

        # print(
        #     "gasto_mantenimiento_fijo_poliza_anual => ",
        #     gasto_mantenimiento_fijo_poliza_anual,
        # )

        # * H2
        factor_inflacion = gastos_domain.calcular_factor_inflacion(
            gasto_mantenimiento_prima_co,
            gasto_mantenimiento_fijo_poliza_anual,
            inflacion_mensual,
        )

        # print("factor_inflacion => ", factor_inflacion)

        # * I
        gasto_mantenimiento_total = gastos_domain.calcular_gasto_mantenimiento_total(
            gasto_mantenimiento_prima_co,
            gasto_mantenimiento_fijo_poliza_anual,
            factor_inflacion,
            periodo_vigencia,
        )

        # print("gasto_mantenimiento_total => ", gasto_mantenimiento_total)

        print("gasto_mantenimiento_prima_co => ", gasto_mantenimiento_prima_co)
        print(
            "gastos_mantenimiento_moneda_poliza => ", gastos_mantenimiento_moneda_poliza
        )
        print(
            "gasto_mantenimiento_fijo_poliza_anual => ",
            gasto_mantenimiento_fijo_poliza_anual,
        )
        print("factor_inflacion => ", factor_inflacion)
        print("gasto_mantenimiento_total => ", gasto_mantenimiento_total)

        resultados_mensuales = self._formatear_resultados(
            gasto_mantenimiento_prima_co,
            gastos_mantenimiento_moneda_poliza,
            gasto_mantenimiento_fijo_poliza_anual,
            factor_inflacion,
            gasto_mantenimiento_total,
        )
        return {"resultados_mensuales": resultados_mensuales}

    def _formatear_resultados(
        self,
        gasto_mantenimiento_prima_co: List[float],
        gastos_mantenimiento_moneda_poliza: List[float],
        gasto_mantenimiento_fijo_poliza_anual: List[float],
        factor_inflacion: List[float],
        gasto_mantenimiento_total: List[float],
    ) -> List[Dict[str, Any]]:

        # Crear resultado mensual
        resultados_formateados = []
        for i, resultado in enumerate(gasto_mantenimiento_prima_co):
            mes = i + 1
            anio_poliza = 1
            _gasto_mantenimiento_prima_co = str(Decimal(str(resultado)))
            _gasto_mantenimiento_moneda_poliza = str(gastos_mantenimiento_moneda_poliza)
            _gasto_mantenimiento_fijo_poliza_anual = str(
                Decimal(str(gasto_mantenimiento_fijo_poliza_anual[i]))
            )
            _factor_inflacion = str(Decimal(str(factor_inflacion[i])))
            _gasto_mantenimiento_total = str(Decimal(str(gasto_mantenimiento_total[i])))

            resultado_mensual = ResultadoMensualGastos(
                mes=mes,
                anio_poliza=anio_poliza,
                gasto_mantenimiento_prima_co=_gasto_mantenimiento_prima_co,
                gastos_mantenimiento_moneda_poliza=_gasto_mantenimiento_moneda_poliza,
                gasto_mantenimiento_fijo_poliza_anual=_gasto_mantenimiento_fijo_poliza_anual,
                factor_inflacion=_factor_inflacion,
                gasto_mantenimiento_total=_gasto_mantenimiento_total,
            )

            resultados_formateados.append(resultado_mensual.model_dump())
        return resultados_formateados


# Instancia global del servicio
gastos_service = GastosService()
