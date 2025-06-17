from src.core.constants import FACTOR_RESERVA


def tasa_interes_reserva(tasas_interes: dict) -> float:
    """Se agregar el atributo tasa_reserva a cada periodo de la tabla de tasas de interés"""
    tasa_reserva = 0
    for key, value in tasas_interes.items():
        tasa_reserva = float(value["tasa_inversion"]) - FACTOR_RESERVA
        tasas_interes[key]["tasa_reserva"] = tasa_reserva
    return tasas_interes
