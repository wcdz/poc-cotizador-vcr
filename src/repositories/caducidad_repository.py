from abc import ABC, abstractmethod
import json
import os
from typing import Dict, Any, List, Optional
from pathlib import Path


class CaducidadRepository(ABC):
    """Interfaz abstracta para el repositorio de caducidad"""
    
    @abstractmethod
    def get_caducidad_data(self) -> List[Dict[str, Any]]:
        """Obtiene todos los datos de caducidad como una lista de diccionarios"""
        pass
    
    @abstractmethod
    def get_caducidad_by_anio(self, anio: int) -> Dict[str, Any]:
        """Obtiene los datos de caducidad para un año específico"""
        pass
    
    @abstractmethod
    def get_caducidad_valor(self, anio: int, plazo: int) -> float:
        """Obtiene el valor de caducidad para un año y plazo específicos"""
        pass
    
    @abstractmethod
    def get_caducidad_mensual_data(self) -> Dict[str, Any]:
        """Obtiene todos los datos de caducidad mensual como un diccionario"""
        pass
    
    @abstractmethod
    def get_caducidad_mensual_valor(self, anio: int, plazo: int) -> float:
        """Obtiene el valor de caducidad mensual para un año y plazo específicos"""
        pass


class JsonCaducidadRepository(CaducidadRepository):
    """Implementación del repositorio de caducidad usando archivo JSON"""
    
    def __init__(self, base_path: str = None, producto: str = "rumbo"):
        """
        Inicializa el repositorio de caducidad
        
        Args:
            base_path: Ruta base para los archivos JSON (optional)
            producto: Nombre del producto (default: "rumbo")
        """
        if base_path:
            self.base_path = Path(base_path)
        else:
            # Ruta por defecto: raíz del proyecto / assets / producto
            self.base_path = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) / "assets" / producto.lower()
        
        self.caducidad_path = self.base_path / "caducidad.json"
        self.caducidad_mensual_path = self.base_path / "caducidad_mensual.json"
        self._cache = None
        self._cache_mensual = None
    
    def get_caducidad_data(self) -> List[Dict[str, Any]]:
        """
        Carga los datos de caducidad desde el archivo JSON
        Retorna todo el contenido como una lista de diccionarios
        """
        # Si ya está en caché, devolver directamente
        if self._cache is not None:
            return self._cache
        
        if not self.caducidad_path.exists():
            self._cache = []
            return []
        
        try:
            with open(self.caducidad_path, "r", encoding="utf-8") as f:
                caducidad_data = json.load(f)
                self._cache = caducidad_data
                return caducidad_data
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error al cargar datos de caducidad: {e}")
            self._cache = []
            return []
    
    def get_caducidad_mensual_data(self) -> Dict[str, Any]:
        """
        Carga los datos de caducidad mensual desde el archivo JSON
        Retorna todo el contenido como un diccionario
        
        Returns:
            Diccionario con los datos de caducidad mensual
        """
        # Si ya está en caché, devolver directamente
        if self._cache_mensual is not None:
            return self._cache_mensual
        
        if not self.caducidad_mensual_path.exists():
            self._cache_mensual = {}
            return {}
        
        try:
            with open(self.caducidad_mensual_path, "r", encoding="utf-8") as f:
                caducidad_data = json.load(f)
                self._cache_mensual = caducidad_data
                return caducidad_data
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error al cargar datos de caducidad mensual: {e}")
            self._cache_mensual = {}
            return {}
    
    def get_caducidad_by_anio(self, anio: int) -> Dict[str, Any]:
        """
        Obtiene los datos de caducidad para un año específico
        
        Args:
            anio: Año para el cual se quieren obtener los datos de caducidad
            
        Returns:
            Diccionario con los datos de caducidad del año solicitado
            
        Raises:
            ValueError: Si no se encuentra el año especificado
        """
        caducidad_data = self.get_caducidad_data()
        
        for item in caducidad_data:
            if item["año"] == anio:
                return item
        
        raise ValueError(f"No se encontraron datos de caducidad para el año {anio}")
    
    def get_caducidad_valor(self, anio: int, plazo: int) -> float:
        """
        Obtiene el valor de caducidad para un año y plazo específicos
        
        Args:
            anio: Año para el cual se quiere obtener el valor
            plazo: Plazo para el cual se quiere obtener el valor
            
        Returns:
            Valor de caducidad como porcentaje (flotante)
            
        Raises:
            ValueError: Si no se encuentra el año o plazo especificado
        """
        try:
            item = self.get_caducidad_by_anio(anio)
            plazos = item.get("plazos", {})
            plazo_str = str(plazo)
            
            if plazo_str in plazos:
                return float(plazos[plazo_str])
            
            raise ValueError(f"No se encontró el plazo {plazo} para el año {anio}")
            
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Error al obtener valor de caducidad: {str(e)}")
    
    def get_caducidad_mensual_valor(self, anio: int, plazo: int) -> float:
        """
        Obtiene el valor de caducidad mensual para un año y plazo específicos
        
        Args:
            anio: Año para el cual se quiere obtener el valor
            plazo: Plazo para el cual se quiere obtener el valor
            
        Returns:
            Valor de caducidad mensual como porcentaje (flotante)
            
        Raises:
            ValueError: Si no se encuentra el año o plazo especificado
        """
        try:
            caducidad_mensual = self.get_caducidad_mensual_data()
            anio_str = str(anio)
            plazo_str = str(plazo)
            
            # Verificar si existe el año en los datos
            if anio_str in caducidad_mensual:
                plazos = caducidad_mensual[anio_str]
                
                # Verificar si existe el plazo para ese año
                if plazo_str in plazos:
                    return float(plazos[plazo_str])
            
            raise ValueError(f"No se encontró el valor de caducidad mensual para el año {anio} y plazo {plazo}")
            
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Error al obtener valor de caducidad mensual: {str(e)}")
    
    def limpiar_cache(self):
        """Limpia la caché de datos de caducidad"""
        self._cache = None
        self._cache_mensual = None


# Instancia global del repositorio
caducidad_repository = JsonCaducidadRepository() 