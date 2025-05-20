from src.models.schemas.cotizador import (
    CotizacionInput, 
    CotizacionOutput,
    ParametrosAlmacenados,
    ParametrosCalculados,
    TipoProducto
)


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
            parametros_calculados=parametros_calculados
        )
        
        # Añadir campos específicos según el producto
        if cotizacion_input.producto == TipoProducto.RUMBO:
            respuesta.porcentaje_devolucion = ""
        elif cotizacion_input.producto == TipoProducto.ENDOSOS:
            respuesta.prima = ""
        
        return respuesta
    
    def _obtener_parametros_almacenados(self) -> ParametrosAlmacenados:
        """Obtiene los parámetros almacenados comunes para todos los productos"""
        return ParametrosAlmacenados(
            gastos_adquisicion=0.01,
            gastos_mantenimiento=0.01,
            tir=0.01,
            moce=0.01,
            inflacion_anual=0.01,
            margen_solvencia=0.01,
            fondo_garantia=0.01
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
            tasa_reserva=0.01
        )
    
    # En el futuro, podrías tener métodos específicos para cada producto:
    # def _calcular_rumbo(self, parametros)
    # def _calcular_endosos(self, parametros) 