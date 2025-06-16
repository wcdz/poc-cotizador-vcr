"""
Producto RUMBO optimizado con mejor arquitectura.
Separación de responsabilidades y código mucho más legible.
"""

from src.helpers.TREA import calcular_trea
from src.utils.frecuencia_meses import frecuencia_meses
from src.models.products.rumbo.evaluador_rumbo import (
    ParametrosOptimizacion,
    EvaluadorVNA,
    OptimizadorBiseccion,
)


class Rumbo:
    """
    Clase Rumbo optimizada con mejor separación de responsabilidades.
    """

    def __init__(
        self,
        expuestos_mes_service,
        flujo_resultado_service,
        gastos_service,
        reserva_service,
        margen_solvencia_service,
    ):
        # Organizar servicios en un diccionario para fácil acceso
        self.servicios = {
            "expuestos_mes": expuestos_mes_service,
            "flujo_resultado": flujo_resultado_service,
            "gastos": gastos_service,
            "reserva": reserva_service,
            "margen_solvencia": margen_solvencia_service,
        }

    def calcular_porcentaje_devolucion_optimo(
        self,
        cotizacion_input,
        parametros_almacenados,
        tasas_interes_data,
        prima,
        flujo_resultado_service,
        parametros_calculados,
        periodo_vigencia,
        periodo_pago_primas,
        expuestos_mes=None,  # Ahora opcional, se calcula internamente
        gastos=None,  # Ahora opcional, se calcula internamente
        primas_recurrentes=None,  # Ahora opcional, se calcula internamente
        siniestros=None,  # Ahora opcional, se calcula internamente
        flujo_accionista=None,  # Ahora opcional, se calcula internamente
        flujo_pasivo=None,  # Ahora opcional, se calcula internamente
        saldo_reserva=None,  # Ahora opcional, se calcula internamente
        moce=None,  # Ahora opcional, se calcula internamente
        reserva_fin_año=None,  # Ahora opcional, se calcula internamente
        margen_solvencia=None,  # Ahora opcional, se calcula internamente
        varianza_margen_solvencia=None,  # Ahora opcional, se calcula internamente
        ingreso_total_inversiones=None,  # Ahora opcional, se calcula internamente
        varianza_reserva=None,  # Ahora opcional, se calcula internamente
        varianza_moce=None,  # Ahora opcional, se calcula internamente
        gastos_mantenimiento=None,  # Ahora opcional, se calcula internamente
        gasto_adquisicion=None,  # Ahora opcional, se calcula internamente
        comision=None,  # Ahora opcional, se calcula internamente
        IR=None,  # Ahora opcional, se calcula internamente
        utilidad_pre_pi_ms=None,  # Ahora opcional, se calcula internamente
    ) -> float:
        """
        Método optimizado que ahora tiene solo 15 líneas en lugar de 200+.
        Toda la complejidad se movió a clases especializadas.

        Los parámetros adicionales se mantienen para compatibilidad hacia atrás,
        pero ahora son opcionales ya que se calculan internamente.
        """
        # 1. Preparar parámetros de optimización
        params = ParametrosOptimizacion(
            cotizacion_input=cotizacion_input,
            parametros_almacenados=parametros_almacenados,
            parametros_calculados=parametros_calculados,
            periodo_vigencia=periodo_vigencia,
            periodo_pago_primas=periodo_pago_primas,
            prima=prima,
            flujo_resultado_service=flujo_resultado_service,
        )

        # 2. Crear evaluador VNA especializado
        evaluador = EvaluadorVNA(params, self.servicios)

        # 3. Ejecutar optimización con algoritmo separado
        optimizador = OptimizadorBiseccion(evaluador.evaluar)
        resultado = optimizador.optimizar()

        # 4. Retornar porcentaje óptimo
        return resultado.porcentaje_optimo

    def _calcular_trea(self, periodo_pago_primas, prima, porcentaje_devolucion_optimo):
        """Cálculo de TREA - sin cambios"""
        return calcular_trea(periodo_pago_primas, prima, porcentaje_devolucion_optimo)

    def calcular_aporte_total(self, periodo_pago_primas, prima):
        """Cálculo de aporte total - sin cambios"""
        return periodo_pago_primas * prima * 12

    def calcular_devolucion_total(
        self,
        tasa_frecuencia_seleccionada,
        suma_asegurada,
        frecuencia_pago_primas,
        periodo_pago_primas,
        porcentaje_devolucion_optimo,
    ):
        """Cálculo de devolución total - sin cambios"""
        _frecuencia_pago_primas = frecuencia_meses(frecuencia_pago_primas)
        _porcentaje_devolucion_optimo = porcentaje_devolucion_optimo / 100

        return (
            tasa_frecuencia_seleccionada * suma_asegurada * 12 / _frecuencia_pago_primas
        ) * (periodo_pago_primas * _porcentaje_devolucion_optimo)

    def calcular_ganancia_total(self, aporte_total, devolucion_total):
        """Cálculo de ganancia total - sin cambios"""
        return devolucion_total - aporte_total
