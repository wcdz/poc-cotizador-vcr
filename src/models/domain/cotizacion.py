from datetime import datetime
from uuid import UUID, uuid4
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Item:
    """Modelo de dominio para un ítem de cotización"""
    nombre: str
    descripcion: str
    precio_unitario: float
    cantidad: int
    id: UUID = field(default_factory=uuid4)
    subtotal: float = field(init=False)
    
    def __post_init__(self):
        self.subtotal = self.precio_unitario * self.cantidad


@dataclass
class Cotizacion:
    """Modelo de dominio para una cotización"""
    numero: str
    cliente: str
    id: UUID = field(default_factory=uuid4)
    fecha_emision: datetime = field(default_factory=datetime.now)
    fecha_validez: Optional[datetime] = None
    items: List[Item] = field(default_factory=list)
    notas: Optional[str] = None
    total: float = field(default=0.0)
    
    def calcular_total(self) -> float:
        """Calcula el total de la cotización basado en los ítems"""
        self.total = sum(item.subtotal for item in self.items)
        return self.total
    
    def agregar_item(self, item: Item) -> None:
        """Agrega un ítem a la cotización y recalcula el total"""
        self.items.append(item)
        self.calcular_total()
    
    def eliminar_item(self, item_id: UUID) -> bool:
        """Elimina un ítem de la cotización por su ID y recalcula el total"""
        for i, item in enumerate(self.items):
            if item.id == item_id:
                self.items.pop(i)
                self.calcular_total()
                return True
        return False
