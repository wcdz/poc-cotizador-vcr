from .cotizacion_context import CotizacionContext
from .steps import (
    ValidationStep,
    ParameterLoadingStep,
    ActuarialCalculationStep,
    OptimizationStep,
    ResponseBuildingStep
)
from src.models.schemas.cotizacion_schema import CotizacionInput, CotizacionOutput


class CotizacionPipeline:
    """Pipeline principal que orquesta todos los pasos de cotización"""
    
    def __init__(self):
        self.steps = self._build_pipeline()
    
    def _build_pipeline(self):
        """Construye la cadena de pasos del pipeline"""
        validation = ValidationStep()
        parameter_loading = ParameterLoadingStep()
        actuarial_calculation = ActuarialCalculationStep()
        optimization = OptimizationStep()
        response_building = ResponseBuildingStep()
        
        # Encadenar los pasos
        validation.set_next(parameter_loading)\
                 .set_next(actuarial_calculation)\
                 .set_next(optimization)\
                 .set_next(response_building)
        
        return validation
    
    def execute(self, cotizacion_input: CotizacionInput) -> CotizacionOutput:
        """
        Ejecuta el pipeline completo de cotización
        
        Args:
            cotizacion_input: Datos de entrada para la cotización
            
        Returns:
            CotizacionOutput: Resultado de la cotización
            
        Raises:
            Exception: Si hay errores en algún paso del pipeline
        """
        # Crear contexto inicial
        context = CotizacionContext(input=cotizacion_input)
        
        try:
            # Ejecutar pipeline
            context = self.steps.execute(context)
            
            # Verificar si hay errores
            if context.errors:
                error_msg = f"Errores en el pipeline: {'; '.join(context.errors)}"
                raise Exception(error_msg)
            
            # Verificar que tenemos output
            if not context.output:
                raise Exception("El pipeline no generó output")
            
            return context.output
            
        except Exception as e:
            # Log del error para debugging
            context.debug_info["pipeline_error"] = str(e)
            context.debug_info["pipeline_failed_at"] = self._find_failed_step(context)
            raise Exception(f"Error en pipeline de cotización: {str(e)}")
    
    def _find_failed_step(self, context: CotizacionContext) -> str:
        """Encuentra en qué paso falló el pipeline"""
        steps = ["Validation", "ParameterLoading", "ActuarialCalculation", "Optimization", "ResponseBuilding"]
        
        for step in steps:
            if f"{step}_start" in context.debug_info and f"{step}_completed" not in context.debug_info:
                return step
        
        return "Unknown"
    
    def get_debug_info(self, cotizacion_input: CotizacionInput) -> dict:
        """
        Ejecuta el pipeline y retorna información de debug
        Útil para testing y diagnostics
        """
        context = CotizacionContext(input=cotizacion_input)
        
        try:
            context = self.steps.execute(context)
        except Exception as e:
            context.debug_info["final_error"] = str(e)
        
        return {
            "debug_info": context.debug_info,
            "errors": context.errors,
            "warnings": context.warnings,
            "context_summary": {
                "has_parametros_almacenados": context.parametros_almacenados is not None,
                "has_parametros_calculados": context.parametros_calculados is not None,
                "has_expuestos_mes": context.expuestos_mes is not None,
                "has_flujo_accionista": context.flujo_accionista is not None,
                "has_porcentaje_optimo": context.porcentaje_devolucion_optimo is not None,
                "has_output": context.output is not None,
            }
        } 