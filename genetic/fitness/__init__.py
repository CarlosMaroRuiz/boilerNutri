"""
Paquete de funciones de evaluación de aptitud (fitness).

Contiene todas las funciones objetivo y la función de fitness agregada
para el problema multiobjetivo de formulación de alimentos.
"""

from .agregacion import calcular_fitness
from .nutricion import calcular_discrepancia_nutricional
from .costo import calcular_costo_total
from .eficiencia import estimar_eficiencia_alimenticia
from .disponibilidad import calcular_disponibilidad_local
from .tiempo import estimar_tiempo_peso_objetivo
from .restricciones import verificar_restricciones

__all__ = [
    'calcular_fitness',
    'calcular_discrepancia_nutricional',
    'calcular_costo_total',
    'estimar_eficiencia_alimenticia',
    'calcular_disponibilidad_local',
    'estimar_tiempo_peso_objetivo',
    'verificar_restricciones'
]
