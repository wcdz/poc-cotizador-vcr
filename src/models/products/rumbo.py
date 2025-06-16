from src.helpers.trea import calcular_trea
from src.utils.frecuencia_meses import frecuencia_meses


class Rumbo:
    def __init__(
        self,
        expuestos_mes_service,
        flujo_resultado_service,
        gastos_service,
        reserva_service,
        margen_solvencia_service,
    ):
        self.expuestos_mes = expuestos_mes_service
        self.flujo_resultado_service = flujo_resultado_service
        self.gastos_service = gastos_service
        self.reserva_service = reserva_service
        self.margen_solvencia_service = margen_solvencia_service

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
        expuestos_mes,
        gastos,
        primas_recurrentes,
        siniestros,
        flujo_accionista,
        flujo_pasivo,
        saldo_reserva,
        moce,
        reserva_fin_año,
        margen_solvencia,
        varianza_margen_solvencia,
        ingreso_total_inversiones,
        varianza_reserva,
        varianza_moce,
        gastos_mantenimiento,
        gasto_adquisicion,
        comision,
        IR,
        utilidad_pre_pi_ms,
    ):
        def evaluar_vna(porcentaje):
            expuestos_mes = self.expuestos_mes.calcular_expuestos_mes(
                edad_actuarial=cotizacion_input.parametros.edad_actuarial,
                sexo=cotizacion_input.parametros.sexo,
                fumador=cotizacion_input.parametros.fumador,
                frecuencia_pago_primas=cotizacion_input.parametros.frecuencia_pago_primas,
                periodo_vigencia=periodo_vigencia,
                periodo_pago_primas=periodo_pago_primas,
                ajuste_mortalidad=parametros_almacenados.ajuste_mortalidad,
            )
            siniestros = flujo_resultado_service.calcular_siniestros(
                expuestos_mes=expuestos_mes,
                suma_asegurada=parametros_almacenados.suma_asegurada_rumbo,
            )
            primas_recurrentes = flujo_resultado_service.calcular_primas_recurrentes(
                expuestos_mes=expuestos_mes,
                periodo_pago_primas=periodo_pago_primas,
                frecuencia_pago_primas=cotizacion_input.parametros.frecuencia_pago_primas,
                prima=prima,
            )
            gastos = self.gastos_service.calcular_gastos(
                periodo_vigencia=periodo_vigencia,
                periodo_pago_primas=periodo_pago_primas,
                prima=prima,
                expuestos_mes=expuestos_mes,
                frecuencia_pago_primas=cotizacion_input.parametros.frecuencia_pago_primas,
                mantenimiento_poliza=parametros_calculados.mantenimiento_poliza,
                moneda=parametros_almacenados.moneda,
                valor_dolar=parametros_almacenados.valor_dolar,
                valor_soles=parametros_almacenados.valor_soles,
                tiene_asistencia=parametros_almacenados.tiene_asistencia,
                costo_mensual_asistencia_funeraria=parametros_almacenados.costo_mensual_asistencia_funeraria,
                inflacion_mensual=parametros_calculados.inflacion_mensual,
            )
            gastos_mantenimiento = (
                flujo_resultado_service.calcular_gastos_mantenimiento(
                    gastos_mantenimiento=gastos,
                )
            )
            gasto_adquisicion = flujo_resultado_service.calcular_gasto_adquisicion(
                gasto_adquisicion=parametros_almacenados.gasto_adquisicion,
            )
            comision = flujo_resultado_service.calcular_comision(
                primas_recurrentes=primas_recurrentes,
                asistencia=parametros_almacenados.tiene_asistencia,
                frecuencia_pago_primas=cotizacion_input.parametros.frecuencia_pago_primas,
                costo_asistencia_funeraria=parametros_almacenados.costo_mensual_asistencia_funeraria,
                expuestos_mes=expuestos_mes,
                comision=parametros_almacenados.comision,
            )
            rescate = self.reserva_service.calcular_rescate(
                periodo_vigencia=periodo_vigencia,
                prima=prima,
                fraccionamiento_primas=parametros_almacenados.fraccionamiento_primas,
                porcentaje_devolucion=porcentaje,
            )
            rescates = flujo_resultado_service.calcular_rescates(
                expuestos_mes=expuestos_mes,
                rescate=rescate,
            )
            flujo_pasivo_ = self.reserva_service.calcular_flujo_pasivo(
                siniestros,
                rescates,
                gastos_mantenimiento,
                comision,
                gasto_adquisicion,
                primas_recurrentes,
            )
            saldo_reserva_ = self.reserva_service.calcular_saldo_reserva(
                flujo_pasivo_,
                parametros_calculados.tasa_interes_mensual,
                rescate,
                expuestos_mes,
            )
            moce_ = self.reserva_service.calcular_moce(
                tasa_costo_capital_mensual=parametros_calculados.tasa_costo_capital_mensual,
                tasa_interes_mensual=parametros_calculados.tasa_interes_mensual,
                margen_reserva=parametros_almacenados.margen_solvencia,
                saldo_reserva=saldo_reserva_,
            )
            reserva_fin_año_ = self.margen_solvencia_service.calcular_reserva_fin_año(
                saldo_reserva=saldo_reserva_,
                moce=moce_,
            )
            margen_solvencia_ = self.margen_solvencia_service.calcular_margen_solvencia(
                reserva_fin_año=reserva_fin_año_,
                margen_solvencia_reserva=parametros_calculados.reserva,
            )
            varianza_margen_solvencia_ = (
                self.margen_solvencia_service.calcular_varianza_margen_solvencia(
                    margen_solvencia=margen_solvencia_,
                )
            )
            ingreso_inversiones_ = (
                self.margen_solvencia_service.calcular_ingreso_inversiones(
                    reserva_fin_año=reserva_fin_año_,
                    tasa_inversion=parametros_calculados.tasa_inversion,
                )
            )
            ingresiones_inversiones_margen_solvencia_ = (
                self.margen_solvencia_service.ingresiones_inversiones_margen_solvencia(
                    margen_solvencia=margen_solvencia_,
                    tasa_inversion=parametros_calculados.tasa_inversion,
                )
            )
            ingreso_total_inversiones_ = self.margen_solvencia_service.calcular_ingreso_total_inversiones(
                ingreso_inversiones=ingreso_inversiones_,
                ingresiones_inversiones_margen_solvencia=ingresiones_inversiones_margen_solvencia_,
            )
            varianza_moce_ = self.reserva_service.calcular_varianza_moce(moce_)
            varianza_reserva_ = self.reserva_service.calcular_varianza_reserva(
                saldo_reserva_
            )
            variacion_reserva_ = flujo_resultado_service.calcular_variacion_reserva(
                varianza_reserva=varianza_reserva_,
                varianza_moce=varianza_moce_,
            )
            utilidad_pre_ = flujo_resultado_service.calcular_utilidad_pre_pi_ms(
                primas_recurrentes,
                comision,
                gasto_adquisicion,
                gastos_mantenimiento,
                siniestros,
                rescates,
                variacion_reserva_,
            )
            IR_ = flujo_resultado_service.calcular_IR(
                utilidad_pre_pi_ms=utilidad_pre_,
                impuesto_renta=parametros_almacenados.impuesto_renta,
            )
            flujo_accionista_ = flujo_resultado_service.calcular_flujo_accionista(
                utilidad_pre_pi_ms=utilidad_pre_,
                varianza_margen_solvencia=varianza_margen_solvencia_,
                IR=IR_,
                ingreso_total_inversiones=ingreso_total_inversiones_,
            )
            vna = flujo_resultado_service.auxiliar(
                flujo_accionista=flujo_accionista_,
                tasa_costo_capital_mes=parametros_calculados.tasa_costo_capital_mes,
            )
            return vna

        # --- Búsqueda por bisección con tope dinámico ---
        a = 100.0
        b = 130.0
        max_b = 200.0
        paso_b = 10.0
        tol = 1e-6
        max_iter = 50
        vna_a = evaluar_vna(a)
        vna_b = evaluar_vna(b)

        # Si no hay cruce, aumentar b dinámicamente
        while vna_a * vna_b > 0 and b < max_b:
            b += paso_b
            vna_b = evaluar_vna(b)
        if abs(vna_a) < tol:
            return a
        if abs(vna_b) < tol:
            return b
        if vna_a * vna_b > 0:
            # No hay cruce de signo, devolvemos el mejor de los extremos
            return a if abs(vna_a) < abs(vna_b) else b
        for _ in range(max_iter):
            c = (a + b) / 2.0
            vna_c = evaluar_vna(c)
            if abs(vna_c) < tol:
                return c
            if vna_a * vna_c < 0:
                b = c
                vna_b = vna_c
            else:
                a = c
                vna_a = vna_c
            if abs(b - a) < tol:
                break

        if abs(vna_a) < abs(vna_b):
            # print(f"Porcentaje óptimo A: {a:.5f}% con VNA={vna_a:.10f}")
            return a
        else:
            # print(f"Porcentaje óptimo B: {b:.5f}% con VNA={vna_b:.10f}")
            return b

    def _calcular_trea(self, periodo_pago_primas, prima, porcentaje_devolucion_optimo):
        return calcular_trea(periodo_pago_primas, prima, porcentaje_devolucion_optimo)

    def calcular_aporte_total(self, periodo_pago_primas, prima):
        return periodo_pago_primas * prima * 12

    def calcular_devolucion_total(
        self,
        tasa_frecuencia_seleccionada,
        suma_asegurada,
        frecuencia_pago_primas,
        periodo_pago_primas,
        porcentaje_devolucion_optimo,
    ):

        _frecuencia_pago_primas = frecuencia_meses(frecuencia_pago_primas)
        _porcentaje_devolucion_optimo = porcentaje_devolucion_optimo / 100

        return (
            tasa_frecuencia_seleccionada * suma_asegurada * 12 / _frecuencia_pago_primas
        ) * (periodo_pago_primas * _porcentaje_devolucion_optimo)

    def calcular_ganancia_total(self, aporte_total, devolucion_total):
        return devolucion_total - aporte_total
