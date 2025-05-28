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
from src.services.expuestos_mes_service import ExpuestosMesService
from src.services.gastos_service import GastosService


class CotizadorService:
    """Servicio unificado para cotizaciones de distintos productos"""

    def __init__(self):
        self.parametros_repository = JsonParametrosRepository()
        self.tasa_interes_repository = JsonTasaInteresRepository()
        self.expuestos_mes = ExpuestosMesService()
        self.gastos_service = GastosService()

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

        # Extraer la prima del esquema de entrada si es RUMBO
        prima = 0.0
        periodo_vigencia = cotizacion_input.parametros.periodo_vigencia
        periodo_pago_primas = cotizacion_input.parametros.periodo_pago_primas
        if cotizacion_input.producto == TipoProducto.RUMBO:
            prima = cotizacion_input.parametros.prima

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
        )

        # Convertir el modelo de dominio a esquema de respuesta
        parametros_calculados = self._convertir_a_esquema(parametros_dominio)

        expuestos_mes = self.expuestos_mes.calcular_expuestos_mes(
            edad_actuarial=cotizacion_input.parametros.edad_actuarial,
            sexo=cotizacion_input.parametros.sexo,
            fumador=cotizacion_input.parametros.fumador,
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

        # Crear la respuesta base
        respuesta = CotizacionOutput(
            producto=cotizacion_input.producto,
            parametros_entrada=cotizacion_input.parametros,
            parametros_almacenados=parametros_almacenados,
            parametros_calculados=parametros_calculados,
            expuestos_mes=expuestos_mes,
            gastos=gastos,
        )

        # Añadir campos específicos según el producto
        if cotizacion_input.producto == TipoProducto.RUMBO:
            respuesta.porcentaje_devolucion = ""
        elif cotizacion_input.producto == TipoProducto.ENDOSOS:
            respuesta.prima = ""

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
        )

    def _convertir_a_esquema(
        self, dominio: ParametrosCalculadosDomain
    ) -> ParametrosCalculadosSchema:
        """Convierte el modelo de dominio a esquema de respuesta"""
        return ParametrosCalculadosSchema(
            adquisicion_fijo_poliza=dominio.adquisicion_fijo_poliza,
            mantenimiento_poliza=dominio.mantenimiento_poliza,
            tir_mensual=dominio.tir_mensual,
            reserva=dominio.reserva,
            tasa_interes_anual=dominio.tasa_interes_anual,
            tasa_interes_mensual=dominio.tasa_interes_mensual,
            tasa_inversion=dominio.tasa_inversion,
            inflacion_mensual=dominio.inflacion_mensual,
        )

    # En el futuro, podrías tener métodos específicos para cada producto:
    # def _calcular_rumbo(self, parametros)
    # def _calcular_endosos(self, parametros)
