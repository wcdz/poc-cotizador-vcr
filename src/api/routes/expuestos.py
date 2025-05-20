from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from typing import Dict, Any

from src.models.schemas.expuestos import (
    ExpuestosInput,
    ExpuestosOutput,
    ProyeccionInput,
    ProyeccionOutput
)
from src.services.expuestos_mes_service import ExpuestosMesService
from src.models.domain.expuestos_mes import ExpuestosMes

router = APIRouter()

def get_expuestos_service():
    """Dependencia para obtener el servicio de expuestos mensuales"""
    return ExpuestosMesService()

@router.post("/calcular", response_model=ExpuestosOutput)
async def calcular_expuestos(
    datos: ExpuestosInput,
    service: ExpuestosMesService = Depends(get_expuestos_service)
):
    """
    Calcula la exposición mensual al riesgo basada en los datos proporcionados.
    
    Ejemplo de petición:
    ```json
    {
        "fecha_inicio": "2023-01-01",
        "fecha_fin": "2023-12-31",
        "configuracion": {
            "factor_crecimiento": 0.01,
            "factor_inflacion": 0.02
        },
        "datos_historicos": [
            {"fecha": "2023-01-01", "cantidad": 100, "monto": 50000},
            {"fecha": "2023-02-01", "cantidad": 120, "monto": 55000}
        ]
    }
    ```
    """
    try:
        # Parsear fechas
        fecha_inicio = datetime.strptime(datos.fecha_inicio, "%Y-%m-%d").date()
        fecha_fin = datetime.strptime(datos.fecha_fin, "%Y-%m-%d").date()
        
        # Configurar servicio
        if datos.configuracion:
            service.factor_crecimiento = datos.configuracion.factor_crecimiento
            service.factor_inflacion = datos.configuracion.factor_inflacion
        
        # Crear modelo y cargar datos
        modelo_expuestos = service.crear_modelo_expuestos(fecha_inicio, fecha_fin)
        modelo_expuestos = service.cargar_datos_historicos(
            modelo_expuestos, 
            [hist.dict() for hist in datos.datos_historicos]
        )
        
        # Calcular y devolver resultados
        return service.calcular_exposicion_total(modelo_expuestos)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al calcular expuestos: {str(e)}")

@router.post("/proyectar", response_model=ProyeccionOutput)
async def proyectar_expuestos(
    datos: ProyeccionInput,
    service: ExpuestosMesService = Depends(get_expuestos_service)
):
    """
    Proyecta la exposición mensual al riesgo para un número de meses adicionales.
    
    Ejemplo de petición:
    ```json
    {
        "datos_expuestos": {
            "fecha_inicio": "2023-01-01",
            "fecha_fin": "2023-12-31",
            "configuracion": {
                "factor_crecimiento": 0.01,
                "factor_inflacion": 0.02
            },
            "datos_historicos": [
                {"fecha": "2023-01-01", "cantidad": 100, "monto": 50000},
                {"fecha": "2023-02-01", "cantidad": 120, "monto": 55000}
            ]
        },
        "meses_proyeccion": 12
    }
    ```
    """
    try:
        # Configurar servicio
        if datos.datos_expuestos.configuracion:
            service.factor_crecimiento = datos.datos_expuestos.configuracion.factor_crecimiento
            service.factor_inflacion = datos.datos_expuestos.configuracion.factor_inflacion
        
        # Parsear fechas
        fecha_inicio = datetime.strptime(
            datos.datos_expuestos.fecha_inicio, "%Y-%m-%d"
        ).date()
        fecha_fin = datetime.strptime(
            datos.datos_expuestos.fecha_fin, "%Y-%m-%d"
        ).date()
        
        # Crear modelo y cargar datos
        modelo_expuestos = service.crear_modelo_expuestos(fecha_inicio, fecha_fin)
        modelo_expuestos = service.cargar_datos_historicos(
            modelo_expuestos, 
            [hist.dict() for hist in datos.datos_expuestos.datos_historicos]
        )
        
        # Proyectar y devolver resultados
        return service.proyectar_expuestos(modelo_expuestos, datos.meses_proyeccion)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al proyectar expuestos: {str(e)}") 