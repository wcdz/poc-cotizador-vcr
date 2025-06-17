from .base_strategy import CotizacionStrategy
from ..pipeline import CotizacionPipeline
from typing import Dict, Any, List
from copy import deepcopy
from src.models.schemas.cotizacion_schema import CotizacionInput, CotizacionOutput, TipoProducto, ParametrosRumbo
from src.repositories.periodos_cotizacion_repository import JsonPeriodosCotizacionRepository


class RumboStrategy(CotizacionStrategy):
    """Estrategia de cotización para el producto RUMBO"""
    
    def __init__(self):
        self.pipeline = CotizacionPipeline()
        self.periodos_repo = JsonPeriodosCotizacionRepository()
    
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
    
    def execute_collection(self, cotizacion_input: CotizacionInput) -> Dict[str, Any]:
        """
        🚀 IMPLEMENTACIÓN DEL PATRÓN STRATEGY PARA COLECCIONES
        
        Ejecuta múltiples cotizaciones para diferentes períodos disponibles
        según el monto de la prima del producto RUMBO
        
        Args:
            cotizacion_input: Datos de entrada base para RUMBO
            
        Returns:
            Dict con todas las cotizaciones organizadas por período
        """
        # Validar que es producto RUMBO
        if cotizacion_input.producto != TipoProducto.RUMBO:
            raise ValueError(f"RumboStrategy solo maneja producto RUMBO, recibido: {cotizacion_input.producto}")
        
        # Validar que tiene parámetros de RUMBO
        if not isinstance(cotizacion_input.parametros, ParametrosRumbo):
            raise ValueError("Los parámetros deben ser de tipo ParametrosRumbo")
        
        # Obtener períodos disponibles para la prima
        prima = cotizacion_input.parametros.prima
        periodos_disponibles = self.periodos_repo.get_periodos_disponibles(prima)
        
        if not periodos_disponibles:
            return {
                "prima": prima,
                "periodos_disponibles": [],
                "cotizaciones": [],
                "mensaje": "No hay períodos disponibles para esta prima"
            }
        
        # Generar cotizaciones para cada período
        cotizaciones_resultado = []
        
        for periodo in periodos_disponibles:
            try:
                # Crear copia profunda para evitar mutaciones
                cotizacion_periodo = deepcopy(cotizacion_input)
                
                # Actualizar períodos
                cotizacion_periodo.parametros.periodo_vigencia = periodo
                cotizacion_periodo.parametros.periodo_pago_primas = periodo
                
                # Ejecutar cotización individual
                cotizacion_output = self.execute(cotizacion_periodo)
                
                cotizaciones_resultado.append({
                    "periodo": periodo,
                    "cotizacion": cotizacion_output.rumbo if cotizacion_output.rumbo else cotizacion_output
                })
                
            except Exception as e:
                cotizaciones_resultado.append({
                    "periodo": periodo,
                    "error": str(e)
                })
        
        return {
            "prima": prima,
            "periodos_disponibles": periodos_disponibles,
            "cotizaciones": cotizaciones_resultado,
            "total_cotizaciones": len(cotizaciones_resultado)
        }
    
    def get_product_name(self) -> str:
        """Retorna el nombre del producto"""
        return "RUMBO"
    
    def get_debug_info(self, cotizacion_input: CotizacionInput) -> dict:
        """Retorna información de debug específica para RUMBO"""
        debug_info = self.pipeline.get_debug_info(cotizacion_input)
        debug_info["strategy"] = "RumboStrategy"
        debug_info["product"] = "RUMBO"
        return debug_info 