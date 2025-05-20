from abc import ABC, abstractmethod
import json
import os
from typing import Dict, Any
from pathlib import Path


class TasaInteresRepository(ABC):
    """Interfaz abstracta para el repositorio de tasas de interés"""
    
    @abstractmethod
    def get_tasas_interes(self) -> Dict[str, Any]:
        """Obtiene todas las tasas de interés como un diccionario"""
        pass


class JsonTasaInteresRepository(TasaInteresRepository):
    """Implementación del repositorio de tasas de interés usando archivo JSON"""
    
    def __init__(self, base_path: str = None, producto: str = "rumbo"):
        """
        Inicializa el repositorio de tasas de interés
        
        Args:
            base_path: Ruta base para los archivos JSON (optional)
            producto: Nombre del producto (default: "rumbo")
        """
        if base_path:
            self.base_path = Path(base_path)
        else:
            # Ruta por defecto: raíz del proyecto / assets / producto
            self.base_path = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) / "assets" / producto.lower()
        
        self.tasas_path = self.base_path / "tasa_interes.json"
        self._cache = None
    
    def get_tasas_interes(self) -> Dict[str, Any]:
        """
        Carga las tasas de interés desde el archivo JSON
        Retorna todo el contenido como un diccionario
        """
        # Si ya está en caché, devolver directamente
        if self._cache is not None:
            return self._cache
        
        if not self.tasas_path.exists():
            self._cache = {}
            return {}
        
        try:
            with open(self.tasas_path, "r", encoding="utf-8") as f:
                tasas = json.load(f)
                self._cache = tasas
                return tasas
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error al cargar tasas de interés: {e}")
            self._cache = {}
            return {}
    
    def limpiar_cache(self):
        """Limpia la caché de tasas de interés"""
        self._cache = None


# Instancia global del repositorio
tasa_interes_repository = JsonTasaInteresRepository() 