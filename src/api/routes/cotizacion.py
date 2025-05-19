from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from src.models.schemas.cotizacion import (
    CotizacionResponse, 
    CotizacionCreate, 
    CotizacionUpdate,
    CotizacionFilter,
    ItemCreate
)
from src.services.cotizador import CotizadorService
from src.api.dependencies import get_cotizador_service


router = APIRouter(prefix="/cotizaciones", tags=["cotizaciones"])


@router.get("/", response_model=List[CotizacionResponse])
async def listar_cotizaciones(
    cliente: Optional[str] = Query(None, description="Filtrar por nombre de cliente"),
    fecha_desde: Optional[datetime] = Query(None, description="Filtrar desde fecha"),
    fecha_hasta: Optional[datetime] = Query(None, description="Filtrar hasta fecha"),
    service: CotizadorService = Depends(get_cotizador_service)
):
    """
    Obtiene todas las cotizaciones con filtros opcionales.
    
    - **cliente**: Filtrar por nombre de cliente (parcial)
    - **fecha_desde**: Filtrar cotizaciones desde esta fecha
    - **fecha_hasta**: Filtrar cotizaciones hasta esta fecha
    """
    # Si hay filtros, usarlos
    if cliente or fecha_desde or fecha_hasta:
        filtros = CotizacionFilter(
            cliente=cliente,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta
        )
        return service.filtrar_cotizaciones(filtros)
    
    # Si no hay filtros, traer todas
    return service.obtener_cotizaciones()


@router.get("/{cotizacion_id}", response_model=CotizacionResponse)
async def obtener_cotizacion(
    cotizacion_id: UUID,
    service: CotizadorService = Depends(get_cotizador_service)
):
    """
    Obtiene una cotización por su ID.
    
    - **cotizacion_id**: ID único de la cotización
    """
    cotizacion = service.obtener_cotizacion_por_id(cotizacion_id)
    if not cotizacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cotización con ID {cotizacion_id} no encontrada"
        )
    return cotizacion


@router.post("/", response_model=CotizacionResponse, status_code=status.HTTP_201_CREATED)
async def crear_cotizacion(
    cotizacion: CotizacionCreate,
    service: CotizadorService = Depends(get_cotizador_service)
):
    """
    Crea una nueva cotización.
    
    - **cotizacion**: Datos de la cotización a crear
    """
    return service.crear_cotizacion(cotizacion)


@router.put("/{cotizacion_id}", response_model=CotizacionResponse)
async def actualizar_cotizacion(
    cotizacion_id: UUID,
    cotizacion: CotizacionUpdate,
    service: CotizadorService = Depends(get_cotizador_service)
):
    """
    Actualiza una cotización existente.
    
    - **cotizacion_id**: ID único de la cotización a actualizar
    - **cotizacion**: Datos actualizados de la cotización
    """
    cotizacion_actualizada = service.actualizar_cotizacion(cotizacion_id, cotizacion)
    if not cotizacion_actualizada:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cotización con ID {cotizacion_id} no encontrada"
        )
    return cotizacion_actualizada


@router.delete("/{cotizacion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_cotizacion(
    cotizacion_id: UUID,
    service: CotizadorService = Depends(get_cotizador_service)
):
    """
    Elimina una cotización existente.
    
    - **cotizacion_id**: ID único de la cotización a eliminar
    """
    eliminado = service.eliminar_cotizacion(cotizacion_id)
    if not eliminado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cotización con ID {cotizacion_id} no encontrada"
        )


@router.post("/{cotizacion_id}/items", response_model=CotizacionResponse)
async def agregar_item(
    cotizacion_id: UUID,
    item: ItemCreate,
    service: CotizadorService = Depends(get_cotizador_service)
):
    """
    Agrega un nuevo ítem a una cotización existente.
    
    - **cotizacion_id**: ID único de la cotización
    - **item**: Datos del ítem a agregar
    """
    item_dict = item.model_dump()
    cotizacion = service.agregar_item_a_cotizacion(cotizacion_id, item_dict)
    if not cotizacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cotización con ID {cotizacion_id} no encontrada"
        )
    return cotizacion


@router.delete("/{cotizacion_id}/items/{item_id}", response_model=CotizacionResponse)
async def eliminar_item(
    cotizacion_id: UUID,
    item_id: UUID,
    service: CotizadorService = Depends(get_cotizador_service)
):
    """
    Elimina un ítem de una cotización existente.
    
    - **cotizacion_id**: ID único de la cotización
    - **item_id**: ID único del ítem a eliminar
    """
    cotizacion = service.eliminar_item_de_cotizacion(cotizacion_id, item_id)
    if not cotizacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cotización con ID {cotizacion_id} o ítem con ID {item_id} no encontrado"
        )
    return cotizacion
