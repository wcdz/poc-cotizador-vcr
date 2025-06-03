from dataclasses import dataclass
from src.models.domain.expuestos_mes import ExpuestosMes
from src.utils.anios_meses import anios_meses


@dataclass
class ParametrosReserva:
    """Parámetros necesarios para los cálculos de reserva"""

    margen_solvencia_reserva: float
    periodo_vigencia: int


@dataclass
class Reserva:
    """Modelo de dominio para la reserva"""

    def calcular_moce(
        self,
        tasa_interes_mensual: float,
        periodo_vigencia: int,
        margen_reserva: float,
    ):
        """
        Z2 (MOCE) = Parametros_Supuestos!$C$71 * ( VNA(Parametros_Supuestos!$C$59; Y3: $Y$851) + Y2)

            Parametros_Supuestos!$C$71 (tir_mensual)  # ! input [OK]

            Parametros_Supuestos!$C$59 (tasa_interes_mensual) # ! input [OK]

            Y2 (5% Rsva) = J2 * 5% (margen_reserva) # ! NUEVA CONSTANTE

            Y3  # ! (LO MISMO QUE Y2 PERO AGARRA DEL 2DA VALOR DE LA LISTA)
        """
        return (tasa_interes_mensual, periodo_vigencia, margen_reserva)

    def calcular_saldo_reserva(
        self,
        tasa_interes_mensual: float,
        rescate,
        periodo_vigencia: int,
        expuestos_mes: ExpuestosMes,
    ):
        """
        J2 (Saldo_Reserva) = =MAX( SI ( I2 + VNA( Parametros_Supuestos!$C$59; I3 : I946 ) < 0; 0; I2+ VNA(Parametros_Supuestos!$C$59; I3 : I946 )); R2 *'Expuestos Mes'!L2)
        """

        # C59 tasa_interes_mensual
        # I3 flujo pasivo
        # R2 calculo_rescate
        # L2 expuestos_mes

        return 1

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
        periodo_vigencia: int,
        prima: float,
        fraccionamiento_primas: float,
        devolucion: list[dict],
        porcentaje_devolucion: float,
    ):

        # * F2
        rescate = self.calcular_rescate(
            periodo_vigencia,
            prima,
            fraccionamiento_primas,
            devolucion,
            porcentaje_devolucion,
        )

        # * CADUCADOS
        resultados_mes = expuestos_mes.get("resultados_mensuales", [])
        ajuste_devolucion_anticipada = []
        for idx, fila in enumerate(resultados_mes):
            ajuste_devolucion_anticipada.append(
                float(rescate[idx]) * float(fila.get("caducados", 0))
            )

        return ajuste_devolucion_anticipada

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
