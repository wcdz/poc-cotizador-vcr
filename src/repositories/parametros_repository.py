from abc import ABC, abstractmethod
import json
import os
from typing import Dict, Any, Optional, List
from pathlib import Path


class ParametrosRepository(ABC):
    """Interfaz abstracta para el repositorio de parámetros"""
    
    @abstractmethod
    def get_parametros_by_producto(self, producto: str) -> Dict[str, Any]:
        """Obtiene todos los parámetros para un producto específico"""
        pass
    
    @abstractmethod
    def get_parametro(self, producto: str, nombre_parametro: str, valor_default: Any = None) -> Any:
        """Obtiene un parámetro específico para un producto"""
        pass
    
    @abstractmethod
    def guardar_parametro(self, producto: str, nombre_parametro: str, valor: Any) -> bool:
        """Guarda un parámetro específico para un producto"""
        pass


class JsonParametrosRepository(ParametrosRepository):
    """Implementación del repositorio de parámetros usando archivos JSON"""
    
    def __init__(self, base_path: str = None):
        """
        Inicializa el repositorio de parámetros
        
        Args:
            base_path: Ruta base para los archivos JSON (optional)
        """
        if base_path:
            self.base_path = Path(base_path)
        else:
            # Ruta por defecto: raíz del proyecto / assets
            self.base_path = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) / "assets"
        
        # Cache para evitar múltiples lecturas de disco
        self._cache: Dict[str, Dict[str, Any]] = {}
    
    def _get_parametros_path(self, producto: str) -> Path:
        """Obtiene la ruta al archivo de parámetros para un producto"""
        return self.base_path / producto.lower() / "parametros.json"
    
    def _cargar_parametros(self, producto: str) -> Dict[str, Any]:
        """
        Carga los parámetros desde el archivo JSON
        Simula una consulta a la base de datos
        """
        producto = producto.lower()
        
        # Si ya está en caché, devolver directamente
        if producto in self._cache:
            return self._cache[producto]
        
        # Simular latencia de base de datos (opcional, para pruebas)
        # import time
        # time.sleep(0.1)
        
        parametros_path = self._get_parametros_path(producto)
        
        if not parametros_path.exists():
            self._cache[producto] = {}
            return {}
        
        try:
            with open(parametros_path, "r", encoding="utf-8") as f:
                parametros = json.load(f)
                self._cache[producto] = parametros
                return parametros
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error al cargar parámetros para {producto}: {e}")
            self._cache[producto] = {}
            return {}
    
    def get_parametros_by_producto(self, producto: str) -> Dict[str, Any]:
        """
        Obtiene todos los parámetros para un producto
        Simula un SELECT * FROM parametros WHERE producto = ?
        """
        return self._cargar_parametros(producto)
    
    def get_parametro(self, producto: str, nombre_parametro: str, valor_default: Any = None) -> Any:
        """
        Obtiene un parámetro específico para un producto
        Simula un SELECT valor FROM parametros WHERE producto = ? AND nombre = ?
        """
        parametros = self._cargar_parametros(producto)
        return parametros.get(nombre_parametro, valor_default)
    
    def guardar_parametro(self, producto: str, nombre_parametro: str, valor: Any) -> bool:
        """
        Guarda un parámetro específico para un producto
        Simula un UPDATE parametros SET valor = ? WHERE producto = ? AND nombre = ?
        """
        producto = producto.lower()
        parametros = self._cargar_parametros(producto)
        
        # Actualizar el valor
        parametros[nombre_parametro] = valor
        
        # Actualizar caché
        self._cache[producto] = parametros
        
        # Guardar en disco (simulación de COMMIT)
        parametros_path = self._get_parametros_path(producto)
        os.makedirs(parametros_path.parent, exist_ok=True)
        
        try:
            with open(parametros_path, "w", encoding="utf-8") as f:
                json.dump(parametros, f, indent=2)
            return True
        except IOError as e:
            print(f"Error al guardar parámetros para {producto}: {e}")
            return False
    
    def limpiar_cache(self):
        """Limpia la caché de parámetros (útil para pruebas)"""
        self._cache = {}


# Instancia global del repositorio
parametros_repository = JsonParametrosRepository() 