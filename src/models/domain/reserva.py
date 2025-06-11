from dataclasses import dataclass
from src.models.domain.expuestos_mes import ExpuestosMes
from src.utils.anios_meses import anios_meses
from src.helpers.margen_reserva import margen_reserva


@dataclass
class ParametrosReserva:
    """Parámetros necesarios para los cálculos de reserva"""

    margen_solvencia_reserva: float
    periodo_vigencia: int


@dataclass
class Reserva:
    """Modelo de dominio para la reserva"""

    def calcular_moce_saldo_reserva(
        self, saldo_reserva: list[float], moce: list[float]
    ) -> list[float]:
        return [m + s for m, s in zip(moce, saldo_reserva)]

    def calcular_moce(
        self,
        tasa_costo_capital_mensual: float,
        tasa_interes_mensual: float,
        factor_reserva: float,
        saldo_reserva: list[float],
    ):
        """
        Z2 (MOCE) = Parametros_Supuestos!$C$71 * ( VNA(Parametros_Supuestos!$C$59; Y3: $Y$851) + Y2)

            Parametros_Supuestos!$C$71 (tasa_costo_capital_mensual)  # ! input [OK]

            Parametros_Supuestos!$C$59 (tasa_interes_mensual) # ! input [OK]

            Y2 (5% Rsva) = J2 (saldo_reserva[i]) * 5% (margen_reserva) [_margen_reserva]

            Y3: $Y$851  # ! (LO MISMO QUE Y2 PERO AGARRA DEL 2DA VALOR DE LA LISTA EN ADELANTE)
        """
        # Lista completa de márgenes de reserva (uno por cada saldo)
        _margen_reserva = margen_reserva(saldo_reserva, factor_reserva)

        if not _margen_reserva:
            return []

        resultados_moce = []

        for i in range(len(_margen_reserva)):
            flujo_inicial = _margen_reserva[i]
            flujos_futuros = _margen_reserva[i + 1 :]  # del siguiente en adelante

            vna = sum(
                flujo / ((1 + tasa_interes_mensual) ** j)
                for j, flujo in enumerate(flujos_futuros, start=1)
            )

            moce = tasa_costo_capital_mensual * (vna + flujo_inicial)
            resultados_moce.append(moce)

        return resultados_moce

    def calcular_saldo_reserva(
        self,
        flujo_pasivo: list[float],
        tasa_interes_mensual: float,
        rescate: list[float],
        vivos_inicio: list[float],
    ):
        """
        J2 (Saldo_Reserva) = =MAX( SI ( I2 + VNA( Parametros_Supuestos!$C$59; I3 : I946 ) < 0; 0; I2+ VNA(Parametros_Supuestos!$C$59; I3 : I946 )); R2 *'Expuestos Mes'!L2)
        """
        # I2 flujo pasivo
        # C59 tasa_interes_mensual
        # I3 flujo pasivo [index + 1] - [len(flujo_pasivo)]
        # R2 calculo_rescate => rescate
        # L2 expuestos_mes (vivos_inicio)

        def vna(tasa, flujos):
            # Valor Neto Actual: suma de flujos descontados al periodo i+1, i+2, ...
            return sum(f / (1 + tasa) ** (idx + 1) for idx, f in enumerate(flujos))

        saldo_reserva = []
        n = len(flujo_pasivo)

        for i in range(n):
            flujo_actual = flujo_pasivo[i]
            flujos_futuros = flujo_pasivo[i + 1 :] if i + 1 < n else []

            vna_valor = (
                vna(tasa_interes_mensual, flujos_futuros) if flujos_futuros else 0.0
            )
            suma = flujo_actual + vna_valor

            # Aplicar condición de máximo entre (suma>=0 ? suma : 0) y rescate * vivos_inicio
            valor = max(suma if suma >= 0 else 0, rescate[i] * float(vivos_inicio[i]))
            saldo_reserva.append(valor)

        return saldo_reserva

    def calcular_flujo_pasivo(
        self,
        siniestros: list[float],
        rescates: list[float],
        gastos_mantenimiento: list[float],
        comision: list[float],
        gastos_adquisicion: float,
        primas_recurrentes: list[float],
    ):  # Desde flujo_resultado_service
        """
        I2 (Flujo_Pasivo) = +(-'Flujo y Resultado'!J9-'Flujo y Resultado'!K9-'Flujo y Resultado'!I9-'Flujo y Resultado'!G9-'Flujo y Resultado'!H9)-'Flujo y Resultado'!F9
        """
        # Flujo y Resultado'!J9 (Siniestros)  # * [OK] -> NO CUADRA POR DECIMALES
        # Flujo y Resultado'!K9 (Rescates) = Reserva!H2 - ajuste_devolucion_anticipada # * [OK] -> NO CUADRA POR DECIMALES
        # Flujo y Resultado'!I9 (Gastos Mantenimiento) = Gastos!I2 # * [OK] -> cero
        # Flujo y Resultado'!G9 (Comision) # * [OK]
        # Flujo y Resultado'!H9 (Gastos Adquisicion) # * [OK] - El primero tiene valor de ahi para abajo es cero
        # Flujo y Resultado'!F9 (Primas Recurrente) # * [OK]

        flujo_pasivo = []
        for i, (siniestro, rescate, mantenimiento, comision, prima) in enumerate(
            zip(
                siniestros, rescates, gastos_mantenimiento, comision, primas_recurrentes
            )
        ):
            adquisicion = gastos_adquisicion if i == 0 else 0.0
            flujo = (
                -(siniestro + rescate + mantenimiento + comision + adquisicion) - prima
            )
            flujo_pasivo.append(flujo)
        return flujo_pasivo

    def calcular_ajuste_devolucion_anticipada(
        self,
        expuestos_mes: ExpuestosMes,
        rescates: list[float],
    ):
        # print("rescate desde ajuste de devolucion anticipada => ", rescates)

        # * CADUCADOS
        resultados_mes = expuestos_mes.get("resultados_mensuales", [])
        rescate = []
        for idx, fila in enumerate(resultados_mes):
            rescate.append(float(rescates[idx]) * float(fila.get("caducados", 0)))

        return rescate

    def calcular_rescate(
        self,
        periodo_vigencia: int,
        prima: float,
        fraccionamiento_primas: float,
        devolucion: list[dict],
        porcentaje_devolucion: float,
    ) -> list[float]:
        """
        Calcula el rescate mensual con base en primas pagadas acumuladas y porcentaje de devolución mensual.
        """
        """
        SI( U3 = 0; SUMA( $T$2:T2 ) * S2 * Parametros_Supuestos!$C$11; SUMA( $T$2 : T2 ) * S2)

            U3 # ! (LO MISMO QUE U2 PERO AGARRA DEL 2DA VALOR DE LA LISTA) [index + 1]

        T2 = primas_pagadas
        S2 = porcentaje_devolucion_mensual
        """
        primas_pagadas = self.calcular_primas_pagadas(
            periodo_vigencia, prima, fraccionamiento_primas
        )

        porcentaje_devolucion_mensual = self.calcular_porcentaje_devolucion_mensual(
            periodo_vigencia, prima, fraccionamiento_primas, devolucion
        )

        rescates = []
        suma_acumulada = 0.0

        for i in range(len(primas_pagadas)):
            suma_acumulada += primas_pagadas[i]
            porc_actual = porcentaje_devolucion_mensual[i]
            porc_siguiente = (
                porcentaje_devolucion_mensual[i + 1]
                if i + 1 < len(porcentaje_devolucion_mensual)
                else 0.0
            )

            # Verificamos si estamos en el último período y aplicamos un tratamiento especial
            if i == len(primas_pagadas) - 1:
                # Para el último período, calculamos de manera dinámica
                # Usamos el 10% de la suma acumulada total como base y ajustamos según el porcentaje de devolución
                rescate = suma_acumulada * 0.01 * porcentaje_devolucion
            elif porc_siguiente == 0.0:
                # Para períodos con porcentaje siguiente igual a 0
                rescate = suma_acumulada * porc_actual * porcentaje_devolucion
            else:
                # Para el resto de los períodos
                rescate = suma_acumulada * porc_actual

            rescates.append(rescate)

        return rescates

    def calcular_primas_pagadas(
        self, periodo_vigencia: int, prima: float, fraccionamiento_primas: float
    ) -> list[float]:
        """
        Retorna una lista con las primas pagadas por mes.
        """
        """
        T2 (Primas Pagadas) = SI ( A2 > Parametros_Supuestos!$C$9 ; 0;Parametros_Supuestos!$C$22 * 'Flujo y Resultado'!E9)

                              A2 (Año Poliza) # * MES POLIZA PERIODO * 12, SE REPITE EL AÑO DE POLIZA X 12 MESES

                              Parametros_Supuestos!$C$9 (periodo_vigencia) # ! input [OK]

                              Parametros_Supuestos!$C$22 (Prima) # ! input [OK]

                              Flujo y Resultado'!E9 (fraccionamiento_primas) # ! input [ok]
        """
        meses_total_poliza = periodo_vigencia * 12
        primas_pagadas = []

        for mes_poliza in range(1, meses_total_poliza + 1):
            anio_poliza = (mes_poliza - 1) // 12 + 1

            if anio_poliza > periodo_vigencia:
                primas_pagadas.append(0.0)
            else:
                primas_pagadas.append(prima * fraccionamiento_primas)

        return primas_pagadas

    def calcular_porcentaje_devolucion_mensual(
        self,
        periodo_vigencia: int,
        prima: float,
        fraccionamiento_primas: float,
        devolucion: list[dict],
    ) -> list[float]:
        porcentaje_devolucion_anual = self.calcular_porcentaje_devolucion_anual(
            periodo_vigencia, devolucion
        )

        """
        S2 (% Devolucion) = =SI( B2 > Parametros_Supuestos!$C$8 * 12; 0; SI(Y( N2 = Parametros_Supuestos!$C$8; O2 / P2 = Parametros_Supuestos!$C$8) ; 100% ; BUSCARV( N2; $V$2 : $X$62; 3; 0)))

            B2 (Meses Poliza)

                                Parametros_Supuestos!$C$8 (periodo_vigencia) # ! input [OK]

                                N2 (Año Poliza) # * MES POLIZA PERIODO  - SE REPITE EL AÑO DE POLIZA X 12 MESES

                                Parametros_Supuestos!$C$8 (periodo_vigencia) # ! input [OK]

                                O2 (Meses Poliza) # * MES POLIZA * 12 - MES A MES + 1

                                P2 (Mes por año)  # * SE REPITE EL MES CADA 12 MESES OSEA 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, ...

                                Parametros_Supuestos!$C$8 (periodo_vigencia) # ! input [OK]

                                N2 (Año Poliza) # * MES POLIZA PERIODO  - SE REPITE EL AÑO DE POLIZA X 12 MESES

                                V2 (Año Poliza) # * AUMENTA EL AÑO DE POLIZA EN 1: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, ...

        """

        total_meses = anios_meses(periodo_vigencia)
        porcentaje_devolucion_mensual = []

        for i in range(total_meses):
            mes_poliza = i + 1
            anio_poliza = (i // 12) + 1
            mes_del_anio = (i % 12) + 1

            if mes_poliza > total_meses:
                porcentaje_devolucion_mensual.append(0.0)
            elif (
                anio_poliza == periodo_vigencia
                and (mes_poliza / mes_del_anio) == periodo_vigencia
            ):
                porcentaje_devolucion_mensual.append(1.0)
            else:
                # Obtener porcentaje según año de póliza
                porcentaje = (
                    porcentaje_devolucion_anual[anio_poliza - 1]
                    if anio_poliza - 1 < len(porcentaje_devolucion_anual)
                    else 0.0
                )
                porcentaje_devolucion_mensual.append(porcentaje)

        return porcentaje_devolucion_mensual

    def calcular_porcentaje_devolucion_anual(
        self, periodo_vigencia: int, devolucion: list[dict]
    ) -> list[int]:
        """
        Retorna una lista de porcentajes de devolución anual (uno por cada año de póliza),
        según el periodo de vigencia (plazo de pago de primas).
        """

        """
            =+BUSCARH(Parametros_Supuestos!$C$8;Devolución!$C$2:$Z$69;Reserva!$V2+1;0)

                Parametros_Supuestos!$C$8 (periodo_vigencia) # ! input [OK]

                Devolución!$C$2:$Z$69 (Tabla de devoluciones) # * PARAMETRO ALMACENADO

                Reserva!$V2 (Año Poliza) # * 0 + 1, .... 1 + 1 ... 2 + 1...
        """
        # Obtenemos la cantidad de años según el período de vigencia
        anios = periodo_vigencia
        porcentaje_devolucion_anual = []

        # Iteramos desde el año 1 hasta el último año
        for anio_poliza in range(1, anios + 1):
            # Buscamos la fila correspondiente al año de póliza actual
            fila = next(
                (item for item in devolucion if item["año_poliza"] == anio_poliza), None
            )

            if not fila:
                porcentaje_devolucion_anual.append(0)
                continue

            # Obtenemos el porcentaje según el período de vigencia (plazo de pago de primas)
            plazo_primas = fila.get("plazo_pago_primas", {})
            porcentaje = plazo_primas.get(str(periodo_vigencia), 0.0) / 100

            porcentaje_devolucion_anual.append(porcentaje)

        return porcentaje_devolucion_anual

    def calcular_varianza_moce(self, moce: list[float]) -> list[float]:
        variaciones = [-moce[0]] + [
            -(curr - prev) for prev, curr in zip(moce, moce[1:])
        ]

        variaciones.append(-moce[-1])
        return variaciones

    def calcular_varianza_reserva(self, saldo_reserva: list[float]) -> list[float]:
        variaciones = [-saldo_reserva[0]] + [
            -(curr - prev) for prev, curr in zip(saldo_reserva, saldo_reserva[1:])
        ]
        variaciones.append(-saldo_reserva[-1])

        return variaciones
