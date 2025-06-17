from .base_step import PipelineStep
from ..cotizacion_context import CotizacionContext
from src.models.schemas.cotizacion_schema import TipoProducto
from src.models.products.rumbo.rumbo import Rumbo
from src.services.expuestos_mes_service import ExpuestosMesService
from src.services.gastos_service import GastosService
from src.services.flujo_resultado_service import FlujoResultadoService
from src.services.margen_solvencia_service import MargenSolvenciaService
from src.services.reserva_service import ReservaService


class OptimizationStep(PipelineStep):
    """Paso de optimización específico por producto"""
    
    def __init__(self):
        super().__init__("Optimization")
        # Inicializar servicios para Rumbo
        self.expuestos_mes_service = ExpuestosMesService()
        self.gastos_service = GastosService()
        self.flujo_resultado_service = FlujoResultadoService()
        self.margen_solvencia_service = MargenSolvenciaService()
        self.reserva_service = ReservaService()
        
        self.rumbo = Rumbo(
            self.expuestos_mes_service,
            self.flujo_resultado_service,
            self.gastos_service,
            self.reserva_service,
            self.margen_solvencia_service,
        )
    
    def process(self, context: CotizacionContext) -> CotizacionContext:
        """Ejecuta optimización según el tipo de producto"""
        
        if context.input.producto == TipoProducto.RUMBO:
            context = self._optimizar_rumbo(context)
        elif context.input.producto == TipoProducto.ENDOSOS:
            context = self._optimizar_endosos(context)
        # Agregar más productos aquí
        
        return context
    
    def _optimizar_rumbo(self, context: CotizacionContext) -> CotizacionContext:
        """Optimización específica para producto RUMBO"""
        
        # Calcular porcentaje de devolución óptimo
        context.porcentaje_devolucion_optimo = self.rumbo.calcular_porcentaje_devolucion_optimo(
            cotizacion_input=context.input,
            parametros_almacenados=context.parametros_almacenados,
            tasas_interes_data=context.tasas_interes_data,
            prima=context.prima,
            flujo_resultado_service=self.flujo_resultado_service,
            parametros_calculados=context.parametros_calculados,
            periodo_vigencia=context.periodo_vigencia,
            periodo_pago_primas=context.periodo_pago_primas,
            expuestos_mes=context.expuestos_mes,
            gastos=context.gastos,
            primas_recurrentes=context.primas_recurrentes,
            siniestros=context.siniestros,
            flujo_accionista=context.flujo_accionista,
            flujo_pasivo=context.flujo_pasivo,
            saldo_reserva=context.saldo_reserva,
            moce=context.moce,
            reserva_fin_año=context.reserva_fin_año,
            margen_solvencia=context.margen_solvencia,
            varianza_margen_solvencia=context.varianza_margen_solvencia,
            ingreso_total_inversiones=context.ingreso_total_inversiones,
            varianza_reserva=context.varianza_reserva,
            varianza_moce=context.varianza_moce,
            gastos_mantenimiento=context.gastos_mantenimiento,
            gasto_adquisicion=context.gasto_adquisicion,
            comision=context.comision,
            IR=context.IR,
            utilidad_pre_pi_ms=context.utilidad_pre_pi_ms,
        )
        
        if context.porcentaje_devolucion_optimo:
            # Calcular TREA
            context.trea = self.rumbo._calcular_trea(
                context.periodo_pago_primas, 
                context.prima, 
                context.porcentaje_devolucion_optimo
            )
            
            # Calcular aporte total
            context.aporte_total = self.rumbo.calcular_aporte_total(
                context.periodo_pago_primas, 
                context.prima
            )
            
            # Calcular devolución total
            context.devolucion_total = self.rumbo.calcular_devolucion_total(
                tasa_frecuencia_seleccionada=context.parametros_calculados.tasa_frecuencia_seleccionada,
                suma_asegurada=context.suma_asegurada,
                frecuencia_pago_primas=context.input.parametros.frecuencia_pago_primas,
                periodo_pago_primas=context.periodo_pago_primas,
                porcentaje_devolucion_optimo=context.porcentaje_devolucion_optimo,
            )
            
            # Calcular ganancia total
            context.ganancia_total = self.rumbo.calcular_ganancia_total(
                aporte_total=context.aporte_total,
                devolucion_total=context.devolucion_total,
            )
            
            context.tabla_devolucion = self.rumbo.calcular_tabla_devolucion(
                periodo_vigencia=context.periodo_vigencia,
                porcentaje_devolucion_optimo=context.porcentaje_devolucion_optimo,
            )
        
        return context
    
    def _optimizar_endosos(self, context: CotizacionContext) -> CotizacionContext:
        """Optimización específica para producto ENDOSOS"""
        # TODO: Implementar lógica de optimización para ENDOSOS
        context.warnings.append("Optimización para ENDOSOS no implementada aún")
        return context 