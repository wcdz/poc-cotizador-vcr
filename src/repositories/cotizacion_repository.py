from typing import List, Optional, Dict
from uuid import UUID
import json
import os
from datetime import datetime

from src.models.domain.cotizacion import Cotizacion, Item


class CotizacionRepository:
    """
    Repositorio para gestionar la persistencia de cotizaciones.
    En un entorno de producción, esto conectaría con una base de datos real.
    Por simplicidad, este ejemplo usa un almacenamiento en memoria con persistencia en JSON.
    """
    
    def __init__(self):
        self.cotizaciones: Dict[UUID, Cotizacion] = {}
        self._file_path = "data/cotizaciones.json"
        self._ensure_data_directory()
        self._load_cotizaciones()
    
    def _ensure_data_directory(self) -> None:
        """Asegura que el directorio de datos exista"""
        os.makedirs(os.path.dirname(self._file_path), exist_ok=True)
    
    def _load_cotizaciones(self) -> None:
        """Carga las cotizaciones desde el archivo JSON si existe"""
        if not os.path.exists(self._file_path):
            return
        
        try:
            with open(self._file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                for cotizacion_data in data:
                    # Reconstruir objetos de dominio desde JSON
                    items = []
                    for item_data in cotizacion_data.pop("items", []):
                        item = Item(
                            nombre=item_data["nombre"],
                            descripcion=item_data["descripcion"],
                            precio_unitario=item_data["precio_unitario"],
                            cantidad=item_data["cantidad"],
                            id=UUID(item_data["id"])
                        )
                        items.append(item)
                    
                    # Convertir fechas de string a datetime
                    cotizacion_data["fecha_emision"] = datetime.fromisoformat(cotizacion_data["fecha_emision"])
                    if cotizacion_data.get("fecha_validez"):
                        cotizacion_data["fecha_validez"] = datetime.fromisoformat(cotizacion_data["fecha_validez"])
                    
                    cotizacion = Cotizacion(
                        numero=cotizacion_data["numero"],
                        cliente=cotizacion_data["cliente"],
                        id=UUID(cotizacion_data["id"]),
                        fecha_emision=cotizacion_data["fecha_emision"],
                        fecha_validez=cotizacion_data.get("fecha_validez"),
                        notas=cotizacion_data.get("notas"),
                        items=items
                    )
                    cotizacion.calcular_total()
                    self.cotizaciones[cotizacion.id] = cotizacion
        except (json.JSONDecodeError, FileNotFoundError):
            # Si hay errores, comenzar con un diccionario vacío
            self.cotizaciones = {}
    
    def _save_cotizaciones(self) -> None:
        """Guarda las cotizaciones en el archivo JSON"""
        data = []
        for cotizacion in self.cotizaciones.values():
            # Convertir objetos de dominio a diccionarios serializables
            cotizacion_dict = {
                "id": str(cotizacion.id),
                "numero": cotizacion.numero,
                "cliente": cotizacion.cliente,
                "fecha_emision": cotizacion.fecha_emision.isoformat(),
                "total": cotizacion.total,
                "items": []
            }
            
            if cotizacion.fecha_validez:
                cotizacion_dict["fecha_validez"] = cotizacion.fecha_validez.isoformat()
            
            if cotizacion.notas:
                cotizacion_dict["notas"] = cotizacion.notas
            
            for item in cotizacion.items:
                item_dict = {
                    "id": str(item.id),
                    "nombre": item.nombre,
                    "descripcion": item.descripcion,
                    "precio_unitario": item.precio_unitario,
                    "cantidad": item.cantidad,
                    "subtotal": item.subtotal
                }
                cotizacion_dict["items"].append(item_dict)
            
            data.append(cotizacion_dict)
        
        with open(self._file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
    
    def get_all(self) -> List[Cotizacion]:
        """Obtiene todas las cotizaciones"""
        return list(self.cotizaciones.values())
    
    def get_by_id(self, cotizacion_id: UUID) -> Optional[Cotizacion]:
        """Obtiene una cotización por su ID"""
        return self.cotizaciones.get(cotizacion_id)
    
    def create(self, cotizacion: Cotizacion) -> Cotizacion:
        """Crea una nueva cotización"""
        self.cotizaciones[cotizacion.id] = cotizacion
        self._save_cotizaciones()
        return cotizacion
    
    def update(self, cotizacion: Cotizacion) -> Optional[Cotizacion]:
        """Actualiza una cotización existente"""
        if cotizacion.id not in self.cotizaciones:
            return None
        
        self.cotizaciones[cotizacion.id] = cotizacion
        self._save_cotizaciones()
        return cotizacion
    
    def delete(self, cotizacion_id: UUID) -> bool:
        """Elimina una cotización por su ID"""
        if cotizacion_id not in self.cotizaciones:
            return False
        
        del self.cotizaciones[cotizacion_id]
        self._save_cotizaciones()
        return True
    
    def filter(self, cliente: Optional[str] = None, 
               fecha_desde: Optional[datetime] = None,
               fecha_hasta: Optional[datetime] = None) -> List[Cotizacion]:
        """Filtra cotizaciones por criterios específicos"""
        resultado = list(self.cotizaciones.values())
        
        if cliente:
            resultado = [c for c in resultado if cliente.lower() in c.cliente.lower()]
        
        if fecha_desde:
            resultado = [c for c in resultado if c.fecha_emision >= fecha_desde]
        
        if fecha_hasta:
            resultado = [c for c in resultado if c.fecha_emision <= fecha_hasta]
        
        return resultado 