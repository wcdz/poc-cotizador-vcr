from .base_step import PipelineStep
from ..cotizacion_context import CotizacionContext
from src.models.schemas.cotizacion_schema import CotizacionOutput, TipoProducto


class ResponseBuildingStep(PipelineStep):
    """Paso de construcción de la respuesta final"""
    
    def __init__(self):
        super().__init__("ResponseBuilding")
    
    def process(self, context: CotizacionContext) -> CotizacionContext:
        """Construye la respuesta final según el tipo de producto"""
        
        # Crear la respuesta base
        context.output = CotizacionOutput(
            producto=context.input.producto,
            parametros_entrada=context.input.parametros,
            parametros_almacenados=context.parametros_almacenados,
            parametros_calculados=context.parametros_calculados,
        )
        
        # Añadir campos específicos según el producto
        if context.input.producto == TipoProducto.RUMBO:
            context = self._build_rumbo_response(context)
        elif context.input.producto == TipoProducto.ENDOSOS:
            context = self._build_endosos_response(context)
        
        return context
    
    def _build_rumbo_response(self, context: CotizacionContext) -> CotizacionContext:
        """Construye respuesta específica para RUMBO"""
        
        # ✅ CORRECCIÓN: Crear nuevo objeto ParametrosRumbo limpio en lugar de diccionario
        from src.models.schemas.cotizacion_schema import ParametrosRumbo
        
        parametros_limpios = ParametrosRumbo(
            edad_actuarial=context.input.parametros.edad_actuarial,
            periodo_vigencia=context.input.parametros.periodo_vigencia,
            periodo_pago_primas=context.input.parametros.periodo_pago_primas,
            sexo=context.input.parametros.sexo,
            fumador=context.input.parametros.fumador,
            prima=context.input.parametros.prima,
            # Omitir campos que no queremos en la respuesta:
            # suma_asegurada, porcentaje_devolucion, moneda, frecuencia_pago_primas
        )
        
        context.output.parametros_entrada = parametros_limpios
        
        # Construir datos específicos de RUMBO
        if context.porcentaje_devolucion_optimo and context.trea:
            rumbo_data = {
                "porcentaje_devolucion": str(round(context.porcentaje_devolucion_optimo, 2)),
                "trea": str(round(context.trea, 2)),
                "aporte_total": str(context.aporte_total),
                "devolucion_total": str(round(context.devolucion_total, 2)),
                "ganancia_total": str(round(context.ganancia_total, 2)),
                "tabla_devolucion": str(context.tabla_devolucion),
            }
            context.output.rumbo = rumbo_data
        else:
            rumbo_data = {
                "porcentaje_devolucion": "",
                "trea": "",
            }
            context.output.rumbo = rumbo_data
        
        return context
    
    def _build_endosos_response(self, context: CotizacionContext) -> CotizacionContext:
        """Construye respuesta específica para ENDOSOS"""
        
        endosos_data = {"prima": ""}
        context.output.endosos = endosos_data
        
        return context 