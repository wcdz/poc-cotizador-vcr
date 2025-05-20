from dataclasses import dataclass, field
from datetime import datetime, date
from typing import List, Dict, Optional, Union
from decimal import Decimal
import math


@dataclass
class ExpuestoMensual:
    """Representa la exposición mensual al riesgo para un mes específico"""
    fecha: date
    cantidad: int
    monto_expuesto: Decimal
    factor_ajuste: Decimal = Decimal('1.0')
    
    @property
    def monto_ajustado(self) -> Decimal:
        """Calcula el monto expuesto ajustado por el factor"""
        return self.monto_expuesto * self.factor_ajuste


@dataclass
class ExpuestosMes:
    """
    Modelo de dominio para la exposición mensual al riesgo.
    Encapsula todos los cálculos relacionados con la exposición mensual.
    """
    fecha_inicio: date
    fecha_fin: date
    factor_crecimiento: Decimal = Decimal('0.0')
    factor_inflacion: Decimal = Decimal('0.0')
    expuestos_mensuales: List[ExpuestoMensual] = field(default_factory=list)
    
    def agregar_expuesto(self, fecha: date, cantidad: int, monto: Union[float, Decimal]) -> None:
        """Agrega un nuevo mes a los expuestos mensuales"""
        if isinstance(monto, float):
            monto = Decimal(str(monto))
            
        # Validación básica
        if fecha < self.fecha_inicio or fecha > self.fecha_fin:
            raise ValueError(f"La fecha {fecha} está fuera del rango permitido")
            
        # Calcula el factor de ajuste según la distancia temporal
        factor = self._calcular_factor_ajuste(fecha)
        
        expuesto = ExpuestoMensual(
            fecha=fecha,
            cantidad=cantidad,
            monto_expuesto=monto,
            factor_ajuste=factor
        )
        
        self.expuestos_mensuales.append(expuesto)
    
    def _calcular_factor_ajuste(self, fecha: date) -> Decimal:
        """
        Calcula el factor de ajuste basado en el crecimiento 
        y la inflación para una fecha dada
        """
        # Calcular meses de diferencia desde la fecha inicial
        meses_diff = (fecha.year - self.fecha_inicio.year) * 12 + fecha.month - self.fecha_inicio.month
        
        # Aplicar factor de crecimiento compuesto mensual
        factor_crecimiento = (Decimal('1.0') + self.factor_crecimiento) ** Decimal(str(meses_diff))
        
        # Aplicar factor de inflación compuesto mensual
        factor_inflacion = (Decimal('1.0') + self.factor_inflacion) ** Decimal(str(meses_diff))
        
        # Combinar los factores
        return factor_crecimiento * factor_inflacion
    
    def calcular_total_expuestos(self) -> int:
        """Calcula el total de expuestos en el período"""
        return sum(expuesto.cantidad for expuesto in self.expuestos_mensuales)
    
    def calcular_total_monto(self) -> Decimal:
        """Calcula el monto total expuesto (sin ajustar)"""
        return sum(expuesto.monto_expuesto for expuesto in self.expuestos_mensuales)
    
    def calcular_total_monto_ajustado(self) -> Decimal:
        """Calcula el monto total expuesto ajustado por los factores"""
        return sum(expuesto.monto_ajustado for expuesto in self.expuestos_mensuales)
    
    def proyectar_expuestos(self, meses_adicionales: int) -> 'ExpuestosMes':
        """
        Proyecta los expuestos para un número adicional de meses
        utilizando los factores de crecimiento e inflación
        """
        if not self.expuestos_mensuales:
            raise ValueError("No hay datos de expuestos para proyectar")
            
        # Ordenar expuestos por fecha
        expuestos_ordenados = sorted(self.expuestos_mensuales, key=lambda x: x.fecha)
        
        # Obtener el último mes
        ultimo_expuesto = expuestos_ordenados[-1]
        ultimo_mes = ultimo_expuesto.fecha.month
        ultimo_anio = ultimo_expuesto.fecha.year
        
        # Extender la fecha fin para la proyección
        nueva_fecha_fin = date(
            year=ultimo_anio + ((ultimo_mes + meses_adicionales - 1) // 12),
            month=((ultimo_mes + meses_adicionales - 1) % 12) + 1,
            day=1  # Primer día del mes
        )
        
        # Crear nueva instancia con la proyección
        proyeccion = ExpuestosMes(
            fecha_inicio=self.fecha_inicio,
            fecha_fin=nueva_fecha_fin,
            factor_crecimiento=self.factor_crecimiento,
            factor_inflacion=self.factor_inflacion,
            expuestos_mensuales=self.expuestos_mensuales.copy()  # Copiar los existentes
        )
        
        # Generar la proyección para los meses adicionales
        mes_actual = ultimo_mes
        anio_actual = ultimo_anio
        
        for _ in range(meses_adicionales):
            # Avanzar al siguiente mes
            mes_actual += 1
            if mes_actual > 12:
                mes_actual = 1
                anio_actual += 1
                
            fecha_proyeccion = date(year=anio_actual, month=mes_actual, day=1)
            
            # Proyectar basado en el último mes conocido con factores aplicados
            nueva_cantidad = math.ceil(ultimo_expuesto.cantidad * 
                               (1 + float(self.factor_crecimiento)) ** _)
                               
            nuevo_monto = ultimo_expuesto.monto_expuesto * \
                          (Decimal('1.0') + self.factor_crecimiento) ** Decimal(str(_)) * \
                          (Decimal('1.0') + self.factor_inflacion) ** Decimal(str(_))
            
            proyeccion.agregar_expuesto(
                fecha=fecha_proyeccion,
                cantidad=nueva_cantidad,
                monto=nuevo_monto
            )
            
        return proyeccion
    
    def obtener_expuestos_por_mes(self) -> Dict[str, Dict]:
        """
        Obtiene un diccionario con los expuestos por mes
        en formato {YYYY-MM: {cantidad: X, monto: Y, monto_ajustado: Z}}
        """
        resultado = {}
        for expuesto in self.expuestos_mensuales:
            clave = f"{expuesto.fecha.year}-{expuesto.fecha.month:02d}"
            resultado[clave] = {
                "cantidad": expuesto.cantidad,
                "monto": float(expuesto.monto_expuesto),
                "monto_ajustado": float(expuesto.monto_ajustado)
            }
        return resultado
