from abc import ABC, abstractmethod
import json
import os
from typing import Dict, Any, List, Optional
from pathlib import Path


class DevolucionRepository(ABC):
    """Interfaz abstracta para el repositorio de devolución"""
    
    @abstractmethod
    def get_devolucion_data(self) -> List[Dict[str, Any]]:
        """Obtiene todos los datos de devolución como una lista de diccionarios"""
        pass
    
    @abstractmethod
    def get_devolucion_by_anio_poliza(self, anio_poliza: int) -> Dict[str, Any]:
        """Obtiene los datos de devolución para un año específico de póliza"""
        pass
    
    @abstractmethod
    def get_devolucion_valor(self, anio_poliza: int, plazo_pago_primas: int) -> float:
        """Obtiene el valor de devolución para un año de póliza y plazo de pago de primas específicos"""
        pass


class JsonDevolucionRepository(DevolucionRepository):
    """Implementación del repositorio de devolución usando archivo JSON"""
    
    def __init__(self, base_path: str = None, producto: str = "rumbo"):
        """
        Inicializa el repositorio de devolución
        
        Args:
            base_path: Ruta base para los archivos JSON (optional)
            producto: Nombre del producto (default: "rumbo")
        """
        if base_path:
            self.base_path = Path(base_path)
        else:
            # Ruta por defecto: raíz del proyecto / assets / producto
            self.base_path = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) / "assets" / producto.lower()
        
        self.devolucion_path = self.base_path / "devolucion.json"
        self._cache = None
    
    def get_devolucion_data(self) -> List[Dict[str, Any]]:
        """
        Carga los datos de devolución desde el archivo JSON
        Retorna todo el contenido como una lista de diccionarios
        """
        # Si ya está en caché, devolver directamente
        if self._cache is not None:
            return self._cache
        
        if not self.devolucion_path.exists():
            self._cache = []
            return []
        
        try:
            with open(self.devolucion_path, "r", encoding="utf-8") as f:
                devolucion_data = json.load(f)
                self._cache = devolucion_data
                return devolucion_data
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error al cargar datos de devolución: {e}")
            self._cache = []
            return []
    
    def get_devolucion_by_anio_poliza(self, anio_poliza: int) -> Dict[str, Any]:
        """
        Obtiene los datos de devolución para un año específico de póliza
        
        Args:
            anio_poliza: Año de póliza para el cual se quieren obtener los datos de devolución
            
        Returns:
            Diccionario con los datos de devolución del año de póliza solicitado
            
        Raises:
            ValueError: Si no se encuentra el año de póliza especificado
        """
        devolucion_data = self.get_devolucion_data()
        
        for item in devolucion_data:
            if item["año_poliza"] == anio_poliza:
                return item
        
        raise ValueError(f"No se encontraron datos de devolución para el año de póliza {anio_poliza}")
    
    def get_devolucion_valor(self, anio_poliza: int, plazo_pago_primas: int) -> float:
        """
        Obtiene el valor de devolución para un año de póliza y plazo de pago de primas específicos
        
        Args:
            anio_poliza: Año de póliza para el cual se quiere obtener el valor
            plazo_pago_primas: Plazo de pago de primas para el cual se quiere obtener el valor
            
        Returns:
            Valor de devolución como porcentaje (flotante)
            
        Raises:
            ValueError: Si no se encuentra el año de póliza o plazo de pago de primas especificado
        """
        try:
            item = self.get_devolucion_by_anio_poliza(anio_poliza)
            plazos = item.get("plazo_pago_primas", {})
            plazo_str = str(plazo_pago_primas)
            
            if plazo_str in plazos:
                return float(plazos[plazo_str])
            
            raise ValueError(f"No se encontró el plazo de pago de primas {plazo_pago_primas} para el año de póliza {anio_poliza}")
            
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Error al obtener valor de devolución: {str(e)}")
    
    def limpiar_cache(self):
        """Limpia la caché de devolución (útil para pruebas)"""
        self._cache = None


# Instancia global del repositorio
devolucion_repository = JsonDevolucionRepository() 