from typing import Dict, List, Any, Optional, Union
from decimal import Decimal

from src.models.domain.expuestos_mes import (
    ExpuestosMesActuarial,
    ParametrosActuariales,
    FrecuenciaPago,
    ResultadoMensual,
)
from src.repositories.tabla_mortalidad_repository import Sexo, EstadoFumador
from src.models.schemas.expuestos_mes_schema import (
    ResultadoMensualOutput,
    ResumenOutput,
    ResumenAnioOutput,
)
from src.repositories.parametros_repository import JsonParametrosRepository


class ExpuestosMesService:
    """Servicio para realizar cálculos actuariales de expuestos"""

    def __init__(self):
        self.parametros_repository = JsonParametrosRepository()
        self.parametros_dict = self.parametros_repository.get_parametros_by_producto(
            "rumbo"
        )

    def calcular_proyeccion(
        self,
        edad_actuarial: int,
        sexo: str,
        fumador: bool,
        frecuencia_pago_primas: str,
        periodo_vigencia: int,
        periodo_pago_primas: int,
        ajuste_mortalidad: float,
    ) -> Dict[str, Any]:
        """
        Realiza el cálculo de proyección de expuestos

        Args:
            edad_actuarial: Edad actuarial (edad + x meses según regla actuarial)
            sexo: 'M' para masculino o 'F' para femenino
            fumador: True si es fumador, False en caso contrario
            frecuencia_pago_primas: "ANUAL", "SEMESTRAL", "TRIMESTRAL" o "MENSUAL"
            periodo_vigencia: Período de vigencia del seguro en años
            periodo_pago_primas: Período de pago de primas en años
            ajuste_mortalidad: Factor de ajuste para la tabla de mortalidad
            meses_proyeccion: Número de meses a proyectar (default: 12)

        Returns:
            Diccionario con los resultados de la proyección
        """
        # Convertir parámetros a tipos enumerados
        sexo_enum = Sexo.MASCULINO if sexo == Sexo.MASCULINO else Sexo.FEMENINO
        fumador_enum = EstadoFumador.FUMADOR if fumador else EstadoFumador.NO_FUMADOR
        frecuencia_enum = FrecuenciaPago(frecuencia_pago_primas)
        ajuste_mortalidad = self.parametros_dict.get(
            "ajuste_mortalidad", 0.01
        )  # ! VALIDAR ESTO A FUTURO

        # Crear parámetros actuariales
        parametros = ParametrosActuariales(
            edad_actuarial=edad_actuarial,
            sexo=sexo_enum,
            fumador=fumador_enum,
            frecuencia_pago_primas=frecuencia_enum,
            periodo_vigencia=periodo_vigencia,
            periodo_pago_primas=periodo_pago_primas,
            ajuste_mortalidad=ajuste_mortalidad,
        )

        # Crear modelo de dominio
        expuestos_actuarial = ExpuestosMesActuarial(parametros=parametros)

        # Calcular proyección
        resultados = expuestos_actuarial.calcular_proyeccion()

        # Obtener resumen
        resumen = expuestos_actuarial.obtener_resumen()

        # Formatear resultados para la API
        return self._formatear_resultados(resultados, resumen)

    def _formatear_resultados(
        self, resultados: List[ResultadoMensual], resumen: Dict[str, Union[float, Dict]]
    ) -> Dict[str, Any]:
        """
        Formatea los resultados para la respuesta de la API

        Args:
            resultados: Lista de resultados mensuales
            resumen: Resumen de la proyección

        Returns:
            Diccionario con los resultados formateados
        """
        resultados_formateados = []

        for r in resultados:
            resultado_mensual = ResultadoMensualOutput(
                mes=r.mes,
                anio_poliza=r.anio_poliza,
                edad_actual=r.edad_actual,
                vivos_inicio=str(Decimal(str(r.vivos_inicio))),
                fallecidos=str(Decimal(str(r.fallecidos))),
                vivos_despues_fallecidos=str(Decimal(str(r.vivos_despues_fallecidos))),
                caducados=str(Decimal(str(r.caducados))),
                vivos_final=str(Decimal(str(r.vivos_final))),
                mortalidad_anual=str(Decimal(str(r.mortalidad_anual))),
                mortalidad_mensual=str(Decimal(str(r.mortalidad_mensual))),
                mortalidad_ajustada=str(Decimal(str(r.mortalidad_ajustada))),
                tasa_caducidad=str(Decimal(str(r.tasa_caducidad))),
            )
            resultados_formateados.append(resultado_mensual.model_dump())

        # Formatear y redondear el resumen
        resumen_por_anio = {}
        for anio, datos in resumen["por_anio"].items():
            resumen_por_anio[str(anio)] = ResumenAnioOutput(
                fallecidos=str(Decimal(str(datos["fallecidos"]))),
                caducados=str(Decimal(str(datos["caducados"]))),
                vivos_final=str(Decimal(str(datos["vivos_final"]))),
            ).model_dump()

        resumen_formateado = ResumenOutput(
            vivos_inicial=str(Decimal(str(resumen["vivos_inicial"]))),
            vivos_final=str(Decimal(str(resumen["vivos_final"]))),
            fallecidos_total=str(Decimal(str(resumen["fallecidos_total"]))),
            caducados_total=str(Decimal(str(resumen["caducados_total"]))),
            meses_calculados=resumen["meses_calculados"],
            por_anio=resumen_por_anio,
        ).model_dump()

        return {
            "resultados_mensuales": resultados_formateados,
            "resumen": resumen_formateado,
        }


# Instancia global del servicio
expuestos_mes_service = ExpuestosMesService()
