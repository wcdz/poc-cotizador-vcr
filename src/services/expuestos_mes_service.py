from typing import Dict, List, Any, Optional, Union

from src.models.domain.expuestos_mes import (
    ExpuestosMesActuarial,
    ParametrosActuariales,
    FrecuenciaPago,
    ResultadoMensual,
)
from src.repositories.tabla_mortalidad_repository import Sexo, EstadoFumador
from src.core.constans import MESES_PROYECCION
from src.models.schemas.expuestos_mes_schema import (
    ResultadoMensualOutput,
    ResumenOutput,
    ResumenAnioOutput
)


class ExpuestosMesService:
    """Servicio para realizar cálculos actuariales de expuestos"""

    def calcular_proyeccion(
        self,
        edad_actuarial: int,
        sexo: str,
        fumador: bool,
        frecuencia_pago_primas: str,
        periodo_vigencia: int,
        periodo_pago_primas: int,
        ajuste_mortalidad: float,
        meses_proyeccion: int = MESES_PROYECCION,
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
        resultados = expuestos_actuarial.calcular_proyeccion(meses=meses_proyeccion)

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
                vivos_inicio=round(r.vivos_inicio, 6),
                fallecidos=round(r.fallecidos, 6),
                vivos_despues_fallecidos=round(r.vivos_despues_fallecidos, 6),
                caducados=round(r.caducados, 6),
                vivos_final=round(r.vivos_final, 6),
                mortalidad_anual=round(r.mortalidad_anual, 6),
                mortalidad_mensual=round(r.mortalidad_mensual, 6),
                mortalidad_ajustada=round(r.mortalidad_ajustada, 6),
                tasa_caducidad=round(r.tasa_caducidad, 6),
            )
            resultados_formateados.append(resultado_mensual.model_dump())

        # Formatear y redondear el resumen
        resumen_por_anio = {}
        for anio, datos in resumen["por_anio"].items():
            resumen_por_anio[str(anio)] = ResumenAnioOutput(
                fallecidos=round(datos["fallecidos"], 6),
                caducados=round(datos["caducados"], 6),
                vivos_final=round(datos["vivos_final"], 6)
            ).model_dump()

        resumen_formateado = ResumenOutput(
            vivos_inicial=round(resumen["vivos_inicial"], 6),
            vivos_final=round(resumen["vivos_final"], 6),
            fallecidos_total=round(resumen["fallecidos_total"], 6),
            caducados_total=round(resumen["caducados_total"], 6),
            meses_calculados=resumen["meses_calculados"],
            por_anio=resumen_por_anio
        ).model_dump()

        return {
            "resultados_mensuales": resultados_formateados,
            "resumen": resumen_formateado,
        }


# Instancia global del servicio
expuestos_mes_service = ExpuestosMesService()
