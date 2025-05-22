def caducidad_mensual(periodo_vigencia, valores_duros, porcentajes_anuales):
    resultados = {}
    total_meses = periodo_vigencia * 12

    for mes_global in range(1, total_meses + 1):
        anio = (mes_global - 1) // 12 + 1
        mes = (mes_global - 1) % 12 + 1

        if mes_global == total_meses:
            valor = 1.0  # Último mes de todos
        elif str(anio) in valores_duros and str(mes) in valores_duros[str(anio)]:
            valor = round(valores_duros[str(anio)][str(mes)] / 100, 8)
        else:
            r_anual = porcentajes_anuales.get(str(anio), 10) / 100
            valor = round(1 - (1 - r_anual) ** (1 / 12), 8)

        resultados[mes_global] = valor

    return resultados
