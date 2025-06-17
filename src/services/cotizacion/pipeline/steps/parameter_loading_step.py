from .base_step import PipelineStep
from ..cotizacion_context import CotizacionContext
from src.repositories.parametros_repository import JsonParametrosRepository
from src.repositories.tasa_interes_repository import JsonTasaInteresRepository
from src.repositories.factores_pago_repository import JsonFactoresPagoRepository
from src.models.domain.parametros_calculados import ParametrosCalculados as ParametrosCalculadosDomain
from src.models.schemas.cotizacion_schema import TipoProducto


class ParameterLoadingStep(PipelineStep):
    """Paso de carga de parámetros almacenados y calculados"""
    
    def __init__(self):
        super().__init__("ParameterLoading")
        self.parametros_repository = JsonParametrosRepository()
        self.tasa_interes_repository = JsonTasaInteresRepository()
        self.factores_pago_repository = JsonFactoresPagoRepository()
    
    def process(self, context: CotizacionContext) -> CotizacionContext:
        """Carga todos los parámetros necesarios para el cálculo"""
        
        # Obtener parámetros almacenados
        context.parametros_almacenados = self._obtener_parametros_almacenados(
            context.input.producto.value
        )
        
        # Obtener tasas de interés
        context.tasas_interes_data = self.tasa_interes_repository.get_tasas_interes()
        
        # Obtener factores de pago
        context.factores_pago = self.factores_pago_repository.get_factores_pago()
        
        # Extraer prima según el producto
        if context.input.producto == TipoProducto.RUMBO:
            context.prima = context.input.parametros.prima
            context.suma_asegurada = context.parametros_almacenados.suma_asegurada_rumbo
        
        # Crear parámetros calculados de dominio
        parametros_dominio = ParametrosCalculadosDomain(
            prima=context.prima,
            gasto_adquisicion=context.parametros_almacenados.gasto_adquisicion,
            gasto_mantenimiento=context.parametros_almacenados.gasto_mantenimiento,
            tasa_costo_capital_tir=context.parametros_almacenados.tir,
            moce=context.parametros_almacenados.moce,
            inflacion_anual=context.parametros_almacenados.inflacion_anual,
            margen_solvencia=context.parametros_almacenados.margen_solvencia,
            fondo_garantia=context.parametros_almacenados.fondo_garantia,
            periodo_vigencia=context.periodo_vigencia,
            tasas_interes_data=context.tasas_interes_data,
            periodo_pago_primas=context.periodo_pago_primas,
            frecuencia_pago_primas=context.input.parametros.frecuencia_pago_primas,
            factores_pago=context.factores_pago,
            suma_asegurada=context.suma_asegurada,
        )
        
        # Convertir a esquema de respuesta
        context.parametros_calculados = self._convertir_a_esquema(parametros_dominio)
        
        return context
    
    def _obtener_parametros_almacenados(self, producto: str):
        """Obtiene los parámetros almacenados para un producto específico"""
        from src.models.schemas.cotizacion_schema import ParametrosAlmacenados
        
        parametros_dict = self.parametros_repository.get_parametros_by_producto(
            producto.lower()
        )
        
        return ParametrosAlmacenados(
            gasto_adquisicion=parametros_dict.get("gasto_adquisicion", 0.01),
            gasto_mantenimiento=parametros_dict.get("gasto_mantenimiento", 0.01),
            tir=parametros_dict.get("tasa_costo_capital_tir", 0.01),
            moce=parametros_dict.get("moce", 0.01),
            inflacion_anual=parametros_dict.get("inflacion_anual", 0.01),
            margen_solvencia=parametros_dict.get("margen_solvencia", 0.01),
            fondo_garantia=parametros_dict.get("fondo_garantia", 0.01),
            ajuste_mortalidad=parametros_dict.get("ajuste_mortalidad", 0.01),
            moneda=parametros_dict.get("moneda", "SOLES"),
            valor_dolar=parametros_dict.get("valor_dolar", 0.01),
            valor_soles=parametros_dict.get("valor_soles", 0.01),
            tiene_asistencia=parametros_dict.get("tiene_asistencia", False),
            costo_mensual_asistencia_funeraria=parametros_dict.get("costo_mensual_asistencia_funeraria", 0.01),
            moneda_poliza=parametros_dict.get("moneda_poliza", 0.01),
            fraccionamiento_primas=parametros_dict.get("fraccionamiento_primas", 0.01),
            comision=parametros_dict.get("comision", 0.01),
            costo_asistencia_funeraria=parametros_dict.get("costo_asistencia_funeraria", 0.01),
            impuesto_renta=parametros_dict.get("impuesto_renta", 0.01),
            suma_asegurada_rumbo=parametros_dict.get("suma_asegurada_rumbo", 0.01),
        )
    
    def _convertir_a_esquema(self, dominio: ParametrosCalculadosDomain):
        """Convierte el modelo de dominio a esquema de respuesta"""
        from src.models.schemas.cotizacion_schema import ParametrosCalculados
        
        return ParametrosCalculados(
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