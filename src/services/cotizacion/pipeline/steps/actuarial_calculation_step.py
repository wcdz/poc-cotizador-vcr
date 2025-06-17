from .base_step import PipelineStep
from ..cotizacion_context import CotizacionContext
from src.services.expuestos_mes_service import ExpuestosMesService
from src.services.gastos_service import GastosService
from src.services.flujo_resultado_service import FlujoResultadoService
from src.services.margen_solvencia_service import MargenSolvenciaService
from src.services.reserva_service import ReservaService


class ActuarialCalculationStep(PipelineStep):
    """Paso de cálculos actuariales - Todos los flujos financieros"""

    def __init__(self):
        super().__init__("ActuarialCalculation")
        self.expuestos_mes_service = ExpuestosMesService()
        self.gastos_service = GastosService()
        self.flujo_resultado_service = FlujoResultadoService()
        self.margen_solvencia_service = MargenSolvenciaService()
        self.reserva_service = ReservaService()

    def process(self, context: CotizacionContext) -> CotizacionContext:
        """Ejecuta todos los cálculos actuariales"""

        # 1. CÁLCULOS BASE
        context = self._calcular_expuestos_mes(context)
        context = self._calcular_gastos(context)

        # 2. FLUJOS PRINCIPALES
        context = self._calcular_flujos_principales(context)

        # 3. RESCATES
        context = self._calcular_rescates(context)

        # 4. FLUJOS SECUNDARIOS
        context = self._calcular_flujos_secundarios(context)

        # 5. RESERVAS Y PASIVOS
        context = self._calcular_reservas_y_pasivos(context)

        # 6. MÁRGENES DE SOLVENCIA
        context = self._calcular_margenes_solvencia(context)

        # 7. VARIANZAS Y UTILIDADES
        context = self._calcular_varianzas_y_utilidades(context)

        # 8. FLUJO ACCIONISTA FINAL
        context = self._calcular_flujo_accionista_final(context)

        return context

    def _calcular_expuestos_mes(self, context: CotizacionContext) -> CotizacionContext:
        """Calcula los expuestos por mes"""
        context.expuestos_mes = self.expuestos_mes_service.calcular_expuestos_mes(
            edad_actuarial=context.input.parametros.edad_actuarial,
            sexo=context.input.parametros.sexo,
            fumador=(
                context.input.parametros.fumador
                if context.input.parametros.fumador
                else False
            ),
            frecuencia_pago_primas=context.input.parametros.frecuencia_pago_primas,
            periodo_vigencia=context.periodo_vigencia,
            periodo_pago_primas=context.periodo_pago_primas,
            ajuste_mortalidad=context.parametros_almacenados.ajuste_mortalidad,
        )
        return context

    def _calcular_gastos(self, context: CotizacionContext) -> CotizacionContext:
        """Calcula los gastos"""
        context.gastos = self.gastos_service.calcular_gastos(
            periodo_vigencia=context.periodo_vigencia,
            periodo_pago_primas=context.periodo_pago_primas,
            prima=context.prima,
            expuestos_mes=context.expuestos_mes,
            frecuencia_pago_primas=context.input.parametros.frecuencia_pago_primas,
            mantenimiento_poliza=context.parametros_calculados.mantenimiento_poliza,
            moneda=context.parametros_almacenados.moneda,
            valor_dolar=context.parametros_almacenados.valor_dolar,
            valor_soles=context.parametros_almacenados.valor_soles,
            tiene_asistencia=context.parametros_almacenados.tiene_asistencia,
            costo_mensual_asistencia_funeraria=context.parametros_almacenados.costo_mensual_asistencia_funeraria,
            inflacion_mensual=context.parametros_calculados.inflacion_mensual,
        )
        return context

    def _calcular_flujos_principales(
        self, context: CotizacionContext
    ) -> CotizacionContext:
        """Calcula primas recurrentes y siniestros"""
        context.primas_recurrentes = (
            self.flujo_resultado_service.calcular_primas_recurrentes(
                expuestos_mes=context.expuestos_mes,
                periodo_pago_primas=context.periodo_pago_primas,
                frecuencia_pago_primas=context.input.parametros.frecuencia_pago_primas,
                prima=context.prima,
            )
        )

        context.siniestros = self.flujo_resultado_service.calcular_siniestros(
            expuestos_mes=context.expuestos_mes,
            suma_asegurada=context.suma_asegurada,
        )
        return context

    def _calcular_rescates(self, context: CotizacionContext) -> CotizacionContext:
        """Calcula rescates y ajustes"""
        context.rescate = self.reserva_service.calcular_rescate(
            periodo_vigencia=context.periodo_vigencia,
            prima=context.input.parametros.prima,
            fraccionamiento_primas=context.parametros_almacenados.fraccionamiento_primas,
            porcentaje_devolucion=context.input.parametros.porcentaje_devolucion,
        )

        context.rescates_ajuste_devolucion = (
            self.flujo_resultado_service.calcular_rescates(
                expuestos_mes=context.expuestos_mes,
                rescate=context.rescate,
            )
        )
        return context

    def _calcular_flujos_secundarios(
        self, context: CotizacionContext
    ) -> CotizacionContext:
        """Calcula gastos mantenimiento, adquisición y comisiones"""
        context.gastos_mantenimiento = (
            self.flujo_resultado_service.calcular_gastos_mantenimiento(
                gastos_mantenimiento=context.gastos,
            )
        )

        context.gasto_adquisicion = (
            self.flujo_resultado_service.calcular_gasto_adquisicion(
                gasto_adquisicion=context.parametros_almacenados.gasto_adquisicion,
            )
        )

        context.comision = self.flujo_resultado_service.calcular_comision(
            primas_recurrentes=context.primas_recurrentes,
            asistencia=context.parametros_almacenados.tiene_asistencia,
            frecuencia_pago_primas=context.input.parametros.frecuencia_pago_primas,
            costo_asistencia_funeraria=context.parametros_almacenados.costo_mensual_asistencia_funeraria,
            expuestos_mes=context.expuestos_mes,
            comision=context.parametros_almacenados.comision,
        )
        return context

    def _calcular_reservas_y_pasivos(
        self, context: CotizacionContext
    ) -> CotizacionContext:
        """Calcula flujo pasivo, saldo reserva y MOCE"""
        context.flujo_pasivo = self.reserva_service.calcular_flujo_pasivo(
            context.siniestros,
            context.rescates_ajuste_devolucion,
            context.gastos_mantenimiento,
            context.comision,
            context.gasto_adquisicion,
            context.primas_recurrentes,
        )

        context.saldo_reserva = self.reserva_service.calcular_saldo_reserva(
            context.flujo_pasivo,
            context.parametros_calculados.tasa_interes_mensual,
            context.rescate,
            context.expuestos_mes,
        )

        context.moce = self.reserva_service.calcular_moce(
            tasa_costo_capital_mensual=context.parametros_calculados.tasa_costo_capital_mensual,
            tasa_interes_mensual=context.parametros_calculados.tasa_interes_mensual,
            margen_reserva=context.parametros_almacenados.margen_solvencia,
            saldo_reserva=context.saldo_reserva,
        )

        context.moce_saldo_reserva = self.reserva_service.calcular_moce_saldo_reserva(
            saldo_reserva=context.saldo_reserva,
            moce=context.moce,
        )

        context.reserva_fin_año = (
            self.margen_solvencia_service.calcular_reserva_fin_año(
                saldo_reserva=context.saldo_reserva,
                moce=context.moce,
            )
        )
        return context

    def _calcular_margenes_solvencia(
        self, context: CotizacionContext
    ) -> CotizacionContext:
        """Calcula márgenes de solvencia e inversiones"""
        context.margen_solvencia = (
            self.margen_solvencia_service.calcular_margen_solvencia(
                reserva_fin_año=context.reserva_fin_año,
                margen_solvencia_reserva=context.parametros_calculados.reserva,
            )
        )

        context.varianza_margen_solvencia = (
            self.margen_solvencia_service.calcular_varianza_margen_solvencia(
                margen_solvencia=context.margen_solvencia,
            )
        )

        context.ingreso_inversiones = (
            self.margen_solvencia_service.calcular_ingreso_inversiones(
                reserva_fin_año=context.reserva_fin_año,
                tasa_inversion=context.parametros_calculados.tasa_inversion,
            )
        )

        context.ingreso_inversiones_margen_solvencia = (
            self.margen_solvencia_service.ingresiones_inversiones_margen_solvencia(
                margen_solvencia=context.margen_solvencia,
                tasa_inversion=context.parametros_calculados.tasa_inversion,
            )
        )

        context.ingreso_total_inversiones = self.margen_solvencia_service.calcular_ingreso_total_inversiones(
            ingreso_inversiones=context.ingreso_inversiones,
            ingresiones_inversiones_margen_solvencia=context.ingreso_inversiones_margen_solvencia,
        )
        return context

    def _calcular_varianzas_y_utilidades(
        self, context: CotizacionContext
    ) -> CotizacionContext:
        """Calcula varianzas y utilidades"""
        context.varianza_moce = self.reserva_service.calcular_varianza_moce(
            context.moce
        )
        context.varianza_reserva = self.reserva_service.calcular_varianza_reserva(
            context.saldo_reserva
        )

        context.variacion_reserva = (
            self.flujo_resultado_service.calcular_variacion_reserva(
                varianza_reserva=context.varianza_reserva,
                varianza_moce=context.varianza_moce,
            )
        )

        context.utilidad_pre_pi_ms = (
            self.flujo_resultado_service.calcular_utilidad_pre_pi_ms(
                primas_recurrentes=context.primas_recurrentes,
                comision=context.comision,
                gasto_adquisicion=context.gasto_adquisicion,
                gastos_mantenimiento=context.gastos_mantenimiento,
                siniestros=context.siniestros,
                rescates=context.rescates_ajuste_devolucion,
                variacion_reserva=context.variacion_reserva,
            )
        )

        context.IR = self.flujo_resultado_service.calcular_IR(
            utilidad_pre_pi_ms=context.utilidad_pre_pi_ms,
            impuesto_renta=context.parametros_almacenados.impuesto_renta,
        )
        return context

    def _calcular_flujo_accionista_final(
        self, context: CotizacionContext
    ) -> CotizacionContext:
        """Calcula el flujo accionista y auxiliar VNA"""
        context.flujo_accionista = (
            self.flujo_resultado_service.calcular_flujo_accionista(
                utilidad_pre_pi_ms=context.utilidad_pre_pi_ms,
                varianza_margen_solvencia=context.varianza_margen_solvencia,
                IR=context.IR,
                ingreso_total_inversiones=context.ingreso_total_inversiones,
            )
        )

        context.auxiliar_vna = self.flujo_resultado_service.auxiliar(
            flujo_accionista=context.flujo_accionista,
            tasa_costo_capital_mes=context.parametros_calculados.tasa_costo_capital_mes,
        )
        return context

    def _calcular_tabla_devolucion(
        self, context: CotizacionContext
    ) -> CotizacionContext:
        """Calcula la tabla de devolución"""
        context.tabla_devolucion = self.reserva_service.calcular_tabla_devolucion_rumbo(
            periodo_vigencia=context.periodo_vigencia,
            porcentaje_devolucion_optimo=context.porcentaje_devolucion_optimo,
        )
        return context
