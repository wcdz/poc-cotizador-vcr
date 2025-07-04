from src.models.schemas.cotizacion_schema import (
    CotizacionInput,
    CotizacionOutput,
    ParametrosAlmacenados as ParametrosAlmacenadosSchema,
    ParametrosCalculados as ParametrosCalculadosSchema,
    TipoProducto,
)

from src.repositories.parametros_repository import JsonParametrosRepository
from src.models.domain.parametros_calculados import (
    ParametrosCalculados as ParametrosCalculadosDomain,
)
from src.repositories.tasa_interes_repository import JsonTasaInteresRepository
from src.repositories.devolucion_repository import JsonDevolucionRepository
from src.services.expuestos_mes_service import ExpuestosMesService
from src.services.gastos_service import GastosService
from src.services.flujo_resultado_service import FlujoResultadoService
from src.services.margen_solvencia_service import MargenSolvenciaService
from src.services.reserva_service import ReservaService
from src.repositories.factores_pago_repository import JsonFactoresPagoRepository
from src.models.products.rumbo.rumbo import Rumbo


class CotizadorService:
    """Servicio unificado para cotizaciones de distintos productos"""

    def __init__(self):
        self.parametros_repository = JsonParametrosRepository()
        self.tasa_interes_repository = JsonTasaInteresRepository()
        self.devolucion_repository = JsonDevolucionRepository()
        self.factores_pago_repository = JsonFactoresPagoRepository()
        self.expuestos_mes = ExpuestosMesService()
        self.gastos_service = GastosService()
        self.flujo_resultado_service = FlujoResultadoService()
        self.margen_solvencia_service = MargenSolvenciaService()
        self.reserva_service = ReservaService()
        self.rumbo = Rumbo(
            self.expuestos_mes,
            self.flujo_resultado_service,
            self.gastos_service,
            self.reserva_service,
            self.margen_solvencia_service,
        )

    def cotizar(self, cotizacion_input: CotizacionInput) -> CotizacionOutput:
        """
        Realiza la cotización para el producto especificado
        Determina qué lógica de cotización aplicar según el tipo de producto
        """
        # Validar que los parámetros correspondan al producto
        cotizacion_input.validate_product_parameters()

        # Obtener parámetros almacenados
        parametros_almacenados = self._obtener_parametros_almacenados(
            cotizacion_input.producto.value
        )

        # Obtener tasas de interés - pasar el diccionario completo sin procesar
        tasas_interes_data = self.tasa_interes_repository.get_tasas_interes()

        factores_pago = self.factores_pago_repository.get_factores_pago()

        # Extraer la prima del esquema de entrada si es RUMBO
        prima = 0.0
        periodo_vigencia = cotizacion_input.parametros.periodo_vigencia
        periodo_pago_primas = cotizacion_input.parametros.periodo_pago_primas
        if cotizacion_input.producto == TipoProducto.RUMBO:
            prima = cotizacion_input.parametros.prima
            suma_asegurada = parametros_almacenados.suma_asegurada_rumbo

        # Crear el modelo de dominio con los parámetros necesarios para los cálculos
        parametros_dominio = ParametrosCalculadosDomain(
            prima=prima,
            gasto_adquisicion=parametros_almacenados.gasto_adquisicion,
            gasto_mantenimiento=parametros_almacenados.gasto_mantenimiento,
            tasa_costo_capital_tir=parametros_almacenados.tir,
            moce=parametros_almacenados.moce,
            inflacion_anual=parametros_almacenados.inflacion_anual,
            margen_solvencia=parametros_almacenados.margen_solvencia,
            fondo_garantia=parametros_almacenados.fondo_garantia,
            periodo_vigencia=periodo_vigencia,
            tasas_interes_data=tasas_interes_data,
            periodo_pago_primas=periodo_pago_primas,
            frecuencia_pago_primas=cotizacion_input.parametros.frecuencia_pago_primas,
            factores_pago=factores_pago,
            suma_asegurada=suma_asegurada,
        )

        # Convertir el modelo de dominio a esquema de respuesta
        parametros_calculados = self._convertir_a_esquema(parametros_dominio)

        expuestos_mes = self.expuestos_mes.calcular_expuestos_mes(
            edad_actuarial=cotizacion_input.parametros.edad_actuarial,
            sexo=cotizacion_input.parametros.sexo,
            fumador=(
                cotizacion_input.parametros.fumador
                if cotizacion_input.parametros.fumador
                else False
            ),
            frecuencia_pago_primas=cotizacion_input.parametros.frecuencia_pago_primas,
            periodo_vigencia=periodo_vigencia,
            periodo_pago_primas=periodo_pago_primas,
            ajuste_mortalidad=parametros_almacenados.ajuste_mortalidad,
        )

        gastos = self.gastos_service.calcular_gastos(
            periodo_vigencia=periodo_vigencia,
            periodo_pago_primas=periodo_pago_primas,
            prima=prima,
            expuestos_mes=expuestos_mes,
            frecuencia_pago_primas=cotizacion_input.parametros.frecuencia_pago_primas,
            mantenimiento_poliza=parametros_calculados.mantenimiento_poliza,
            moneda=parametros_almacenados.moneda,
            valor_dolar=parametros_almacenados.valor_dolar,
            valor_soles=parametros_almacenados.valor_soles,
            tiene_asistencia=parametros_almacenados.tiene_asistencia,
            costo_mensual_asistencia_funeraria=parametros_almacenados.costo_mensual_asistencia_funeraria,
            inflacion_mensual=parametros_calculados.inflacion_mensual,
        )

        primas_recurrentes = self.flujo_resultado_service.calcular_primas_recurrentes(
            expuestos_mes=expuestos_mes,
            periodo_pago_primas=periodo_pago_primas,
            frecuencia_pago_primas=cotizacion_input.parametros.frecuencia_pago_primas,
            prima=prima,
        )

        # print("\n")
        # print("primas_recurrentes => ", primas_recurrentes)

        siniestros = self.flujo_resultado_service.calcular_siniestros(
            expuestos_mes=expuestos_mes,
            suma_asegurada=suma_asegurada,
        )

        # print("\n")
        # print("siniestros => ", siniestros)

        rescate = self.reserva_service.calcular_rescate(
            periodo_vigencia=periodo_vigencia,
            prima=cotizacion_input.parametros.prima,
            fraccionamiento_primas=parametros_almacenados.fraccionamiento_primas,
            porcentaje_devolucion=cotizacion_input.parametros.porcentaje_devolucion,
        )

        # print("\n")
        # print(cotizacion_input.parametros.porcentaje_devolucion)
        # print("\n")

        # print("rescate => ", rescate)

        recates_ajuste_devolucion_anticipada = (
            self.flujo_resultado_service.calcular_rescates(
                expuestos_mes=expuestos_mes,
                rescate=rescate,
            )
        )

        # print("\n")
        # print("recates_ajuste_devolucion_anticipada => ",recates_ajuste_devolucion_anticipada)

        gastos_mantenimiento = (
            self.flujo_resultado_service.calcular_gastos_mantenimiento(
                gastos_mantenimiento=gastos,
            )
        )

        # print("\n")
        # print("gastos_mantenimiento => ", gastos_mantenimiento)

        gasto_adquisicion = self.flujo_resultado_service.calcular_gasto_adquisicion(
            gasto_adquisicion=parametros_almacenados.gasto_adquisicion,
        )

        # print("\n")
        # print("gastos_adquisicion => ", gasto_adquisicion)

        comision = self.flujo_resultado_service.calcular_comision(
            primas_recurrentes=primas_recurrentes,
            asistencia=parametros_almacenados.tiene_asistencia,
            frecuencia_pago_primas=cotizacion_input.parametros.frecuencia_pago_primas,
            costo_asistencia_funeraria=parametros_almacenados.costo_mensual_asistencia_funeraria,
            expuestos_mes=expuestos_mes,
            comision=parametros_almacenados.comision,
        )

        # print("\n")
        # print("comision => ", comision)

        flujo_resultado = {"primas_recurrentes": primas_recurrentes}

        flujo_pasivo = self.reserva_service.calcular_flujo_pasivo(
            siniestros,
            recates_ajuste_devolucion_anticipada,
            gastos_mantenimiento,
            comision,
            gasto_adquisicion,
            primas_recurrentes,
        )
        # print("flujo pasivo => ", flujo_pasivo)

        saldo_reserva = self.reserva_service.calcular_saldo_reserva(
            flujo_pasivo,
            parametros_calculados.tasa_interes_mensual,
            rescate,
            expuestos_mes,
        )

        # print("saldo_reserva => ", saldo_reserva)

        moce = self.reserva_service.calcular_moce(
            tasa_costo_capital_mensual=parametros_calculados.tasa_costo_capital_mensual,
            tasa_interes_mensual=parametros_calculados.tasa_interes_mensual,
            margen_reserva=parametros_almacenados.margen_solvencia,
            saldo_reserva=saldo_reserva,
        )

        # print("moce => ", moce)

        moce_saldo_reserva = self.reserva_service.calcular_moce_saldo_reserva(
            saldo_reserva=saldo_reserva,
            moce=moce,
        )

        # print("moce_saldo_reserva => ", moce_saldo_reserva)
        reserva_fin_año = self.margen_solvencia_service.calcular_reserva_fin_año(
            saldo_reserva=saldo_reserva,
            moce=moce,
        )

        # print("reserva_fin_año => ", reserva_fin_año)

        margen_solvencia = self.margen_solvencia_service.calcular_margen_solvencia(
            reserva_fin_año=reserva_fin_año,
            margen_solvencia_reserva=parametros_calculados.reserva,
        )

        # print("margen_solvencia => ", margen_solvencia)

        varianza_margen_solvencia = (
            self.margen_solvencia_service.calcular_varianza_margen_solvencia(
                margen_solvencia=margen_solvencia,
            )
        )

        # print("varianza_margen_solvencia => ", varianza_margen_solvencia)

        ingreso_inversiones = (
            self.margen_solvencia_service.calcular_ingreso_inversiones(
                reserva_fin_año=reserva_fin_año,
                tasa_inversion=parametros_calculados.tasa_inversion,
            )
        )

        # print("ingreso_inversiones => ", ingreso_inversiones)

        ingresiones_inversiones_margen_solvencia = (
            self.margen_solvencia_service.ingresiones_inversiones_margen_solvencia(
                margen_solvencia=margen_solvencia,
                tasa_inversion=parametros_calculados.tasa_inversion,
            )
        )

        # print("ingresiones_inversiones_margen_solvencia => ",ingresiones_inversiones_margen_solvencia)

        ingreso_total_inversiones = self.margen_solvencia_service.calcular_ingreso_total_inversiones(
            ingreso_inversiones=ingreso_inversiones,
            ingresiones_inversiones_margen_solvencia=ingresiones_inversiones_margen_solvencia,
        )

        # print("ingreso_total_inversiones => ", ingreso_total_inversiones)

        varianza_moce = self.reserva_service.calcular_varianza_moce(moce)

        # print("varianza_moce => ", varianza_moce)

        varianza_reserva = self.reserva_service.calcular_varianza_reserva(saldo_reserva)

        # print("saldo_reserva => ", saldo_reserva)

        variacion_reserva = self.flujo_resultado_service.calcular_variacion_reserva(
            varianza_reserva=varianza_reserva,
            varianza_moce=varianza_moce,
        )

        # print("\n")
        # print("variacion_reserva => ", variacion_reserva)
        # print("\n")

        utilidad_pre_pi_ms = self.flujo_resultado_service.calcular_utilidad_pre_pi_ms(
            primas_recurrentes=primas_recurrentes,
            comision=comision,
            gasto_adquisicion=gasto_adquisicion,
            gastos_mantenimiento=gastos_mantenimiento,
            siniestros=siniestros,
            rescates=recates_ajuste_devolucion_anticipada,
            variacion_reserva=variacion_reserva,
        )

        # print("\n")
        #print("utilidad_pre_pi_ms => ", utilidad_pre_pi_ms)

        IR = self.flujo_resultado_service.calcular_IR(
            utilidad_pre_pi_ms=utilidad_pre_pi_ms,
            impuesto_renta=parametros_almacenados.impuesto_renta,
        )

        flujo_accionista = self.flujo_resultado_service.calcular_flujo_accionista(
            utilidad_pre_pi_ms=utilidad_pre_pi_ms,
            varianza_margen_solvencia=varianza_margen_solvencia,
            IR=IR,
            ingreso_total_inversiones=ingreso_total_inversiones,
        )

        # print("flujo_accionista => ", flujo_accionista)

        auxiliar_vna = self.flujo_resultado_service.auxiliar(
            flujo_accionista=flujo_accionista,
            tasa_costo_capital_mes=parametros_calculados.tasa_costo_capital_mes,
        )

        # print("auxiliar_vna [COTIZACION ESPERADA] => ", auxiliar_vna)

        # print("factores_pago => ", self.factores_pago_repository.get_factores_pago())

        # Calcular el porcentaje de devolución óptimo si es producto RUMBO
        porcentaje_devolucion_optimo = None
        if cotizacion_input.producto == TipoProducto.RUMBO:
            porcentaje_devolucion_optimo = (
                self.rumbo.calcular_porcentaje_devolucion_optimo(
                    cotizacion_input=cotizacion_input,
                    parametros_almacenados=parametros_almacenados,
                    tasas_interes_data=tasas_interes_data,
                    prima=prima,
                    flujo_resultado_service=self.flujo_resultado_service,
                    parametros_calculados=parametros_calculados,
                    periodo_vigencia=periodo_vigencia,
                    periodo_pago_primas=periodo_pago_primas,
                    expuestos_mes=expuestos_mes,
                    gastos=gastos,
                    primas_recurrentes=primas_recurrentes,
                    siniestros=siniestros,
                    flujo_accionista=flujo_accionista,
                    flujo_pasivo=flujo_pasivo,
                    saldo_reserva=saldo_reserva,
                    moce=moce,
                    reserva_fin_año=reserva_fin_año,
                    margen_solvencia=margen_solvencia,
                    varianza_margen_solvencia=varianza_margen_solvencia,
                    ingreso_total_inversiones=ingreso_total_inversiones,
                    varianza_reserva=varianza_reserva,
                    varianza_moce=varianza_moce,
                    gastos_mantenimiento=gastos_mantenimiento,
                    gasto_adquisicion=gasto_adquisicion,
                    comision=comision,
                    IR=IR,
                    utilidad_pre_pi_ms=utilidad_pre_pi_ms,
                )
            )

            # print("\nPorcentaje de devolución óptimo calculado:",porcentaje_devolucion_optimo)

            # Calcular y mostrar la TREA en consola usando el porcentaje óptimo
            trea = self.rumbo._calcular_trea(
                periodo_pago_primas, prima, porcentaje_devolucion_optimo
            )
            # print(f"TREA para el porcentaje óptimo: {trea * 100:.6f}%")

            aporte_total = self.rumbo.calcular_aporte_total(periodo_pago_primas, prima)
            # print(f"Aporte total: {aporte_total:.2f}")

            devolucion_total = self.rumbo.calcular_devolucion_total(
                tasa_frecuencia_seleccionada=parametros_calculados.tasa_frecuencia_seleccionada,
                suma_asegurada=suma_asegurada,
                frecuencia_pago_primas=cotizacion_input.parametros.frecuencia_pago_primas,
                periodo_pago_primas=periodo_pago_primas,
                porcentaje_devolucion_optimo=porcentaje_devolucion_optimo,
            )
            # print(f"Devolución total: {devolucion_total:.2f}")

            ganancia_total = self.rumbo.calcular_ganancia_total(
                aporte_total=aporte_total,
                devolucion_total=devolucion_total,
            )

        # Crear la respuesta base
        respuesta = CotizacionOutput(
            producto=cotizacion_input.producto,
            parametros_entrada=cotizacion_input.parametros,
            parametros_almacenados=parametros_almacenados,
            parametros_calculados=parametros_calculados,
        )

        # Añadir campos específicos según el producto
        if cotizacion_input.producto == TipoProducto.RUMBO:
            parametros_dict = cotizacion_input.parametros.dict()
            parametros_dict.pop("suma_asegurada", None)
            parametros_dict.pop("porcentaje_devolucion", None)
            parametros_dict.pop("moneda", None)
            parametros_dict.pop("frecuencia_pago_primas", None)

            respuesta.parametros_entrada = parametros_dict

            if porcentaje_devolucion_optimo:
                rumbo = {
                    "porcentaje_devolucion": str(
                        round(porcentaje_devolucion_optimo, 2)
                    ),
                    "trea": str(round(trea, 2)),
                    "aporte_total": str(aporte_total),
                    "devolucion_total": str(devolucion_total),
                    "ganancia_total": str(ganancia_total),
                }
                respuesta.rumbo = rumbo
            else:
                # respuesta.porcentaje_devolucion = ""
                rumbo = {
                    "porcentaje_devolucion": "",
                    "trea": "",
                }
        elif cotizacion_input.producto == TipoProducto.ENDOSOS:
            endosos = {"prima": ""}
            respuesta.endosos = endosos

        return respuesta

    def _obtener_parametros_almacenados(
        self, producto: str
    ) -> ParametrosAlmacenadosSchema:
        """Obtiene los parámetros almacenados para un producto específico"""
        parametros_dict = self.parametros_repository.get_parametros_by_producto(
            producto.lower()
        )

        # Extraer valores del diccionario con valores por defecto si no existen
        gasto_adquisicion = parametros_dict.get("gasto_adquisicion", 0.01)
        gasto_mantenimiento = parametros_dict.get("gasto_mantenimiento", 0.01)
        tasa_costo_capital_tir = parametros_dict.get("tasa_costo_capital_tir", 0.01)
        moce = parametros_dict.get("moce", 0.01)
        inflacion_anual = parametros_dict.get("inflacion_anual", 0.01)
        margen_solvencia = parametros_dict.get("margen_solvencia", 0.01)
        fondo_garantia = parametros_dict.get("fondo_garantia", 0.01)
        ajuste_mortalidad = parametros_dict.get("ajuste_mortalidad", 0.01)
        moneda = parametros_dict.get("moneda", "SOLES")
        valor_dolar = parametros_dict.get("valor_dolar", 0.01)
        valor_soles = parametros_dict.get("valor_soles", 0.01)
        tiene_asistencia = parametros_dict.get("tiene_asistencia", False)
        costo_mensual_asistencia_funeraria = parametros_dict.get(
            "costo_mensual_asistencia_funeraria", 0.01
        )
        moneda_poliza = parametros_dict.get("moneda_poliza", 0.01)
        fraccionamiento_primas = parametros_dict.get("fraccionamiento_primas", 0.01)
        comision = parametros_dict.get("comision", 0.01)
        costo_asistencia_funeraria = parametros_dict.get(
            "costo_asistencia_funeraria", 0.01
        )
        impuesto_renta = parametros_dict.get("impuesto_renta", 0.01)
        suma_asegurada_rumbo = parametros_dict.get("suma_asegurada_rumbo", 0.01)

        return ParametrosAlmacenadosSchema(
            gasto_adquisicion=gasto_adquisicion,
            gasto_mantenimiento=gasto_mantenimiento,
            tir=tasa_costo_capital_tir,
            moce=moce,
            inflacion_anual=inflacion_anual,
            margen_solvencia=margen_solvencia,
            fondo_garantia=fondo_garantia,
            ajuste_mortalidad=ajuste_mortalidad,
            moneda=moneda,
            valor_dolar=valor_dolar,
            valor_soles=valor_soles,
            tiene_asistencia=tiene_asistencia,
            costo_mensual_asistencia_funeraria=costo_mensual_asistencia_funeraria,
            moneda_poliza=moneda_poliza,
            fraccionamiento_primas=fraccionamiento_primas,
            comision=comision,
            costo_asistencia_funeraria=costo_asistencia_funeraria,
            impuesto_renta=impuesto_renta,
            suma_asegurada_rumbo=suma_asegurada_rumbo,
        )

    def _convertir_a_esquema(
        self, dominio: ParametrosCalculadosDomain
    ) -> ParametrosCalculadosSchema:
        """Convierte el modelo de dominio a esquema de respuesta"""
        return ParametrosCalculadosSchema(
            adquisicion_fijo_poliza=dominio.adquisicion_fijo_poliza,
            mantenimiento_poliza=dominio.mantenimiento_poliza,
            tasa_costo_capital_mensual=dominio.tir_mensual,
            reserva=dominio.reserva,
            tasa_interes_anual=dominio.tasa_interes_anual,
            tasa_interes_mensual=dominio.tasa_interes_mensual,
            tasa_inversion=dominio.tasa_inversion,
            inflacion_mensual=dominio.inflacion_mensual,
            tasa_costo_capital_mes=dominio.tasa_costo_capital_mes,
            factor_pago=dominio.factor_pago,
            prima_para_redondeo=dominio.prima_para_redondeo,
            tasa_frecuencia_seleccionada=dominio.tasa_frecuencia_seleccionada,
        )
