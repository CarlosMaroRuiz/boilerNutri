"""
Función de fitness agregada que integra todos los objetivos.

Combina múltiples objetivos mediante agregación ponderada
para generar un valor único de aptitud.
"""

from genetic.fitness.nutricion import calcular_discrepancia_nutricional
from genetic.fitness.costo import calcular_costo_total
from genetic.fitness.eficiencia import estimar_eficiencia_alimenticia
from genetic.fitness.disponibilidad import calcular_disponibilidad_local
from genetic.fitness.tiempo import estimar_tiempo_peso_objetivo
from genetic.fitness.restricciones import verificar_restricciones
from conocimiento.requerimientos import obtener_etapa

def calcular_fitness(individuo, config_evaluacion, ingredientes_data, restricciones_usuario=None):
    """
    Calcula el fitness global para un individuo.
    
    Esta función debe ser MINIMIZADA porque:
    - Integra múltiples objetivos que deben ser minimizados
    - Un valor bajo indica mejor calidad global de la solución
    - Facilita la comparación directa entre diferentes formulaciones
    
    Args:
        individuo: Objeto individuo con porcentajes
        config_evaluacion: Diccionario con configuración de evaluación
        ingredientes_data: Lista de datos de ingredientes
        restricciones_usuario: Objeto con restricciones del usuario (opcional)
        
    Returns:
        Valor de fitness global (menor es mejor)
    """
    # Extraer parámetros de configuración
    raza = config_evaluacion.get("raza", "Ross")
    edad_dias = config_evaluacion.get("edad_dias", 35)
    peso_actual = config_evaluacion.get("peso_actual", 1.5)
    peso_objetivo = config_evaluacion.get("peso_objetivo", 2.5)
    pesos = config_evaluacion.get("pesos", {})
    
    # Determinar etapa según edad
    etapa = obtener_etapa(edad_dias)
    
    # Calcular cada componente del fitness
    componentes = {}
    
    # 1. Discrepancia nutricional
    componentes["discrepancia_nutricional"] = calcular_discrepancia_nutricional(
        individuo, etapa, ingredientes_data
    )
    
    # 2. Costo total
    componentes["costo"] = calcular_costo_total(
        individuo, ingredientes_data, restricciones_usuario
    )
    
    # 3. Eficiencia alimenticia
    componentes["eficiencia"] = estimar_eficiencia_alimenticia(
        individuo, raza, edad_dias, ingredientes_data
    )
    
    # 4. Disponibilidad local
    componentes["disponibilidad"] = calcular_disponibilidad_local(
        individuo, ingredientes_data
    )
    
    # 5. Tiempo hasta peso objetivo
    componentes["tiempo"] = estimar_tiempo_peso_objetivo(
        individuo, peso_actual, peso_objetivo, raza, edad_dias, ingredientes_data
    )
    
    # 6. Penalización por restricciones
    componentes["restricciones"] = verificar_restricciones(
        individuo, ingredientes_data, restricciones_usuario
    )
    
    # Normalizar componentes
    componentes_normalizados = normalizar_objetivos(componentes)
    
    # Aplicar ponderaciones
    fitness = calcular_fitness_ponderado(componentes_normalizados, pesos)
    
    # Almacenar en el individuo
    individuo.fitness = fitness
    
    return fitness

def normalizar_objetivos(componentes):
    """
    Normaliza los valores de los objetivos para agregación
    
    Args:
        componentes: Diccionario con valores de cada objetivo
        
    Returns:
        Diccionario con valores normalizados
    """
    normalizados = {}
    
    # Factores de normalización basados en rangos esperados
    factores_normalizacion = {
        "discrepancia_nutricional": 1.0,  # Ya está en rango 0-1
        "costo": 15.0,  # Rango esperado 0-15 $/kg
        "eficiencia": 2.5,  # Conversión alimenticia 1.0-2.5
        "disponibilidad": 1.0,  # Ya está en rango 0-1
        "tiempo": 100.0,  # Días hasta peso objetivo 0-100
        "restricciones": 100.0  # Penalizaciones 0-100+
    }
    
    for objetivo, valor in componentes.items():
        factor = factores_normalizacion.get(objetivo, 1.0)
        normalizados[objetivo] = min(1.0, valor / factor)
    
    return normalizados

def calcular_fitness_ponderado(componentes_normalizados, pesos_personalizados=None):
    """
    Calcula el fitness aplicando ponderaciones a los objetivos
    
    Args:
        componentes_normalizados: Diccionario con componentes normalizados
        pesos_personalizados: Diccionario con pesos personalizados (opcional)
        
    Returns:
        Valor de fitness ponderado
    """
    # Pesos por defecto
    pesos_default = {
        "discrepancia_nutricional": 0.35,  # 35% - Más importante
        "costo": 0.30,                     # 30% - Muy importante
        "eficiencia": 0.15,                # 15% - Importante
        "disponibilidad": 0.10,            # 10% - Moderadamente importante
        "tiempo": 0.10,                    # 10% - Moderadamente importante
        "restricciones": 1.0               # Peso completo para penalizaciones
    }
    
    # Usar pesos personalizados si se proporcionan
    if pesos_personalizados:
        pesos = {**pesos_default, **pesos_personalizados}
    else:
        pesos = pesos_default
    
    # Calcular fitness ponderado
    fitness = 0
    
    # Objetivos principales (se suman ponderadamente)
    objetivos_principales = ["discrepancia_nutricional", "costo", "eficiencia", 
                           "disponibilidad", "tiempo"]
    
    for objetivo in objetivos_principales:
        if objetivo in componentes_normalizados:
            valor_normalizado = componentes_normalizados[objetivo]
            peso = pesos.get(objetivo, 0)
            fitness += peso * valor_normalizado
    
    # Restricciones (se suman con peso completo)
    if "restricciones" in componentes_normalizados:
        fitness += componentes_normalizados["restricciones"]
    
    return fitness

def calcular_fitness_adaptativo(individuo, config_evaluacion, ingredientes_data, 
                               fase_algoritmo="inicial", restricciones_usuario=None):
    """
    Calcula fitness con pesos adaptativos según la fase del algoritmo
    
    Args:
        individuo: Objeto individuo con porcentajes
        config_evaluacion: Diccionario con configuración de evaluación
        ingredientes_data: Lista de datos de ingredientes
        fase_algoritmo: Fase actual ("inicial", "intermedia", "final")
        restricciones_usuario: Objeto con restricciones del usuario (opcional)
        
    Returns:
        Valor de fitness adaptativo
    """
    # Pesos según la fase del algoritmo
    pesos_por_fase = {
        "inicial": {
            "discrepancia_nutricional": 0.40,  # Mayor peso en nutrición
            "costo": 0.25,
            "eficiencia": 0.15,
            "disponibilidad": 0.10,
            "tiempo": 0.10
        },
        "intermedia": {
            "discrepancia_nutricional": 0.35,
            "costo": 0.30,                     # Aumenta peso del costo
            "eficiencia": 0.15,
            "disponibilidad": 0.10,
            "tiempo": 0.10
        },
        "final": {
            "discrepancia_nutricional": 0.30,
            "costo": 0.35,                     # Mayor peso en costo
            "eficiencia": 0.20,                # Mayor peso en eficiencia
            "disponibilidad": 0.10,
            "tiempo": 0.05
        }
    }
    
    pesos = pesos_por_fase.get(fase_algoritmo, pesos_por_fase["inicial"])
    config_evaluacion["pesos"] = pesos
    
    return calcular_fitness(individuo, config_evaluacion, ingredientes_data, restricciones_usuario)

def evaluar_poblacion(poblacion, config_evaluacion, ingredientes_data, 
                     fase_algoritmo="inicial", restricciones_usuario=None):
    """
    Evalúa toda una población calculando el fitness de cada individuo
    
    Args:
        poblacion: Lista de individuos
        config_evaluacion: Diccionario con configuración de evaluación
        ingredientes_data: Lista de datos de ingredientes
        fase_algoritmo: Fase actual del algoritmo
        restricciones_usuario: Objeto con restricciones del usuario (opcional)
        
    Returns:
        Lista de individuos evaluados
    """
    for individuo in poblacion:
        calcular_fitness_adaptativo(individuo, config_evaluacion, ingredientes_data, 
                                   fase_algoritmo, restricciones_usuario)
    
    return poblacion

def comparar_individuos(individuo1, individuo2, criterio="fitness"):
    """
    Compara dos individuos según diferentes criterios
    
    Args:
        individuo1: Primer individuo
        individuo2: Segundo individuo
        criterio: Criterio de comparación ("fitness", "costo", "nutricion", etc.)
        
    Returns:
        -1 si individuo1 es mejor, 1 si individuo2 es mejor, 0 si son iguales
    """
    if criterio == "fitness":
        if individuo1.fitness < individuo2.fitness:
            return -1
        elif individuo1.fitness > individuo2.fitness:
            return 1
        else:
            return 0
    
    elif criterio == "costo":
        if individuo1.costo_total < individuo2.costo_total:
            return -1
        elif individuo1.costo_total > individuo2.costo_total:
            return 1
        else:
            return 0
    
    elif criterio == "tiempo":
        if hasattr(individuo1, 'dias_peso_objetivo') and hasattr(individuo2, 'dias_peso_objetivo'):
            if individuo1.dias_peso_objetivo < individuo2.dias_peso_objetivo:
                return -1
            elif individuo1.dias_peso_objetivo > individuo2.dias_peso_objetivo:
                return 1
        return 0
    
    else:
        return 0  # Criterio no reconocido

def generar_ranking_multiobjetivo(poblacion, criterios=None):
    """
    Genera un ranking considerando múltiples objetivos
    
    Args:
        poblacion: Lista de individuos
        criterios: Lista de criterios a considerar
        
    Returns:
        Lista ordenada de individuos con rankings
    """
    if criterios is None:
        criterios = ["fitness", "costo", "tiempo"]
    
    ranking = []
    
    for individuo in poblacion:
        scores = {}
        scores["fitness"] = individuo.fitness
        scores["costo"] = individuo.costo_total
        
        if hasattr(individuo, 'dias_peso_objetivo'):
            scores["tiempo"] = individuo.dias_peso_objetivo
        
        if hasattr(individuo, 'conversion_alimenticia'):
            scores["eficiencia"] = individuo.conversion_alimenticia
        
        ranking.append({
            "individuo": individuo,
            "scores": scores
        })
    
    # Ordenar por fitness principal
    ranking.sort(key=lambda x: x["individuo"].fitness)
    
    return ranking

def calcular_metricas_poblacion(poblacion):
    """
    Calcula métricas estadísticas de una población
    
    Args:
        poblacion: Lista de individuos
        
    Returns:
        Diccionario con métricas estadísticas
    """
    if not poblacion:
        return {}
    
    fitness_values = [ind.fitness for ind in poblacion]
    costo_values = [ind.costo_total for ind in poblacion if hasattr(ind, 'costo_total')]
    
    metricas = {
        "fitness": {
            "mejor": min(fitness_values),
            "peor": max(fitness_values),
            "promedio": sum(fitness_values) / len(fitness_values),
            "mediana": sorted(fitness_values)[len(fitness_values) // 2]
        }
    }
    
    if costo_values:
        metricas["costo"] = {
            "mejor": min(costo_values),
            "peor": max(costo_values),
            "promedio": sum(costo_values) / len(costo_values)
        }
    
    # Calcular diversidad (desviación estándar del fitness)
    promedio_fitness = metricas["fitness"]["promedio"]
    varianza = sum((f - promedio_fitness) ** 2 for f in fitness_values) / len(fitness_values)
    metricas["diversidad"] = varianza ** 0.5
    
    return metricas

def detectar_convergencia(historico_fitness, ventana=20, tolerancia=1e-6):
    """
    Detecta si el algoritmo ha convergido
    
    Args:
        historico_fitness: Lista con el mejor fitness por generación
        ventana: Número de generaciones a considerar
        tolerancia: Tolerancia para considerar convergencia
        
    Returns:
        True si ha convergido, False en caso contrario
    """
    if len(historico_fitness) < ventana:
        return False
    
    # Obtener últimas 'ventana' generaciones
    ultimas_generaciones = historico_fitness[-ventana:]
    
    # Verificar si la mejora es menor que la tolerancia
    mejora = ultimas_generaciones[0] - ultimas_generaciones[-1]
    
    return mejora < tolerancia