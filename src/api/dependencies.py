from fastapi import Depends
from typing import Generator

from src.repositories.cotizacion_repository import CotizacionRepository
from src.services.cotizacion import CotizadorService


def get_cotizacion_repository() -> Generator[CotizacionRepository, None, None]:
    """
    Devuelve una instancia del repositorio de cotizaciones.
    En un entorno de producción, aquí se manejaría la conexión a BD.
    """
    repository = CotizacionRepository()
    try:
        yield repository
    finally:
        # Cerrar conexiones si fuera necesario
        pass


def get_cotizador_service(
    repository: CotizacionRepository = Depends(get_cotizacion_repository),
) -> Generator[CotizadorService, None, None]:
    """
    Devuelve una instancia del servicio de cotizaciones.
    Utiliza el patrón de inyección de dependencias.
    """
    service = CotizadorService(repository)
    try:
        yield service
    finally:
        # Limpieza si fuera necesaria
        pass
