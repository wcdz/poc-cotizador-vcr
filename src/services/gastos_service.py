from src.repositories.parametros_repository import JsonParametrosRepository
from src.services.expuestos_mes_service import ExpuestosMesService
from src.models.schemas.expuestos_mes_schema import ProyeccionActuarialOutput
from src.models.schemas.gastos_schema import Gastos, ResultadoMensualGastos
from decimal import Decimal
from typing import Dict, List, Any

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
        self.expuestos_mes = ExpuestosMesService()

    def calcular_gastos(
        self,
        periodo_vigencia: int,
        periodo_pago_primas: int,
        prima: float,
        expuestos_mes: ProyeccionActuarialOutput,
    ) -> Gastos:
        """
        Método para calcular gastos
        """

        print(periodo_vigencia)
        print(periodo_pago_primas)
        print(prima)
        

        # Este es un cálculo simplificado para ejemplo
        resultados_mensuales = []

        # Procesar los resultados mensuales de expuestos
        for i, resultado in enumerate(expuestos_mes["resultados_mensuales"]):
            mes = resultado["mes"]
            anio_poliza = resultado["anio_poliza"]

            # Cálculos simplificados para ejemplo
            gasto_mantenimiento_prima = str(Decimal(str(prima * 0.01)))
            gasto_mantenimiento_fijo = str(
                Decimal(str(10.0))
            )  # Valor fijo para ejemplo
            factor_inflacion = str(
                Decimal(str(1.0 + (anio_poliza - 1) * 0.02))
            )  # Incremento del 2% por año
            gasto_total = str(
                Decimal(
                    str(
                        float(gasto_mantenimiento_prima)
                        + float(gasto_mantenimiento_fijo)
                    )
                )
                * Decimal(factor_inflacion)
            )

            # Crear resultado mensual
            resultado_mensual = ResultadoMensualGastos(
                mes=mes,
                anio_poliza=anio_poliza,
                gasto_mantenimiento_prima=gasto_mantenimiento_prima,
                gasto_mantenimiento_fijo=gasto_mantenimiento_fijo,
                factor_inflacion=factor_inflacion,
                gasto_mantenimiento_total=gasto_total,
            )

            resultados_mensuales.append(resultado_mensual.model_dump())

        # Crear resumen
        resumen = {
            "gasto_total": str(
                Decimal(
                    sum(
                        float(r["gasto_mantenimiento_total"])
                        for r in resultados_mensuales
                    )
                )
            ),
            "gasto_promedio_mensual": str(
                Decimal(
                    sum(
                        float(r["gasto_mantenimiento_total"])
                        for r in resultados_mensuales
                    )
                    / len(resultados_mensuales)
                    if resultados_mensuales
                    else 0
                )
            ),
        }

        # Retornar el objeto Gastos
        return Gastos(
            resultados_mensuales=resultados_mensuales, resumen=resumen
        ).model_dump()


# Instancia global del servicio
gastos_service = GastosService()
