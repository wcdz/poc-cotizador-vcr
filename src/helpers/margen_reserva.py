def margen_reserva(saldo_reserva: list[float], factor_reserva: float) -> list[float]:
    return [saldo * factor_reserva for saldo in saldo_reserva]
