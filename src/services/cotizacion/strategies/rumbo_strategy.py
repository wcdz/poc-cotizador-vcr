from .base_strategy import CotizacionStrategy
from ..pipeline import CotizacionPipeline
from src.models.schemas.cotizacion_schema import CotizacionInput, CotizacionOutput, TipoProducto


class RumboStrategy(CotizacionStrategy):
    """Estrategia de cotización para el producto RUMBO"""
    
    def __init__(self):
        self.pipeline = CotizacionPipeline()
    
    def execute(self, cotizacion_input: CotizacionInput) -> CotizacionOutput:
        """
        Ejecuta la cotización para producto RUMBO
        
        Args:
            cotizacion_input: Datos de entrada para RUMBO
            
        Returns:
            CotizacionOutput: Resultado con optimización de porcentaje de devolución
        """
        # Validar que es producto RUMBO
        if cotizacion_input.producto != TipoProducto.RUMBO:
            raise ValueError(f"RumboStrategy solo maneja producto RUMBO, recibido: {cotizacion_input.producto}")
        
        # Ejecutar pipeline estándar
        return self.pipeline.execute(cotizacion_input)
    
    def get_product_name(self) -> str:
        """Retorna el nombre del producto"""
        return "RUMBO"
    
    def get_debug_info(self, cotizacion_input: CotizacionInput) -> dict:
        """Retorna información de debug específica para RUMBO"""
        debug_info = self.pipeline.get_debug_info(cotizacion_input)
        debug_info["strategy"] = "RumboStrategy"
        debug_info["product"] = "RUMBO"
        return debug_info 