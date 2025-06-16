"""
Clases auxiliares para optimizar los cálculos de Rumbo.
Separa la responsabilidad de evaluación VNA del algoritmo de optimización.
"""

from dataclasses import dataclass
from typing import Callable, Any, Dict
from src.core.constants import (
    PORCENTAJE_INICIAL, 
    PORCENTAJE_MAXIMO_INICIAL, 
    PORCENTAJE_LIMITE,
    PASO_INCREMENTO,
    TOLERANCIA, 
    MAX_ITERACIONES
)


@dataclass
class ParametrosOptimizacion:
    """Encapsula todos los parámetros necesarios para optimización"""
    cotizacion_input: Any
    parametros_almacenados: Any
    parametros_calculados: Any
    periodo_vigencia: int
    periodo_pago_primas: int
    prima: float
    flujo_resultado_service: Any


@dataclass 
class ResultadoOptimizacion:
    """Resultado de la optimización"""
    porcentaje_optimo: float
    vna_final: float
    iteraciones: int
    convergio: bool


class EvaluadorVNA:
    """
    Separar la evaluación VNA del algoritmo de optimización.
    Contiene toda la lógica que estaba en la función evaluar_vna anidada.
    """
    
    def __init__(self, params: ParametrosOptimizacion, servicios: Dict[str, Any]):
        self.params = params
        self.expuestos_mes = servicios['expuestos_mes']
        self.gastos_service = servicios['gastos']
        self.reserva_service = servicios['reserva']
        self.margen_solvencia_service = servicios['margen_solvencia']
        self.flujo_resultado_service = params.flujo_resultado_service
    
    def evaluar(self, porcentaje: float) -> float:
        """
        Evalúa el VNA para un porcentaje dado.
        Esta es toda la lógica que estaba en evaluar_vna().
        """
        # Calcular expuestos mes
        expuestos_mes = self.expuestos_mes.calcular_expuestos_mes(
            edad_actuarial=self.params.cotizacion_input.parametros.edad_actuarial,
            sexo=self.params.cotizacion_input.parametros.sexo,
            fumador=self.params.cotizacion_input.parametros.fumador,
            frecuencia_pago_primas=self.params.cotizacion_input.parametros.frecuencia_pago_primas,
            periodo_vigencia=self.params.periodo_vigencia,
            periodo_pago_primas=self.params.periodo_pago_primas,
            ajuste_mortalidad=self.params.parametros_almacenados.ajuste_mortalidad,
        )
        
        # Calcular siniestros
        siniestros = self.flujo_resultado_service.calcular_siniestros(
            expuestos_mes=expuestos_mes,
            suma_asegurada=self.params.parametros_almacenados.suma_asegurada_rumbo,
        )
        
        # Calcular primas recurrentes
        primas_recurrentes = self.flujo_resultado_service.calcular_primas_recurrentes(
            expuestos_mes=expuestos_mes,
            periodo_pago_primas=self.params.periodo_pago_primas,
            frecuencia_pago_primas=self.params.cotizacion_input.parametros.frecuencia_pago_primas,
            prima=self.params.prima,
        )
        
        # Calcular gastos
        gastos = self.gastos_service.calcular_gastos(
            periodo_vigencia=self.params.periodo_vigencia,
            periodo_pago_primas=self.params.periodo_pago_primas,
            prima=self.params.prima,
            expuestos_mes=expuestos_mes,
            frecuencia_pago_primas=self.params.cotizacion_input.parametros.frecuencia_pago_primas,
            mantenimiento_poliza=self.params.parametros_calculados.mantenimiento_poliza,
            moneda=self.params.parametros_almacenados.moneda,
            valor_dolar=self.params.parametros_almacenados.valor_dolar,
            valor_soles=self.params.parametros_almacenados.valor_soles,
            tiene_asistencia=self.params.parametros_almacenados.tiene_asistencia,
            costo_mensual_asistencia_funeraria=self.params.parametros_almacenados.costo_mensual_asistencia_funeraria,
            inflacion_mensual=self.params.parametros_calculados.inflacion_mensual,
        )
        
        # Calcular gastos mantenimiento
        gastos_mantenimiento = self.flujo_resultado_service.calcular_gastos_mantenimiento(
            gastos_mantenimiento=gastos,
        )
        
        # Calcular gasto adquisición
        gasto_adquisicion = self.flujo_resultado_service.calcular_gasto_adquisicion(
            gasto_adquisicion=self.params.parametros_almacenados.gasto_adquisicion,
        )
        
        # Calcular comisión
        comision = self.flujo_resultado_service.calcular_comision(
            primas_recurrentes=primas_recurrentes,
            asistencia=self.params.parametros_almacenados.tiene_asistencia,
            frecuencia_pago_primas=self.params.cotizacion_input.parametros.frecuencia_pago_primas,
            costo_asistencia_funeraria=self.params.parametros_almacenados.costo_mensual_asistencia_funeraria,
            expuestos_mes=expuestos_mes,
            comision=self.params.parametros_almacenados.comision,
        )
        
        # Calcular rescate
        rescate = self.reserva_service.calcular_rescate(
            periodo_vigencia=self.params.periodo_vigencia,
            prima=self.params.prima,
            fraccionamiento_primas=self.params.parametros_almacenados.fraccionamiento_primas,
            porcentaje_devolucion=porcentaje,
        )
        
        # Calcular rescates
        rescates = self.flujo_resultado_service.calcular_rescates(
            expuestos_mes=expuestos_mes,
            rescate=rescate,
        )
        
        # Calcular flujo pasivo
        flujo_pasivo_ = self.reserva_service.calcular_flujo_pasivo(
            siniestros,
            rescates,
            gastos_mantenimiento,
            comision,
            gasto_adquisicion,
            primas_recurrentes,
        )
        
        # Calcular saldo reserva
        saldo_reserva_ = self.reserva_service.calcular_saldo_reserva(
            flujo_pasivo_,
            self.params.parametros_calculados.tasa_interes_mensual,
            rescate,
            expuestos_mes,
        )
        
        # Calcular MOCE
        moce_ = self.reserva_service.calcular_moce(
            tasa_costo_capital_mensual=self.params.parametros_calculados.tasa_costo_capital_mensual,
            tasa_interes_mensual=self.params.parametros_calculados.tasa_interes_mensual,
            margen_reserva=self.params.parametros_almacenados.margen_solvencia,
            saldo_reserva=saldo_reserva_,
        )
        
        # Calcular reserva fin año
        reserva_fin_año_ = self.margen_solvencia_service.calcular_reserva_fin_año(
            saldo_reserva=saldo_reserva_,
            moce=moce_,
        )
        
        # Calcular margen solvencia
        margen_solvencia_ = self.margen_solvencia_service.calcular_margen_solvencia(
            reserva_fin_año=reserva_fin_año_,
            margen_solvencia_reserva=self.params.parametros_calculados.reserva,
        )
        
        # Calcular varianza margen solvencia
        varianza_margen_solvencia_ = (
            self.margen_solvencia_service.calcular_varianza_margen_solvencia(
                margen_solvencia=margen_solvencia_,
            )
        )
        
        # Calcular ingreso inversiones
        ingreso_inversiones_ = (
            self.margen_solvencia_service.calcular_ingreso_inversiones(
                reserva_fin_año=reserva_fin_año_,
                tasa_inversion=self.params.parametros_calculados.tasa_inversion,
            )
        )
        
        # Calcular ingresiones inversiones margen solvencia
        ingresiones_inversiones_margen_solvencia_ = (
            self.margen_solvencia_service.ingresiones_inversiones_margen_solvencia(
                margen_solvencia=margen_solvencia_,
                tasa_inversion=self.params.parametros_calculados.tasa_inversion,
            )
        )
        
        # Calcular ingreso total inversiones
        ingreso_total_inversiones_ = self.margen_solvencia_service.calcular_ingreso_total_inversiones(
            ingreso_inversiones=ingreso_inversiones_,
            ingresiones_inversiones_margen_solvencia=ingresiones_inversiones_margen_solvencia_,
        )
        
        # Calcular varianzas
        varianza_moce_ = self.reserva_service.calcular_varianza_moce(moce_)
        varianza_reserva_ = self.reserva_service.calcular_varianza_reserva(saldo_reserva_)
        
        # Calcular variación reserva
        variacion_reserva_ = self.flujo_resultado_service.calcular_variacion_reserva(
            varianza_reserva=varianza_reserva_,
            varianza_moce=varianza_moce_,
        )
        
        # Calcular utilidad pre
        utilidad_pre_ = self.flujo_resultado_service.calcular_utilidad_pre_pi_ms(
            primas_recurrentes,
            comision,
            gasto_adquisicion,
            gastos_mantenimiento,
            siniestros,
            rescates,
            variacion_reserva_,
        )
        
        # Calcular IR
        IR_ = self.flujo_resultado_service.calcular_IR(
            utilidad_pre_pi_ms=utilidad_pre_,
            impuesto_renta=self.params.parametros_almacenados.impuesto_renta,
        )
        
        # Calcular flujo accionista
        flujo_accionista_ = self.flujo_resultado_service.calcular_flujo_accionista(
            utilidad_pre_pi_ms=utilidad_pre_,
            varianza_margen_solvencia=varianza_margen_solvencia_,
            IR=IR_,
            ingreso_total_inversiones=ingreso_total_inversiones_,
        )
        
        # Calcular VNA final
        vna = self.flujo_resultado_service.auxiliar(
            flujo_accionista=flujo_accionista_,
            tasa_costo_capital_mes=self.params.parametros_calculados.tasa_costo_capital_mes,
        )
        
        return vna


class OptimizadorBiseccion:
    """
    Algoritmo de bisección separado y limpio.
    Contiene solo la lógica de optimización.
    """
    
    def __init__(self, evaluador: Callable[[float], float]):
        self.evaluar_vna = evaluador
    
    def optimizar(self) -> ResultadoOptimizacion:
        """
        Ejecuta el algoritmo de bisección.
        Retorna el resultado completo de la optimización.
        """
        # Parámetros del algoritmo
        a = PORCENTAJE_INICIAL
        b = PORCENTAJE_MAXIMO_INICIAL
        max_b = PORCENTAJE_LIMITE
        paso_b = PASO_INCREMENTO
        tol = TOLERANCIA
        max_iter = MAX_ITERACIONES
        
        # Evaluaciones iniciales
        vna_a = self.evaluar_vna(a)
        vna_b = self.evaluar_vna(b)
        iteraciones = 2
        
        # Buscar intervalo válido si no hay cambio de signo inicial
        while vna_a * vna_b > 0 and b < max_b:
            b += paso_b
            vna_b = self.evaluar_vna(b)
            iteraciones += 1
        
        # Verificar convergencia temprana
        if abs(vna_a) < tol:
            return ResultadoOptimizacion(a, vna_a, iteraciones, True)
        if abs(vna_b) < tol:
            return ResultadoOptimizacion(b, vna_b, iteraciones, True)
        
        # Si no hay cruce de signo, devolver mejor aproximación
        if vna_a * vna_b > 0:
            if abs(vna_a) < abs(vna_b):
                return ResultadoOptimizacion(a, vna_a, iteraciones, False)
            else:
                return ResultadoOptimizacion(b, vna_b, iteraciones, False)
        
        # Algoritmo de bisección principal
        for i in range(max_iter):
            c = (a + b) / 2.0
            vna_c = self.evaluar_vna(c)
            iteraciones += 1
            
            if abs(vna_c) < tol:
                return ResultadoOptimizacion(c, vna_c, iteraciones, True)
            
            if vna_a * vna_c < 0:
                b = c
                vna_b = vna_c
            else:
                a = c
                vna_a = vna_c
            
            if abs(b - a) < tol:
                break
        
        # Retornar mejor resultado final
        porcentaje_final = a if abs(vna_a) < abs(vna_b) else b
        vna_final = vna_a if abs(vna_a) < abs(vna_b) else vna_b
        convergio = iteraciones < max_iter
        
        return ResultadoOptimizacion(porcentaje_final, vna_final, iteraciones, convergio) 