from datetime import date, datetime
from typing import Dict, List, Optional, Any
from decimal import Decimal

from src.models.domain.expuestos_mes import ExpuestosMes, ExpuestoMensual


class ExpuestosMesService:
    """
    Servicio que orquesta operaciones relacionadas con el cálculo
    de expuestos mensuales. Este servicio utiliza la clase de dominio
    ExpuestosMes para la lógica de negocio.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicializa el servicio con configuración opcional.
        
        Args:
            config: Configuración opcional con parámetros como factores
                  de crecimiento, inflación, etc.
        """
        self.config = config or {}
        self.factor_crecimiento = Decimal(str(self.config.get('factor_crecimiento', 0.0)))
        self.factor_inflacion = Decimal(str(self.config.get('factor_inflacion', 0.0)))
    
    def crear_modelo_expuestos(self, fecha_inicio: date, fecha_fin: date) -> ExpuestosMes:
        """
        Crea un nuevo modelo de ExpuestosMes con los parámetros configurados.
        
        Args:
            fecha_inicio: Fecha de inicio del período
            fecha_fin: Fecha de fin del período
            
        Returns:
            ExpuestosMes: Nueva instancia del modelo de dominio
        """
        return ExpuestosMes(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            factor_crecimiento=self.factor_crecimiento,
            factor_inflacion=self.factor_inflacion
        )
    
    def cargar_datos_historicos(self, expuestos: ExpuestosMes, datos: List[Dict[str, Any]]) -> ExpuestosMes:
        """
        Carga datos históricos en el modelo de expuestos.
        
        Args:
            expuestos: Modelo de dominio ExpuestosMes
            datos: Lista de diccionarios con formato 
                  [{'fecha': '2023-01-01', 'cantidad': 100, 'monto': 50000}, ...]
                
        Returns:
            ExpuestosMes: Modelo actualizado con los datos históricos
        """
        for dato in datos:
            fecha = self._parsear_fecha(dato['fecha'])
            expuestos.agregar_expuesto(
                fecha=fecha,
                cantidad=dato['cantidad'],
                monto=dato['monto']
            )
        return expuestos
    
    def proyectar_expuestos(self, 
                           expuestos: ExpuestosMes, 
                           meses_adicionales: int) -> Dict[str, Any]:
        """
        Proyecta expuestos para un número adicional de meses.
        
        Args:
            expuestos: Modelo de dominio ExpuestosMes con datos históricos
            meses_adicionales: Número de meses a proyectar
            
        Returns:
            Dict: Resultado con datos históricos y proyectados
        """
        # Generar proyección utilizando la lógica del dominio
        proyeccion = expuestos.proyectar_expuestos(meses_adicionales)
        
        # Formatear resultado para la API
        return {
            "historicos": expuestos.obtener_expuestos_por_mes(),
            "proyectados": proyeccion.obtener_expuestos_por_mes(),
            "totales": {
                "cantidad_total": proyeccion.calcular_total_expuestos(),
                "monto_total": float(proyeccion.calcular_total_monto()),
                "monto_ajustado_total": float(proyeccion.calcular_total_monto_ajustado())
            }
        }
    
    def calcular_exposicion_total(self, expuestos: ExpuestosMes) -> Dict[str, Any]:
        """
        Calcula la exposición total para el período dado.
        
        Args:
            expuestos: Modelo de dominio ExpuestosMes
            
        Returns:
            Dict: Resultado con totales calculados
        """
        return {
            "expuestos_por_mes": expuestos.obtener_expuestos_por_mes(),
            "totales": {
                "cantidad_total": expuestos.calcular_total_expuestos(),
                "monto_total": float(expuestos.calcular_total_monto()),
                "monto_ajustado_total": float(expuestos.calcular_total_monto_ajustado())
            }
        }
    
    def _parsear_fecha(self, fecha_str: str) -> date:
        """
        Parsea una fecha en formato string a objeto date.
        
        Args:
            fecha_str: Fecha en formato 'YYYY-MM-DD'
            
        Returns:
            date: Objeto date
        """
        if isinstance(fecha_str, date):
            return fecha_str
            
        try:
            return datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            # Intentar con formato alternativo
            return datetime.strptime(fecha_str, '%d/%m/%Y').date()
