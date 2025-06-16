def calcular_trea(periodo_pago_primas, prima, porcentaje_devolucion):
    """
    Calcula la TREA según la fórmula de Excel:
    =(1+TASA(C8*12;C22;0;-(C22*C8*C11*12);1))^(12)-1
    Donde:
    C8 = periodo de pago de primas (años)
    C22 = prima
    C11 = porcentaje de devolución (en porcentaje, ej: 125.32 para 125.32%)
    """
    nper = periodo_pago_primas * 12
    pmt = prima
    pv = 0
    fv = -(prima * periodo_pago_primas * 12 * (porcentaje_devolucion / 100))
    tipo = 1  # pagos al inicio

    def funcion_tasa(r):
        if r == 0:
            return pmt * nper + pv + fv
        return (
            pmt * (1 + r * tipo) * (1 - (1 + r) ** -nper) / r
            + pv
            + fv / ((1 + r) ** nper)
        )

    def derivada_f(r, h=1e-6):
        return (funcion_tasa(r + h) - funcion_tasa(r - h)) / (2 * h)

    def newton_raphson(f, f_prime, x0, tol=1e-7, max_iter=100):
        x = x0
        for _ in range(max_iter):
            fx = f(x)
            dfx = f_prime(x)
            if dfx == 0:
                raise Exception("Derivada cero")
            x_new = x - fx / dfx
            if abs(x_new - x) < tol:
                return x_new
            x = x_new
        raise Exception("No converge")

    tasa_mensual = newton_raphson(funcion_tasa, derivada_f, 0.01)
    trea = ((1 + tasa_mensual) ** 12 - 1) * 100
    return trea
