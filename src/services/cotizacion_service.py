from src.models.schemas.cotizacion_schema import (
    CotizacionInput,
    CotizacionOutput,
    ParametrosAlmacenados,
    ParametrosCalculados,
    TipoProducto,
)

from src.repositories.parametros_repository import JsonParametrosRepository


class CotizadorService:
    """Servicio unificado para cotizaciones de distintos productos"""

    def __init__(self):
        # Aquí podrías cargar parámetros desde una base de datos o archivo de configuración
        pass

    def cotizar(self, cotizacion_input: CotizacionInput) -> CotizacionOutput:
        """
        Realiza la cotización para el producto especificado
        Determina qué lógica de cotización aplicar según el tipo de producto
        """
        # Validar que los parámetros correspondan al producto
        cotizacion_input.validate_product_parameters()

        # Obtener parámetros almacenados (valores fijos por ahora)
        parametros_almacenados = self._obtener_parametros_almacenados()

        # Obtener parámetros calculados según el producto
        parametros_calculados = self._calcular_parametros()

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

    def _obtener_parametros_almacenados(self) -> ParametrosAlmacenados:
        """Obtiene los parámetros almacenados comunes para todos los productos"""
        parametros_repository = JsonParametrosRepository()
        parametros_almacenados = parametros_repository.get_parametros_by_producto(
            "rumbo"
        )
        (
            gasto_adquisicion,
            gasto_mantenimiento,
            tasa_costo_capital_tir,
            moce,
            inflacion_anual,
            margen_solvencia,
            fondo_garantia,
        ) = (
            parametros_almacenados["gasto_adquisicion"],
            parametros_almacenados["gasto_mantenimiento"],
            parametros_almacenados["tasa_costo_capital_tir"],
            parametros_almacenados["moce"],
            parametros_almacenados["inflacion_anual"],
            parametros_almacenados["margen_solvencia"],
            parametros_almacenados["fondo_garantia"],
        )

        print(gasto_adquisicion)
        return ParametrosAlmacenados(
            gasto_adquisicion=gasto_adquisicion,
            gasto_mantenimiento=gasto_mantenimiento,
            tir=tasa_costo_capital_tir,
            moce=moce,
            inflacion_anual=inflacion_anual,
            margen_solvencia=margen_solvencia,
            fondo_garantia=fondo_garantia,
        )

    def _calcular_parametros(self) -> ParametrosCalculados:
        """Calcula los parámetros comunes para todos los productos"""
        return ParametrosCalculados(
            adquisicion_fijo_poliza=0.01,
            mantenimiento_poliza=0.01,
            tir_mensual=0.01,
            reserva=0.01,
            tasa_interes_anual=0.01,
            tasa_interes_mensual=0.01,
            tasa_inversion=0.01,
            tasa_reserva=0.01,
        )

    # En el futuro, podrías tener métodos específicos para cada producto:
    # def _calcular_rumbo(self, parametros)
    # def _calcular_endosos(self, parametros)
