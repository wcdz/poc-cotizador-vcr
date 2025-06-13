from abc import ABC, abstractmethod
import json
import os
from typing import Dict, Any
from pathlib import Path
from src.common.frecuencia_pago import FrecuenciaPago


class FactoresPagoRepository(ABC):
    """Interfaz abstracta para el repositorio de factores de pago"""

    @abstractmethod
    def get_factores_pago(self) -> Dict[str, float]:
        """Obtiene todos los factores de pago como un diccionario"""
        pass

    @abstractmethod
    def get_factor_pago(self, frecuencia: FrecuenciaPago) -> float:
        """Obtiene el factor de pago para una frecuencia específica"""
        pass


class JsonFactoresPagoRepository(FactoresPagoRepository):
    """Implementación del repositorio de factores de pago usando archivo JSON"""

    def __init__(self, base_path: str = None, producto: str = "rumbo"):
        """
        Inicializa el repositorio de factores de pago

        Args:
            base_path: Ruta base para los archivos JSON (optional)
            producto: Nombre del producto (default: "rumbo")
        """
        if base_path:
            self.base_path = Path(base_path)
        else:
            # Ruta por defecto: raíz del proyecto / assets / producto
            self.base_path = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) / "assets" / producto.lower()

        self.factores_pago_path = self.base_path / "factores_pago.json"
        self._cache = None

    def get_factores_pago(self) -> Dict[str, float]:
        """
        Carga los factores de pago desde el archivo JSON
        Retorna todo el contenido como un diccionario
        """
        # Si ya está en caché, devolver directamente
        if self._cache is not None:
            return self._cache

        if not self.factores_pago_path.exists():
            self._cache = {}
            return {}

        try:
            with open(self.factores_pago_path, "r", encoding="utf-8") as f:
                factores = json.load(f)
                self._cache = factores
                return factores
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error al cargar factores de pago: {e}")
            self._cache = {}
            return {}

    def get_factor_pago(self, frecuencia: FrecuenciaPago) -> float:
        """
        Obtiene el factor de pago para una frecuencia específica
        Args:
            frecuencia: Frecuencia de pago (FrecuenciaPago)
        Returns:
            Factor de pago como flotante
        Raises:
            ValueError: Si no se encuentra la frecuencia especificada
        """
        factores = self.get_factores_pago()
        clave = frecuencia.value.lower()  # El JSON usa claves en minúsculas
        if clave not in factores:
            raise ValueError(f"No se encontró el factor de pago para la frecuencia '{frecuencia.value}'")
        return float(factores[clave])

    def limpiar_cache(self):
        """Limpia la caché de factores de pago"""
        self._cache = None


# Instancia global del repositorio
factores_pago_repository = JsonFactoresPagoRepository()
