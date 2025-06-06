from dataclasses import dataclass


@dataclass
class MargenSolvencia:
    """Modelo de dominio para el margen de solvencia"""

    # Definicion de atributos

    def calcular_margen_solvencia(
        self, reserva_fin_año: list[float], margen_solvencia_reserva: float
    ):
        return [reserva * margen_solvencia_reserva for reserva in reserva_fin_año]

    def calcular_varianza_margen_solvencia(
        self, margen_solvencia: list[float]
    ) -> list[float]:
        # variable_margen_solvencia.append(-margen_solvencia[-1])
        return [margen_solvencia[0]] + [
            actual - anterior
            for anterior, actual in zip(margen_solvencia, margen_solvencia[1:])
        ]
