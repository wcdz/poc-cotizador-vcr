from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta

from src.models.domain.cotizacion import Cotizacion, Item
from src.models.schemas.cotizacion import CotizacionCreate, CotizacionUpdate, CotizacionFilter
from src.repositories.cotizacion_repository import CotizacionRepository


class CotizadorService:
    """Servicio que implementa la lógica de negocio relacionada con cotizaciones"""
    
    def __init__(self, repository: CotizacionRepository):
        self.repository = repository
    
    def generar_numero_cotizacion(self) -> str:
        """
        Genera un número único para una nueva cotización
        Formato: COT-[AÑO][MES]-[SECUENCIAL]
        """
        ahora = datetime.now()
        prefijo = f"COT-{ahora.year}{ahora.month:02d}-"
        
        # Buscar la última cotización con este prefijo
        cotizaciones = self.repository.get_all()
        ultimo_numero = 0
        
        for cotizacion in cotizaciones:
            if cotizacion.numero.startswith(prefijo):
                try:
                    # Extraer el número secuencial
                    secuencial = int(cotizacion.numero.split('-')[-1])
                    ultimo_numero = max(ultimo_numero, secuencial)
                except ValueError:
                    pass
        
        # Incrementar el secuencial
        nuevo_secuencial = ultimo_numero + 1
        return f"{prefijo}{nuevo_secuencial:04d}"
    
    def obtener_cotizaciones(self) -> List[Cotizacion]:
        """Obtiene todas las cotizaciones"""
        return self.repository.get_all()
    
    def obtener_cotizacion_por_id(self, cotizacion_id: UUID) -> Optional[Cotizacion]:
        """Obtiene una cotización por su ID"""
        return self.repository.get_by_id(cotizacion_id)
    
    def crear_cotizacion(self, cotizacion_data: CotizacionCreate) -> Cotizacion:
        """Crea una nueva cotización"""
        # Si no se proporcionó un número, generar uno automáticamente
        if not cotizacion_data.numero or cotizacion_data.numero == "auto":
            numero = self.generar_numero_cotizacion()
        else:
            numero = cotizacion_data.numero
        
        # Por defecto, la validez es de 30 días
        fecha_validez = cotizacion_data.fecha_validez
        if not fecha_validez:
            fecha_validez = datetime.now() + timedelta(days=30)
        
        # Crear los items
        items = []
        for item_data in cotizacion_data.items:
            item = Item(
                nombre=item_data.nombre,
                descripcion=item_data.descripcion,
                precio_unitario=item_data.precio_unitario,
                cantidad=item_data.cantidad
            )
            items.append(item)
        
        # Crear la cotización
        cotizacion = Cotizacion(
            numero=numero,
            cliente=cotizacion_data.cliente,
            fecha_validez=fecha_validez,
            notas=cotizacion_data.notas,
            items=items
        )
        
        # Calcular el total
        cotizacion.calcular_total()
        
        # Persistir y retornar
        return self.repository.create(cotizacion)
    
    def actualizar_cotizacion(self, cotizacion_id: UUID, 
                             cotizacion_data: CotizacionUpdate) -> Optional[Cotizacion]:
        """Actualiza una cotización existente"""
        cotizacion = self.repository.get_by_id(cotizacion_id)
        if not cotizacion:
            return None
        
        # Actualizar campos si fueron proporcionados
        if cotizacion_data.cliente is not None:
            cotizacion.cliente = cotizacion_data.cliente
        
        if cotizacion_data.fecha_validez is not None:
            cotizacion.fecha_validez = cotizacion_data.fecha_validez
        
        if cotizacion_data.notas is not None:
            cotizacion.notas = cotizacion_data.notas
        
        # Persistir y retornar
        return self.repository.update(cotizacion)
    
    def eliminar_cotizacion(self, cotizacion_id: UUID) -> bool:
        """Elimina una cotización por su ID"""
        return self.repository.delete(cotizacion_id)
    
    def filtrar_cotizaciones(self, filtros: CotizacionFilter) -> List[Cotizacion]:
        """Filtra cotizaciones según criterios específicos"""
        return self.repository.filter(
            cliente=filtros.cliente,
            fecha_desde=filtros.fecha_desde,
            fecha_hasta=filtros.fecha_hasta
        )
    
    def agregar_item_a_cotizacion(self, cotizacion_id: UUID, item_data: Dict[str, Any]) -> Optional[Cotizacion]:
        """Agrega un nuevo ítem a una cotización existente"""
        cotizacion = self.repository.get_by_id(cotizacion_id)
        if not cotizacion:
            return None
        
        # Crear el nuevo ítem
        item = Item(
            nombre=item_data["nombre"],
            descripcion=item_data["descripcion"],
            precio_unitario=item_data["precio_unitario"],
            cantidad=item_data["cantidad"]
        )
        
        # Agregar el ítem y recalcular el total
        cotizacion.agregar_item(item)
        
        # Persistir y retornar
        return self.repository.update(cotizacion)
    
    def eliminar_item_de_cotizacion(self, cotizacion_id: UUID, item_id: UUID) -> Optional[Cotizacion]:
        """Elimina un ítem de una cotización existente"""
        cotizacion = self.repository.get_by_id(cotizacion_id)
        if not cotizacion:
            return None
        
        # Eliminar el ítem y recalcular el total
        if not cotizacion.eliminar_item(item_id):
            return None  # Ítem no encontrado
        
        # Persistir y retornar
        return self.repository.update(cotizacion)
