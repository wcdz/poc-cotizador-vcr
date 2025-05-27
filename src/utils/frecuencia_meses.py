from src.core.constans import ANUAL, SEMESTRAL, TRIMESTRAL, MENSUAL


def frecuencia_meses(frecuencia_pago_primas) -> int:
    """Obtiene la cantidad de meses según la frecuencia de pago"""
    meses_por_frecuencia = {
        "ANUAL": ANUAL,
        "SEMESTRAL": SEMESTRAL,
        "TRIMESTRAL": TRIMESTRAL,
        "MENSUAL": MENSUAL,
    }
    return meses_por_frecuencia.get(frecuencia_pago_primas, 12)
