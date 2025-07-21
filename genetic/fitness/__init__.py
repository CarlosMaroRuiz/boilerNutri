"""
Paquete de funciones de evaluación de aptitud (fitness).

Contiene todas las funciones objetivo y la función de fitness agregada
para el problema multiobjetivo de formulación de alimentos.
"""

from .agregacion import calcular_fitness, calcular_fitness_adaptativo, evaluar_poblacion
from .nutricion import calcular_discrepancia_nutricional, calcular_propiedades_nutricionales
from .costo import calcular_costo_total, seleccionar_proveedor_optimo
from .eficiencia import estimar_eficiencia_alimenticia, obtener_conversion_base
from .disponibilidad import calcular_disponibilidad_local, evaluar_disponibilidad_ingrediente
from .tiempo import estimar_tiempo_peso_objetivo, calcular_ganancia_diaria
from .restricciones import verificar_restricciones, es_formulacion_factible

__all__ = [
    # Función principal de fitness
    'calcular_fitness',
    'calcular_fitness_adaptativo',
    'evaluar_poblacion',
    
    # Objetivos individuales
    'calcular_discrepancia_nutricional',
    'calcular_propiedades_nutricionales',
    'calcular_costo_total',
    'seleccionar_proveedor_optimo',
    'estimar_eficiencia_alimenticia',
    'obtener_conversion_base',
    'calcular_disponibilidad_local',
    'evaluar_disponibilidad_ingrediente',
    'estimar_tiempo_peso_objetivo',
    'calcular_ganancia_diaria',
    
    # Restricciones
    'verificar_restricciones',
    'es_formulacion_factible'
]

# Información sobre los objetivos
OBJETIVOS_INFO = {
    "discrepancia_nutricional": {
        "descripcion": "Mide qué tan cerca está la formulación de los requerimientos nutricionales",
        "tipo": "minimizar",
        "peso_default": 0.35,
        "rango_esperado": (0, 1)
    },
    "costo": {
        "descripcion": "Costo total por kilogramo de la formulación",
        "tipo": "minimizar", 
        "peso_default": 0.30,
        "rango_esperado": (5, 15)
    },
    "eficiencia": {
        "descripcion": "Conversión alimenticia estimada (kg alimento/kg ganancia)",
        "tipo": "minimizar",
        "peso_default": 0.15,
        "rango_esperado": (1.0, 2.5)
    },
    "disponibilidad": {
        "descripcion": "Dificultad para obtener ingredientes localmente",
        "tipo": "minimizar",
        "peso_default": 0.10,
        "rango_esperado": (0, 1)
    },
    "tiempo": {
        "descripcion": "Días estimados hasta alcanzar peso objetivo",
        "tipo": "minimizar", 
        "peso_default": 0.10,
        "rango_esperado": (20, 80)
    }
}

def obtener_info_objetivos():
    """
    Obtiene información sobre todos los objetivos del sistema
    
    Returns:
        Diccionario con información de objetivos
    """
    return OBJETIVOS_INFO.copy()

def validar_pesos_fitness(pesos):
    """
    Valida que los pesos de fitness sean correctos
    
    Args:
        pesos: Diccionario con pesos para cada objetivo
        
    Returns:
        True si los pesos son válidos, False en caso contrario
    """
    objetivos_validos = set(OBJETIVOS_INFO.keys())
    objetivos_proporcionados = set(pesos.keys())
    
    # Verificar que solo se proporcionen objetivos válidos
    if not objetivos_proporcionados.issubset(objetivos_validos):
        return False
    
    # Verificar que los pesos sean números positivos
    for peso in pesos.values():
        if not isinstance(peso, (int, float)) or peso < 0:
            return False
    
    # Verificar que la suma de pesos sea aproximadamente 1 (excluyendo restricciones)
    suma_pesos = sum(pesos.values())
    if abs(suma_pesos - 1.0) > 0.1:  # Tolerancia del 10%
        return False
    
    return True