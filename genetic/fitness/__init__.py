# Importaciones principales (solo las que se usan externamente)
from .agregacion import calcular_fitness, evaluar_poblacion

# Importaciones individuales solo si se necesitan por separado
from .nutricion import calcular_discrepancia_nutricional, calcular_propiedades_nutricionales
from .costo import calcular_costo_total, seleccionar_proveedor_optimo
from .eficiencia import estimar_eficiencia_alimenticia, obtener_conversion_base
from .disponibilidad import calcular_disponibilidad_local, evaluar_disponibilidad_ingrediente
from .tiempo import estimar_tiempo_peso_objetivo, calcular_ganancia_diaria
from .restricciones import verificar_restricciones, es_formulacion_factible

__all__ = [
    # Funciones principales (las más usadas)
    'calcular_fitness',
    'evaluar_poblacion',
    
    # Configuración de objetivos
    'OBJETIVOS',
    'obtener_pesos_default',
    'validar_pesos',
    
    # Funciones individuales (para uso específico)
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
    'verificar_restricciones',
    'es_formulacion_factible'
]