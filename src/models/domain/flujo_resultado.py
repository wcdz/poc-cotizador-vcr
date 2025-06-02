from dataclasses import dataclass
from src.models.domain.expuestos_mes import ExpuestosMes
from src.models.domain.parametros_calculados import ParametrosCalculados
from src.common.frecuencia_pago import FrecuenciaPago
from src.models.schemas.expuestos_mes_schema import ProyeccionActuarialOutput
from src.utils.frecuencia_meses import frecuencia_meses
from src.utils.anios_meses import anios_meses
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

    def calcular_gastos_mantenimiento(self, gastos_mantenimiento: float) -> List[float]:
        return [
            float(_.get("gasto_mantenimiento_total", 0))
            for _ in gastos_mantenimiento.get("resultados_mensuales", [])
        ]

    def calcular_comision(
        self,
        primas_recurrentes: List[float],
        asistencia: bool,
        frecuencia_pago_primas: int,
        costo_asistencia_funeraria: float,
        expuestos_mes: dict,
        comision: float,
    ) -> List[float]:
        """
        Calcula la comisión mensual, ajustando por asistencia funeraria si corresponde.
        Fórmula:
        Comisión = -(prima - ajuste_asistencia) * comisión
        """
        """
        Flujo y Resultado'!G9 (Comision) = -( F9 - SI(Parametros_Supuestos!$C$33="si"; C9 * Parametros_Supuestos!$C$17 * Parametros_Supuestos!$C$36 * 'Expuestos Mes'!AB2 ; 0)) * BUSCARV(A9;Parametros_Supuestos!$E$5 : $H$200; 3;0)

          F9 # ! input [primas_recurrentes

          Parametros_Supuestos!$C$33 # ! input [asistencia]

          C9 (Validador de Pago de Primas) = SI(( B9 - 1 ) / Parametros_Supuestos!$C$17 = ENTERO((B9-1)/Parametros_Supuestos!$C$17);1;0) # * SE CALCULA MES A MES   

          Parametros_Supuestos!$C$17 (Frecuencia elegida (MENSUAL, TRIMESTRAL, SEMESTRAL, ANUAL)) : input #! [ok]

          Parametros_Supuestos!$C$36 (Costo Mensual en US$  Asistencia Funeraria) : input #! [ok] null

          'Expuestos Mes'!AB2 (Vivos Inicio) : input, ya lo calculamos en expuestos_mes_service #! [ok]

          A9 (Año Poliza) # * MES POLIZA PERIODO * 12

          Parametros_Supuestos!$E$5 # * COMISIONES INPUT [OK]
        """
        resultados_mensuales = expuestos_mes.get("resultados_mensuales", [])
        comisiones = []

        for idx, prima in enumerate(primas_recurrentes):
            vivos_inicio = 0
            if idx < len(resultados_mensuales):
                vivos_inicio = float(resultados_mensuales[idx].get("vivos_inicio", 0))

            mes_poliza = idx + 1

            frecuencia_meses_valor = frecuencia_meses(frecuencia_pago_primas)
            # calcular validador pago primas mes a mes
            if ((mes_poliza - 1) % frecuencia_meses_valor) == 0:
                validador_pago_primas = 1
            else:
                validador_pago_primas = 0

            ajuste_asistencia = 0
            if asistencia:
                ajuste_asistencia = (
                    validador_pago_primas
                    * frecuencia_pago_primas
                    * costo_asistencia_funeraria
                    * vivos_inicio
                )

            comision_mes = -(prima - ajuste_asistencia) * comision
            comisiones.append(comision_mes)

        return comisiones

    def calcular_gastos_adquisicion(self, gasto_adquisicion: float) -> List[float]:
        """
        Calcula la lista de gastos de adquisición para cada periodo.

        La fórmula base es tomada de la celda 'Flujo y Resultado'!H9,
        que corresponde al valor constante en Gastos!E2.

        Gastos!E2 representa el gasto fijo de adquisición por póliza en soles,
        definido en Parametros_Supuestos!C40, que es un valor constante (por ejemplo, 1176).
        A partir del segundo periodo, el gasto de adquisición es considerado cero.

        Parámetros:
        ----------
        gasto_adquisicion : float
            Valor fijo del gasto de adquisición por póliza para el primer periodo.

        Retorna:
        --------
        List[float]
            Lista con los gastos de adquisición por periodo,
            donde el primer elemento es gasto_adquisicion y el resto son ceros.
        """
        return gasto_adquisicion
