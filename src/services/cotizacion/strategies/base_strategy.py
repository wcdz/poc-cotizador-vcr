from abc import ABC, abstractmethod
from src.models.schemas.cotizacion_schema import CotizacionInput, CotizacionOutput


class CotizacionStrategy(ABC):
    """Estrategia base para cotización de diferentes productos"""
    
    @abstractmethod
    def execute(self, cotizacion_input: CotizacionInput) -> CotizacionOutput:
        """
        Ejecuta la estrategia de cotización para un producto específico
        
        Args:
            cotizacion_input: Datos de entrada para la cotización
            
        Returns:
            CotizacionOutput: Resultado de la cotización
        """
        pass
    
    @abstractmethod
    def get_product_name(self) -> str:
        """Retorna el nombre del producto que maneja esta estrategia"""
        pass 