from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Union
from enum import Enum
import math
from decimal import Decimal
from src.core.constans import ANUAL, SEMESTRAL, TRIMESTRAL, MENSUAL

from src.repositories.tabla_mortalidad_repository import (
    tabla_mortalidad_repository,
    Sexo,
    EstadoFumador,
)
from src.repositories.caducidad_repository import caducidad_repository


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
    probabilidad_vivos_inicial: float = 1.0  # Por defecto comienza con 100% de vivos
    ajuste_mortalidad: float = (
        1.0  # Factor de ajuste para la mortalidad (tarifa de reaseguro)
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

    def calcular_proyeccion(self, meses: int = 12) -> List[ResultadoMensual]:
        """
        Calcula la proyección de expuestos para un número determinado de meses

        Args:
            meses: Número de meses a proyectar

        Returns:
            Lista de resultados mensuales
        """
        self.resultados = []

        # Inicializar valores para el primer mes
        vivos_inicio = self.parametros.probabilidad_vivos_inicial

        for mes in range(1, meses + 1):
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
            tasa_caducidad = self._obtener_tasa_caducidad_personalizada(anio_poliza)
            caducados = vivos_despues_fallecidos * tasa_caducidad / 100.0

            # Vivos final
            vivos_final = vivos_despues_fallecidos - caducados

            # Registrar resultados
            resultado = ResultadoMensual(
                mes=mes,
                anio_poliza=anio_poliza,
                edad_actual=edad_actual,
                vivos_inicio=vivos_inicio,
                fallecidos=fallecidos,
                vivos_despues_fallecidos=vivos_despues_fallecidos,
                caducados=caducados,
                vivos_final=vivos_final,
                mortalidad_anual=mortalidad_anual,
                mortalidad_mensual=mortalidad_mensual,
                mortalidad_ajustada=mortalidad_ajustada,  # Mantener en formato "por mil"
                tasa_caducidad=tasa_caducidad,
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

    def _obtener_tasa_caducidad_personalizada(self, anio: int) -> float:
        """
        Obtiene la tasa de caducidad para un año específico usando valores personalizados

        Args:
            anio: Año de póliza

        Returns:
            Tasa de caducidad como porcentaje
        """
        # Valores personalizados proporcionados por el usuario
        tasas_personalizadas = {
            1: 8.01940,
            2: 4.33901,
            3: 4.02713,
            4: 2.07597,
            5: 1.20659,
            6: 1.48385,
            7: 1.52937,
            8: 1.63549,
            9: 1.02871,
            10: 1.03940,
            11: 1.40449,
            12: 1.88282,
            13: 0.97,
            14: 0.97,
            15: 0.97,
            16: 0.97,
            17: 0.97,
            18: 0.97,
            19: 0.97,
            20: 0.97,
            21: 0.97,
            22: 0.97,
            23: 0.97,
            24: 0.97,
            25: 0.87,
            26: 0.87,
            27: 0.87,
            28: 0.87,
            29: 0.87,
            30: 0.87,
            31: 0.87,
            32: 0.87,
            33: 0.87,
            34: 0.87,
            35: 0.87,
            36: 0.87,
            37: 0.87,
            38: 0.87,
            39: 0.87,
            40: 0.87,
            41: 0.87,
            42: 0.87,
            43: 0.87,
            44: 0.87,
            45: 0.87,
            46: 0.87,
            47: 0.87,
            48: 0.87,
            49: 0.87,
            50: 0.87,
            51: 0.87,
            52: 0.87,
            53: 0.87,
            54: 0.87,
            55: 0.87,
            56: 0.87,
            57: 0.87,
            58: 0.87,
            59: 0.87,
            60: 0.87,
            61: 0.87,
            62: 0.87,
            63: 0.87,
            64: 0.87,
            65: 0.87,
            66: 0.87,
            67: 0.87,
            68: 0.87,
            69: 0.87,
            70: 0.87,
            71: 0.87,
            72: 100.00,
        }

        # Si el año está en la lista, devolver su valor, de lo contrario devolver 0
        return tasas_personalizadas.get(anio, 0.0)

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
