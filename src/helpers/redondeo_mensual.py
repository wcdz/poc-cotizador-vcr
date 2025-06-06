def redondeo_mensual(tasa_inversion: float) -> float:
    return ((1 + tasa_inversion) ** (1 / 12)) - 1
