"""
Configuración global del proyecto boilerNutri.

Contiene parámetros del algoritmo genético, ponderaciones de objetivos,
y otras configuraciones del sistema.
"""

# Configuración del Algoritmo Genético
ALGORITMO_CONFIG = {
    "tamano_poblacion": 100,
    "num_generaciones": 200,
    "prob_cruza": 0.8,
    "prob_mutacion": 0.2,
    "intensidad_mutacion": 0.1,
    "tamano_torneo": 3,
    "elitismo": 5
}

# Ponderaciones de la función de fitness multiobjetivo
PESOS_FITNESS = {
    "discrepancia_nutricional": 0.40,
    "costo": 0.35,
    "eficiencia": 0.15,
    "disponibilidad": 0.10
}

# Configuración de fases del algoritmo
FASES_CONFIG = {
    "inicial": {"inicio": 0, "fin": 0.3, "alpha_blx": 0.7},
    "intermedia": {"inicio": 0.3, "fin": 0.7},
    "final": {"inicio": 0.7, "fin": 1.0}
}

# Constantes del sistema
PRECISION_PORCENTAJES = 1e-6
PENALIZACION_RESTRICCIONES = 1000
