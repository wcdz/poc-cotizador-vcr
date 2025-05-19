from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from uuid import UUID


class ItemBase(BaseModel):
    nombre: str
    descripcion: str
    precio_unitario: float = Field(gt=0)
    cantidad: int = Field(gt=0)


class ItemCreate(ItemBase):
    pass


class ItemResponse(ItemBase):
    id: UUID
    subtotal: float

    class Config:
        from_attributes = True


class CotizacionBase(BaseModel):
    numero: str
    cliente: str
    fecha_validez: Optional[datetime] = None
    notas: Optional[str] = None


class CotizacionCreate(CotizacionBase):
    items: List[ItemCreate]


class CotizacionUpdate(BaseModel):
    cliente: Optional[str] = None
    fecha_validez: Optional[datetime] = None
    notas: Optional[str] = None


class CotizacionResponse(CotizacionBase):
    id: UUID
    fecha_emision: datetime
    items: List[ItemResponse]
    total: float

    class Config:
        from_attributes = True


class CotizacionFilter(BaseModel):
    cliente: Optional[str] = None
    fecha_desde: Optional[datetime] = None
    fecha_hasta: Optional[datetime] = None
