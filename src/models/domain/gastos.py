from dataclasses import dataclass
from src.models.domain.expuestos_mes import ExpuestosMes
from src.models.domain.parametros_calculados import ParametrosCalculados
from src.common.frecuencia_pago import FrecuenciaPago
from typing import List


@dataclass
class Gastos:
    """
    Modelo de dominio para los gastos.
    """

    # Atributos de entrada desde endpoint o cotizadorService
    periodo_vigencia: int

    # Atributos calculados
    mantenimiento_poliza: float  # viene desde parametros_calculados
    inflacion_mensual: float  # viene desde parametros_calculados

    # Atributos almacenados
    moneda: str
    valor_dolar: float
    valor_soles: float
    tiene_asistencia: bool  # Entendemos que no se usa
    costo_mensual_asistencia_funeraria: float  # Entendemos que no se usa
    moneda_poliza: float  # constante para todo los meses

    # Atributos para flujo y resultado
    periodo_pago_primas: int
    frecuencia_pago_primas: FrecuenciaPago  # Usar la enumeración
    prima: float
    expuestos_mes: ExpuestosMes  # (vivos_inicio)

    def calcular_gasto_mantenimiento_prima_co(
        self, primas_recurrentes: List[float], mantenimiento_poliza: float
    ) -> List[float]:
        """
        Calcula el gasto de mantenimiento de la prima co.
        Multiplica cada prima recurrente por el mantenimiento_poliza.

        Args:
            primas_recurrentes: Lista de primas recurrentes
            mantenimiento_poliza: Valor de mantenimiento por póliza

        Returns:
            Lista con cada prima multiplicada por el valor de mantenimiento
        """
        # Multiplicar cada elemento de la lista por mantenimiento_poliza
        return [prima * mantenimiento_poliza for prima in primas_recurrentes]

    def calcular_gastos_mantenimiento_moneda_poliza(
        self,
        moneda: str,
        valor_dolar: float,
        valor_soles: float,
        tiene_asistencia: bool,
        costo_mensual_asistencia_funeraria: float,
    ) -> float:
        """
            Calcula los gastos de mantenimiento de la póliza en función de la moneda y si tiene asistencia.

        Lógica:
        - Si la moneda es "Dólares", se toma el valor en dólares.
        - Si la moneda es otra (por ejemplo, "Soles"), se toma el valor en soles.
        - Si tiene asistencia funeraria, se suma el costo mensual de dicha asistencia.
        # * CONSIDERAR EL CALCULO PARA DOLARES Y VER COMO MANEJARLO
        """

        if moneda.lower() == "dólares":
            gasto_base = valor_dolar
        else:
            gasto_base = valor_soles

        gasto_total = gasto_base + (
            costo_mensual_asistencia_funeraria if tiene_asistencia else 0
        )

        return gasto_total

    def calcular_gastos_mantenimiento_fijo_poliza_anual(
        self, expuestos_mes: ExpuestosMes, gastos_mantenimiento_moneda_poliza: float
    ):
        resultados_mensuales = expuestos_mes.get("resultados_mensuales", [])

        gastos_mantenimiento_fijo_poliza_anual = []

        for idx, fila in enumerate(resultados_mensuales):
            mes_poliza = idx + 1

            vivos_inicio = float(fila.get("vivos_inicio", "0"))

            gasto_mantenimiento_fijo_poliza_anual = (
                gastos_mantenimiento_moneda_poliza * vivos_inicio
            )

            gastos_mantenimiento_fijo_poliza_anual.append(
                gasto_mantenimiento_fijo_poliza_anual
            )

        return gastos_mantenimiento_fijo_poliza_anual

    def calcular_factor_inflacion(
        self,
        gasto_mantenimiento_prima_co: List[float],  # F2
        gasto_mantenimiento_fijo_poliza_anual: List[float],  # G2
        inflacion_mensual: float,
    ) -> List[float]:
        """
        Calcula el factor de inflación mensual para cada período (mes), utilizado en el ajuste
        de los gastos de mantenimiento de una póliza.

        Fórmula tomada de Excel:
            =SI(G2 + F2 = 0; 0; (1 + InflacionMensual) ^ (Mes - 1))

        Donde:
        - G2: Gasto fijo de mantenimiento por póliza anual (gasto_mantenimiento_fijo_poliza_anual[i])
        - F2: Gasto de mantenimiento de prima CO (gasto_mantenimiento_prima_co[i])
        - InflacionMensual: porcentaje de inflación mensual expresado como decimal (ej. 0.02 para 2%)
        - Mes: el número de mes correspondiente (1 para enero, 2 para febrero, etc.)

        Lógica:
        - Si la suma de G2 y F2 es 0, entonces el factor de inflación es 0.
        - Si no, se aplica la fórmula exponencial (1 + inflacion_mensual) elevado a (mes - 1).

        Retorna:
        - Una lista con los factores de inflación correspondientes a cada mes.
        """
        factores_inflacion = []

        for i in range(len(gasto_mantenimiento_prima_co)):
            f2 = gasto_mantenimiento_prima_co[i]
            g2 = gasto_mantenimiento_fijo_poliza_anual[i]
            mes = i + 1  # mes = índice + 1

            if f2 + g2 == 0:
                factor = 0
            else:
                factor = (1 + inflacion_mensual) ** (mes - 1)

            factores_inflacion.append(factor)

        return factores_inflacion

    def calcular_gasto_mantenimiento_total(
        self,
        gasto_mantenimiento_prima_co: List[float],
        gasto_mantenimiento_fijo_poliza_anual: List[float],
        factor_inflacion: List[float],
        periodo_vigencia: int,
    ) -> List[float]:
        """
            I (Gasto Mantenimiento Total) => =SI( A2 > Parametros_Supuestos!$C$8; 0; (F2 + G2) * H2)

        A2 (año_polizas_repitentes * 12 hasta el año periodo_vigencia (1,1,1 x 12.... 6,6,6 x12...., año_poliza_repitente x 12)): Se repite el año de poliza cada 12 meses #! [ok]

        Parametros_Supuestos!$C$8 (periodo_vigencia): input #![ok]
        """
        gasto_mantenimiento_total = []

        for i in range(len(gasto_mantenimiento_prima_co)):
            f2 = gasto_mantenimiento_prima_co[i]
            g2 = gasto_mantenimiento_fijo_poliza_anual[i]
            h2 = factor_inflacion[i]
            anio = i // 12 + 1

            if anio > periodo_vigencia:
                gasto = 0
            else:
                gasto = (f2 + g2) * h2

            gasto_mantenimiento_total.append(gasto)

        return gasto_mantenimiento_total
