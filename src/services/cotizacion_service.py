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


class CotizadorService:
    """Servicio unificado para cotizaciones de distintos productos"""

    def __init__(self):
        self.parametros_repository = JsonParametrosRepository()

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

        # Extraer la prima del esquema de entrada si es RUMBO
        prima = 0.0
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
        )

        # Convertir el modelo de dominio a esquema de respuesta
        parametros_calculados = self._convertir_a_esquema(parametros_dominio)

        # Crear la respuesta base
        respuesta = CotizacionOutput(
            producto=cotizacion_input.producto,
            parametros_entrada=cotizacion_input.parametros,
            parametros_almacenados=parametros_almacenados,
            parametros_calculados=parametros_calculados,
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

        return ParametrosAlmacenadosSchema(
            gasto_adquisicion=gasto_adquisicion,
            gasto_mantenimiento=gasto_mantenimiento,
            tir=tasa_costo_capital_tir,
            moce=moce,
            inflacion_anual=inflacion_anual,
            margen_solvencia=margen_solvencia,
            fondo_garantia=fondo_garantia,
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
            tasa_reserva=dominio.tasa_reserva,
            inflacion_mensual=dominio.inflacion_mensual,
        )

    # En el futuro, podrías tener métodos específicos para cada producto:
    # def _calcular_rumbo(self, parametros)
    # def _calcular_endosos(self, parametros)
