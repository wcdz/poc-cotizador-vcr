from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Union
from enum import Enum
import math
from decimal import Decimal
from src.core.constans import ANUAL, SEMESTRAL, TRIMESTRAL, MENSUAL, PROBABILIDAD_VIVOS

from src.repositories.tabla_mortalidad_repository import (
    tabla_mortalidad_repository,
    Sexo,
    EstadoFumador,
)
from src.repositories.caducidad_repository import caducidad_repository
from src.helpers.caducidad_mensual import caducidad_mensual
from src.utils.anios_meses import anios_meses


class FrecuenciaPago(str, Enum):
    ANUAL = "ANUAL"
    SEMESTRAL = "SEMESTRAL"
    TRIMESTRAL = "TRIMESTRAL"
    MENSUAL = "MENSUAL"


@dataclass
class ParametrosActuariales:
    """Parámetros necesarios para los cálculos actuariales"""

    edad_actuarial: int
    sexo: Sexo
    fumador: EstadoFumador
    frecuencia_pago_primas: FrecuenciaPago
    periodo_vigencia: int
    periodo_pago_primas: int
    ajuste_mortalidad: float
    probabilidad_vivos_inicial: float = (
        PROBABILIDAD_VIVOS  # Por defecto comienza con 100% de vivos
    )

    def get_meses_frecuencia(self) -> int:
        """Obtiene la cantidad de meses según la frecuencia de pago"""
        meses_por_frecuencia = {
            FrecuenciaPago.ANUAL: ANUAL,
            FrecuenciaPago.SEMESTRAL: SEMESTRAL,
            FrecuenciaPago.TRIMESTRAL: TRIMESTRAL,
            FrecuenciaPago.MENSUAL: MENSUAL,
        }
        return meses_por_frecuencia.get(self.frecuencia_pago_primas, 12)

    def get_duracion_pagos(self) -> int:
        """Calcula la duración de pagos"""
        return self.periodo_vigencia + self.edad_actuarial - 1


@dataclass
class ResultadoMensual:
    """Resultado de cálculos para un mes específico"""

    mes: int
    anio_poliza: int
    edad_actual: int
    vivos_inicio: float
    fallecidos: float
    vivos_despues_fallecidos: float
    caducados: float
    vivos_final: float
    mortalidad_anual: float
    mortalidad_mensual: float
    mortalidad_ajustada: float
    tasa_caducidad: float


@dataclass
class ExpuestosMesActuarial:
    """
    Modelo de dominio para cálculos actuariales basados en expuestos mes.
    Implementa la lógica actuarial para calcular vivos, fallecidos y caducados.
    """

    parametros: ParametrosActuariales
    resultados: List[ResultadoMensual] = field(default_factory=list)

    def calcular_proyeccion(self) -> List[ResultadoMensual]:
        """
        Calcula la proyección de expuestos para un número determinado de meses

        Args:
            meses: Número de meses a proyectar

        Returns:
            Lista de resultados mensuales
        """
        self.resultados = []

        # Inicializar valores para el primer mes
        # Por defecto usamos 1.0 pero puede ser ajustado según parámetros específicos
        vivos_inicio = self.parametros.probabilidad_vivos_inicial

        # Si estamos calculando para un producto concreto, podemos establecer
        # un valor inicial fijo para alinear con el Excel de referencia
        # vivos_inicio = 1.0  # Valor por defecto

        caducidad_mensual = self._obtener_tasa_caducidad_mensual(
            self.parametros.periodo_vigencia
        )

        meses_proyeccion = anios_meses(self.parametros.periodo_vigencia)

        for mes in range(1, meses_proyeccion + 1):
            # Determinar año de póliza y edad actual
            anio_poliza = math.ceil(mes / 12)
            edad_actual = self.parametros.edad_actuarial + anio_poliza - 1

            # Cálculo de mortalidad
            mortalidad_anual = self._obtener_mortalidad_anual(edad_actual)
            mortalidad_mensual = self._calcular_mortalidad_mensual(mortalidad_anual)

            # CORRECCIÓN: El ajuste de mortalidad (ej: 150) viene como porcentaje
            # Primero convertimos a multiplicador (ej: 1.5) y luego aplicamos
            factor_ajuste = self.parametros.ajuste_mortalidad / 100.0
            mortalidad_ajustada = mortalidad_mensual * factor_ajuste

            # CORRECCIÓN: Aplicar la tasa correctamente por mil
            # Si mortalidad_mensual está en formato "por mil", debemos dividir por 1000
            fallecidos = vivos_inicio * mortalidad_ajustada / 1000.0
            vivos_despues_fallecidos = vivos_inicio - fallecidos

            # Cálculo de caducidad - Usamos los valores personalizados
            tasa_caducidad = caducidad_mensual.get(mes, 0.0)
            # La tasa está en formato decimal (ej: 0.04339 para 4.339%)
            # No necesitamos dividir por 100 porque ya viene en formato decimal
            caducados = vivos_despues_fallecidos * tasa_caducidad

            # Vivos final
            vivos_final = vivos_despues_fallecidos - caducados

            # Registrar resultados
            resultado = ResultadoMensual(
                mes=mes,
                anio_poliza=anio_poliza,
                edad_actual=edad_actual,
                vivos_inicio=Decimal(str(vivos_inicio)),
                fallecidos=Decimal(str(fallecidos)),
                vivos_despues_fallecidos=Decimal(str(vivos_despues_fallecidos)),
                caducados=Decimal(str(caducados)),
                vivos_final=Decimal(str(vivos_final)),
                mortalidad_anual=Decimal(str(mortalidad_anual)),
                mortalidad_mensual=Decimal(str(mortalidad_mensual)),
                mortalidad_ajustada=Decimal(
                    str(mortalidad_ajustada)
                ),  # Mantener en formato "por mil"
                tasa_caducidad=Decimal(str(tasa_caducidad)),
            )

            self.resultados.append(resultado)

            # El vivos inicio del siguiente mes es el vivos final del mes actual
            vivos_inicio = vivos_final

        return self.resultados

    def _obtener_mortalidad_anual(self, edad: int) -> float:
        """
        Obtiene la tasa de mortalidad anual para una edad específica

        Args:
            edad: Edad actual

        Returns:
            Tasa de mortalidad anual
        """
        # Si la edad supera la duración de pagos, no hay mortalidad
        if edad > self.parametros.get_duracion_pagos():
            return 0.0

        try:
            # Obtener la tasa de mortalidad desde el repositorio
            tasa_mortalidad = tabla_mortalidad_repository.get_tasa_mortalidad(
                edad=edad, sexo=self.parametros.sexo, fumador=self.parametros.fumador
            )
            return tasa_mortalidad
        except ValueError:
            # Si no se encuentra en la tabla, usar un valor por defecto
            return 0.0

    def _calcular_mortalidad_mensual(self, mortalidad_anual: float) -> float:
        """
        Calcula la tasa de mortalidad mensual a partir de la anual

        Args:
            mortalidad_anual: Tasa de mortalidad anual

        Returns:
            Tasa de mortalidad mensual
        """
        # Fórmula: (1-(1-q_x/1000)^(1/12))*1000
        return (1 - math.pow(1 - mortalidad_anual / 1000, 1 / 12)) * 1000

    def _es_mes_pago(self, mes: int) -> bool:
        """
        Determina si un mes específico es mes de pago según la frecuencia

        Args:
            mes: Número de mes

        Returns:
            True si es mes de pago, False en caso contrario
        """
        meses_frecuencia = self.parametros.get_meses_frecuencia()
        return (mes - 1) % meses_frecuencia == 0

    def _obtener_tasa_caducidad_mensual(self, periodo_vigencia: int) -> float:
        """
        Obtiene la tasa de caducidad para un año específico usando valores personalizados

        Args:
            anio: Año de póliza

        Returns:
            Tasa de caducidad como porcentaje
        """
        # Valores personalizados proporcionados por el usuario

        caducidad_parametrizado_mensual = (
            caducidad_repository.get_caducidad_mensual_data()
        )
        caducidad_por_año = caducidad_repository.get_caducidad_data()

        _caducidad_mensual = caducidad_mensual(
            periodo_vigencia, caducidad_parametrizado_mensual, caducidad_por_año
        )

        return _caducidad_mensual

    def _obtener_tasa_caducidad(self, anio: int, plazo: int) -> float:
        """
        Obtiene la tasa de caducidad para un año y plazo específicos

        Args:
            anio: Año de póliza
            plazo: Plazo en años

        Returns:
            Tasa de caducidad
        """
        try:
            return caducidad_repository.get_caducidad_valor(anio, plazo)
        except ValueError:
            # Si no se encuentra en la tabla, usar un valor por defecto
            return 0.0

    def calcular_reserva_matematica(self) -> Dict[str, float]:
        """
        Calcula la reserva matemática basada en los expuestos

        Returns:
            Diccionario con la reserva matemática total y desglosada por años
        """
        if not self.resultados:
            self.calcular_proyeccion()

        # Implementar aquí el cálculo de reserva matemática
        # Este es un cálculo complejo que depende de varios factores
        # Por ahora, retornamos un valor de ejemplo

        return {
            "total": sum(r.vivos_final for r in self.resultados),
            "por_anio": {
                anio: sum(
                    r.vivos_final for r in self.resultados if r.anio_poliza == anio
                )
                for anio in set(r.anio_poliza for r in self.resultados)
            },
        }

    def obtener_resumen(self) -> Dict[str, Union[float, Dict]]:
        """
        Obtiene un resumen de los resultados de la proyección

        Returns:
            Diccionario con el resumen de resultados
        """
        if not self.resultados:
            self.calcular_proyeccion()

        return {
            "vivos_inicial": self.resultados[0].vivos_inicio if self.resultados else 0,
            "vivos_final": self.resultados[-1].vivos_final if self.resultados else 0,
            "fallecidos_total": sum(r.fallecidos for r in self.resultados),
            "caducados_total": sum(r.caducados for r in self.resultados),
            "meses_calculados": len(self.resultados),
            "por_anio": {
                anio: {
                    "fallecidos": sum(
                        r.fallecidos for r in self.resultados if r.anio_poliza == anio
                    ),
                    "caducados": sum(
                        r.caducados for r in self.resultados if r.anio_poliza == anio
                    ),
                    "vivos_final": next(
                        (
                            r.vivos_final
                            for r in reversed(self.resultados)
                            if r.anio_poliza == anio
                        ),
                        0,
                    ),
                }
                for anio in sorted(set(r.anio_poliza for r in self.resultados))
            },
        }
