from abc import ABC, abstractmethod
import json
import os
from typing import Dict, Any, List, Optional
from pathlib import Path


class PeriodosCotizacionRepository(ABC):
    """Interfaz abstracta para el repositorio de períodos de cotización"""

    @abstractmethod
    def get_periodos_cotizacion(self) -> List[Dict[str, Any]]:
        """Obtiene todos los períodos de cotización como una lista"""
        pass

    @abstractmethod
    def get_periodos_disponibles(self, monto_prima: float) -> List[int]:
        """Obtiene los períodos disponibles para un monto de prima específico"""
        pass


class JsonPeriodosCotizacionRepository(PeriodosCotizacionRepository):
    """Implementación del repositorio de períodos de cotización usando archivo JSON"""

    def __init__(self, base_path: str = None, producto: str = "rumbo"):
        """
        Inicializa el repositorio de períodos de cotización

        Args:
            base_path: Ruta base para los archivos JSON (optional)
            producto: Nombre del producto (default: "rumbo")
        """
        if base_path:
            self.base_path = Path(base_path)
        else:
            # Ruta por defecto: raíz del proyecto / assets / producto
            self.base_path = (
                Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
                / "assets"
                / producto.upper()
            )

        self.periodos_path = self.base_path / "periodos_cotizacion.json"
        self._cache = None

    def get_periodos_cotizacion(self) -> List[Dict[str, Any]]:
        """
        Carga los períodos de cotización desde el archivo JSON
        Retorna todo el contenido como una lista de diccionarios
        """
        # Si ya está en caché, devolver directamente
        if self._cache is not None:
            return self._cache

        if not self.periodos_path.exists():
            self._cache = []
            return []

        try:
            with open(self.periodos_path, "r", encoding="utf-8") as f:
                periodos = json.load(f)
                self._cache = periodos
                return periodos
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error al cargar períodos de cotización: {e}")
            self._cache = []
            return []

    def get_periodos_disponibles(self, monto_prima: float) -> List[int]:
        """
        Obtiene los períodos disponibles para un monto de prima específico

        Args:
            monto_prima: Monto de la prima a consultar

        Returns:
            Lista de períodos disponibles para el monto especificado
        """
        periodos_data = self.get_periodos_cotizacion()

        # Buscar en qué rango de primas se encuentra el monto
        for grupo in periodos_data:
            primas = grupo.get("primas", [])
            periodos = grupo.get("periodos", [])

            # Si el monto está dentro del rango de primas de este grupo
            if primas and min(primas) <= monto_prima <= max(primas):
                return periodos

            # También verificar si el monto coincide exactamente con alguna prima
            if monto_prima in primas:
                return periodos

        # Si no se encuentra ningún rango, retornar lista vacía
        return []

    def get_rango_primas_por_periodo(self, periodo: int) -> List[float]:
        """
        Obtiene todos los montos de prima disponibles para un período específico

        Args:
            periodo: Período de cotización a consultar

        Returns:
            Lista de montos de prima disponibles para el período especificado
        """
        periodos_data = self.get_periodos_cotizacion()
        primas_disponibles = []

        for grupo in periodos_data:
            periodos = grupo.get("periodos", [])
            primas = grupo.get("primas", [])

            # Si el período está disponible en este grupo
            if periodo in periodos:
                primas_disponibles.extend(primas)

        # Remover duplicados y ordenar
        return sorted(list(set(primas_disponibles)))

    def validar_prima_periodo(self, monto_prima: float, periodo: int) -> bool:
        """
        Valida si una prima y período son compatibles

        Args:
            monto_prima: Monto de la prima
            periodo: Período de cotización

        Returns:
            True si la combinación es válida, False en caso contrario
        """
        periodos_disponibles = self.get_periodos_disponibles(monto_prima)
        return periodo in periodos_disponibles

    def limpiar_cache(self):
        """Limpia la caché de períodos de cotización"""
        self._cache = None


# Instancia global del repositorio
periodos_cotizacion_repository = JsonPeriodosCotizacionRepository()
