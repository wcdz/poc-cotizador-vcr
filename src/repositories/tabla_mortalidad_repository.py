from abc import ABC, abstractmethod
import json
import os
from typing import Dict, Any, List, Optional
from pathlib import Path
from enum import Enum, auto


class Sexo(str, Enum):
    MASCULINO = "M"
    FEMENINO = "F"


class EstadoFumador(str, Enum):
    FUMADOR = "fuma"
    NO_FUMADOR = "no_fuma"


class TablaMortalidadRepository(ABC):
    """Interfaz abstracta para el repositorio de tabla de mortalidad"""

    @abstractmethod
    def get_tabla_mortalidad(self) -> Dict[str, Any]:
        """Obtiene toda la tabla de mortalidad como un diccionario"""
        pass

    @abstractmethod
    def get_tasa_mortalidad(
        self, edad: int, sexo: Sexo, fumador: EstadoFumador
    ) -> float:
        """Obtiene la tasa de mortalidad para una edad, sexo y estado de fumador específicos"""
        pass


class JsonTablaMortalidadRepository(TablaMortalidadRepository):
    """Implementación del repositorio de tabla de mortalidad usando archivo JSON"""

    def __init__(self, base_path: str = None, producto: str = "rumbo"):
        """
        Inicializa el repositorio de tabla de mortalidad

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
                / producto.lower()
            )

        self.tabla_mortalidad_path = self.base_path / "tabla_mortalidad.json"
        self._cache = None

    def get_tabla_mortalidad(self) -> Dict[str, Any]:
        """
        Carga la tabla de mortalidad desde el archivo JSON
        Retorna todo el contenido como un diccionario
        """
        # Si ya está en caché, devolver directamente
        if self._cache is not None:
            return self._cache

        if not self.tabla_mortalidad_path.exists():
            self._cache = {}
            return {}

        try:
            with open(self.tabla_mortalidad_path, "r", encoding="utf-8") as f:
                tabla_mortalidad = json.load(f)
                self._cache = tabla_mortalidad
                return tabla_mortalidad
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error al cargar tabla de mortalidad: {e}")
            self._cache = {}
            return {}

    def get_tasa_mortalidad(
        self, edad: int, sexo: Sexo, fumador: EstadoFumador
    ) -> float:
        """
        Obtiene la tasa de mortalidad para una edad, sexo y estado de fumador específicos

        Args:
            edad: Edad de la persona
            sexo: Sexo de la persona (MASCULINO o FEMENINO)
            fumador: Estado de fumador (FUMADOR o NO_FUMADOR)

        Returns:
            Tasa de mortalidad como porcentaje (flotante)

        Raises:
            ValueError: Si no se encuentra la edad especificada
        """
        tabla_mortalidad = self.get_tabla_mortalidad()
        edad_str = str(edad)

        if edad_str not in tabla_mortalidad:
            raise ValueError(f"No se encontró la edad {edad} en la tabla de mortalidad")

        # Determinar la clave correcta basada en sexo y estado de fumador
        if sexo == Sexo.MASCULINO:
            clave_base = "hombres"
        else:
            clave_base = "mujeres"

        clave = f"{clave_base}_{fumador.value}"

        if clave not in tabla_mortalidad[edad_str]:
            raise ValueError(
                f"No se encontró la combinación de sexo y estado de fumador para la edad {edad}"
            )

        return tabla_mortalidad[edad_str][clave]

    def get_tasa_mortalidad_string(self, edad: int, sexo: str, fumador: bool) -> float:
        """
        Versión alternativa que acepta strings y booleanos en lugar de enumeradores

        Args:
            edad: Edad de la persona
            sexo: Sexo de la persona ('M' o 'F')
            fumador: Si la persona es fumadora (True) o no (False)

        Returns:
            Tasa de mortalidad como porcentaje (flotante)
        """
        sexo_enum = Sexo.MASCULINO if sexo == "M" else Sexo.FEMENINO
        fumador_enum = EstadoFumador.FUMADOR if fumador else EstadoFumador.NO_FUMADOR

        return self.get_tasa_mortalidad(edad, sexo_enum, fumador_enum)

    def limpiar_cache(self):
        """Limpia la caché de tabla de mortalidad"""
        self._cache = None


# Instancia global del repositorio
tabla_mortalidad_repository = JsonTablaMortalidadRepository()
