from .base_strategy import CotizacionStrategy
from ..pipeline import CotizacionPipeline
from typing import Dict, Any
from src.models.schemas.cotizacion_schema import CotizacionInput, CotizacionOutput, TipoProducto


class EndososStrategy(CotizacionStrategy):
    """Estrategia de cotización para el producto ENDOSOS"""
    
    def __init__(self):
        self.pipeline = CotizacionPipeline()
    
    def execute(self, cotizacion_input: CotizacionInput) -> CotizacionOutput:
        """
        Ejecuta la cotización para producto ENDOSOS
        
        Args:
            cotizacion_input: Datos de entrada para ENDOSOS
            
        Returns:
            CotizacionOutput: Resultado específico para ENDOSOS
        """
        # Validar que es producto ENDOSOS
        if cotizacion_input.producto != TipoProducto.ENDOSOS:
            raise ValueError(f"EndososStrategy solo maneja producto ENDOSOS, recibido: {cotizacion_input.producto}")
        
        # Ejecutar pipeline estándar
        return self.pipeline.execute(cotizacion_input)
    
    def execute_collection(self, cotizacion_input: CotizacionInput) -> Dict[str, Any]:
        """
        Para ENDOSOS, la colección podría ser diferente (ej: diferentes porcentajes de devolución)
        Por ahora, ejecuta una sola cotización
        
        Args:
            cotizacion_input: Datos de entrada para ENDOSOS
            
        Returns:
            Dict con la cotización de ENDOSOS (sin múltiples períodos)
        """
        # Validar que es producto ENDOSOS
        if cotizacion_input.producto != TipoProducto.ENDOSOS:
            raise ValueError(f"EndososStrategy solo maneja producto ENDOSOS, recibido: {cotizacion_input.producto}")
        
        # Para ENDOSOS, ejecutar una sola cotización
        cotizacion_output = self.execute(cotizacion_input)
        
        return {
            "producto": "ENDOSOS",
            "cotizaciones": [
                {
                    "cotizacion": cotizacion_output.endosos if cotizacion_output.endosos else cotizacion_output
                }
            ],
            "mensaje": "ENDOSOS maneja cotización individual, no colecciones por períodos"
        }
    
    def get_product_name(self) -> str:
        """Retorna el nombre del producto"""
        return "ENDOSOS"
    
    def get_debug_info(self, cotizacion_input: CotizacionInput) -> dict:
        """Retorna información de debug específica para ENDOSOS"""
        debug_info = self.pipeline.get_debug_info(cotizacion_input)
        debug_info["strategy"] = "EndososStrategy"
        debug_info["product"] = "ENDOSOS"
        return debug_info 