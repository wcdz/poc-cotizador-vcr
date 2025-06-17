from .base_step import PipelineStep
from ..cotizacion_context import CotizacionContext


class ValidationStep(PipelineStep):
    """Paso de validación de parámetros de entrada"""
    
    def __init__(self):
        super().__init__("Validation")
    
    def process(self, context: CotizacionContext) -> CotizacionContext:
        """Valida que los parámetros correspondan al producto"""
        
        # Validar que los parámetros correspondan al producto
        context.input.validate_product_parameters()
        
        # Extraer datos básicos
        context.periodo_vigencia = context.input.parametros.periodo_vigencia
        context.periodo_pago_primas = context.input.parametros.periodo_pago_primas
        
        # Validaciones adicionales específicas
        if context.input.parametros.edad_actuarial < 0:
            context.errors.append("Edad actuarial debe ser positiva")
            
        if context.periodo_vigencia <= 0:
            context.errors.append("Periodo de vigencia debe ser positivo")
            
        if context.periodo_pago_primas <= 0:
            context.errors.append("Periodo de pago de primas debe ser positivo")
            
        # Log de validación exitosa
        context.debug_info["validation_passed"] = len(context.errors) == 0
        
        return context 