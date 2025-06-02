from dataclasses import dataclass
from src.models.domain.expuestos_mes import ExpuestosMes
from src.models.domain.parametros_calculados import ParametrosCalculados
from src.common.frecuencia_pago import FrecuenciaPago
from src.models.schemas.expuestos_mes_schema import ProyeccionActuarialOutput
from src.utils.frecuencia_meses import frecuencia_meses
from typing import List


@dataclass
class FlujoResultado:
    """
    Modelo de dominio para el flujo y resultado.

    1. Gastos -> Primas Recurrentes
    """

    def calcular_primas_recurrentes(
        self,
        expuestos_mes: ProyeccionActuarialOutput,
        periodo_pago_primas: int,
        frecuencia_pago_primas: FrecuenciaPago,
        prima: float,
        fraccionamiento_primas: float,
    ):
        """
                Flujo y Resultado'!F9 (Primas Recurrente) =+SI( B9 / 12 > Parametros_Supuestos!$C$9 ;0 ;C9 *Parametros_Supuestos!$C$22 * 'Expuestos Mes'!AB2 ) * E9

                   B9 (Mes poliza) (Iteracion) # ! [Ok]

                   Parametros_Supuestos!$C$9 (Periodo de Pago de Primas) : input #! [ok]

                   C9 (Validador de Pago de primas = # ? 1) = =SI( (B9 - 1) / Parametros_Supuestos!$C$17 = ENTERO(( B9-1 ) / Parametros_Supuestos!$C$17) ; 1 ; 0)

                       B9 (Mes poliza) (Iteracion) # ! [Ok]

                       Parametros_Supuestos!$C$17 (Frecuencia elegida (MENSUAL, TRIMESTRAL, SEMESTRAL, ANUAL)) : input #! [ok]
        t
                   Parametros_Supuestos!$C$22 (prima) : input #! [ok]

                   'Expuestos Mes'!AB2 (vivos_inicio) : input, ya lo calculamos en expuestos_mes_service #! [ok]

                   E9 (Fracionamiento de primas) : input #! [ok] CONSTANTE
        """

        resultados_mensuales = expuestos_mes.get("resultados_mensuales", [])
        frecuencia_meses_valor = frecuencia_meses(frecuencia_pago_primas)

        primas_recurrentes = []

        for idx, fila in enumerate(resultados_mensuales):
            mes_poliza = idx + 1

            if mes_poliza / 12 > periodo_pago_primas:
                prima_mes = 0
            else:
                validador_pago = (
                    1 if ((mes_poliza - 1) % frecuencia_meses_valor == 0) else 0
                )
                vivos_inicio = float(fila.get("vivos_inicio", "0"))
                prima_mes = (
                    validador_pago * prima * vivos_inicio * fraccionamiento_primas
                )

            primas_recurrentes.append(prima_mes)

        return primas_recurrentes

    def calcular_siniestros(
        self, expuestos_mes: ProyeccionActuarialOutput, suma_asegurada: float
    ) -> List[float]:
        """
        Calcula los siniestros mensuales con signo negativo:
        siniestro = -suma_asegurada * fallecidos
        """
        resultados_mensuales = expuestos_mes.get("resultados_mensuales", [])
        siniestros = []

        for fila in resultados_mensuales:
            try:
                fallecidos = float(fila.get("fallecidos", 0))
                # ! print("fallecidos => ", fallecidos)
            except (TypeError, ValueError):
                fallecidos = 0.0
            siniestros.append(-suma_asegurada * fallecidos)

        return siniestros
