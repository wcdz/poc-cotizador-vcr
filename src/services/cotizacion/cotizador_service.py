from typing import Dict, Any, List
from src.models.schemas.cotizacion_schema import (
    CotizacionInput,
    CotizacionOutput,
    TipoProducto,
    ParametrosRumbo,
)
from .strategies import CotizacionStrategy, RumboStrategy, EndososStrategy
from src.repositories.periodos_cotizacion_repository import (
    JsonPeriodosCotizacionRepository,
)


class CotizadorService:
    """
    Servicio unificado para cotizaciones de distintos productos

    Utiliza el patrón Strategy para manejar diferentes tipos de productos
    y el patrón Pipeline para procesar los cálculos de manera ordenada.

    ¡ANTES tenía 380 líneas de código en un solo método!
    ¡AHORA tiene 15 líneas en el método principal! 🚀
    """

    def __init__(self):
        self.strategies = self._initialize_strategies()

    def _initialize_strategies(self) -> Dict[TipoProducto, CotizacionStrategy]:
        """Inicializa las estrategias disponibles para cada producto"""
        return {
            TipoProducto.RUMBO: RumboStrategy(),
            TipoProducto.ENDOSOS: EndososStrategy(),
            # Fácil agregar más productos aquí:
            # TipoProducto.VIDA: VidaStrategy(),
        }

    def cotizar(self, cotizacion_input: CotizacionInput) -> CotizacionOutput:
        """
        🔥 EL MÉTODO QUE ANTES ERA UN MONSTRUO DE 380 LÍNEAS
        🚀 AHORA ES HERMOSO Y TIENE SOLO 15 LÍNEAS

        Realiza la cotización para el producto especificado.
        Utiliza la estrategia correspondiente según el tipo de producto.

        Args:
            cotizacion_input: Datos de entrada para la cotización

        Returns:
            CotizacionOutput: Resultado de la cotización

        Raises:
            ValueError: Si el producto no es soportado
            Exception: Si hay errores en el proceso de cotización
        """
        # 1. Obtener estrategia
        strategy = self._get_strategy(cotizacion_input.producto)

        # 2. Ejecutar cotización
        return strategy.execute(cotizacion_input)

    def get_coleccion_cotizacion(self, cotizacion_input: CotizacionInput) -> Dict[str, Any]:
        """
        🚀 MÉTODO REFACTORIZADO SIGUIENDO EL PATRÓN STRATEGY
        
        Obtiene una colección de cotizaciones para diferentes períodos.
        Delega la lógica específica del producto a la estrategia correspondiente.

        Args:
            cotizacion_input: Datos de entrada para la cotización

        Returns:
            Dict con las cotizaciones para todos los períodos disponibles

        Raises:
            ValueError: Si el producto no es soportado
        """
        # 1. Obtener estrategia
        strategy = self._get_strategy(cotizacion_input.producto)
        
        # 2. Delegar la lógica de colección a la estrategia
        return strategy.execute_collection(cotizacion_input)

    def get_periodos_disponibles(self, cotizacion_input: CotizacionInput) -> List[int]:
        """
        Obtiene los períodos disponibles para una cotización específica.
        Útil para consultas independientes de períodos.
        """
        if cotizacion_input.producto == TipoProducto.RUMBO:
            if isinstance(cotizacion_input.parametros, ParametrosRumbo):
                periodos_repo = JsonPeriodosCotizacionRepository()
                return periodos_repo.get_periodos_disponibles(cotizacion_input.parametros.prima)
        
        # Para otros productos, retornar lista vacía o implementar lógica específica
        return []

    def _get_strategy(self, producto: TipoProducto) -> CotizacionStrategy:
        """Obtiene la estrategia correspondiente al producto"""
        if producto not in self.strategies:
            available_products = list(self.strategies.keys())
            raise ValueError(
                f"Producto {producto} no soportado. "
                f"Productos disponibles: {available_products}"
            )

        return self.strategies[producto]

    def get_supported_products(self) -> list:
        """Retorna la lista de productos soportados"""
        return list(self.strategies.keys())

    def get_debug_info(self, cotizacion_input: CotizacionInput) -> dict:
        """
        Obtiene información de debug del proceso de cotización
        Útil para testing y diagnostics
        """
        try:
            strategy = self._get_strategy(cotizacion_input.producto)
            return strategy.get_debug_info(cotizacion_input)
        except Exception as e:
            return {
                "error": str(e),
                "producto": cotizacion_input.producto,
                "supported_products": self.get_supported_products(),
            }
