from abc import ABC, abstractmethod
from typing import Optional
from ..cotizacion_context import CotizacionContext


class PipelineStep(ABC):
    """Clase base abstracta para los pasos del pipeline de cotización"""
    
    def __init__(self, name: str):
        self.name = name
        self.next_step: Optional['PipelineStep'] = None
    
    def set_next(self, step: 'PipelineStep') -> 'PipelineStep':
        """Establece el próximo paso en el pipeline"""
        self.next_step = step
        return step
    
    def execute(self, context: CotizacionContext) -> CotizacionContext:
        """Ejecuta este paso y el siguiente si existe"""
        try:
            context.debug_info[f"{self.name}_start"] = True
            context = self.process(context)
            context.debug_info[f"{self.name}_completed"] = True
            
            if self.next_step:
                return self.next_step.execute(context)
            return context
            
        except Exception as e:
            context.errors.append(f"Error en {self.name}: {str(e)}")
            context.debug_info[f"{self.name}_error"] = str(e)
            raise
    
    @abstractmethod
    def process(self, context: CotizacionContext) -> CotizacionContext:
        """Lógica específica del paso - debe ser implementada por las subclases"""
        pass 