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
    
    # 1. Discrepancia nutricional (PRIORIDAD ALTA)
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
    
    # Normalizar componentes (MEJORADO)
    componentes_normalizados = normalizar_objetivos_mejorado(componentes)
    
    # Aplicar ponderaciones
    fitness = calcular_fitness_ponderado(componentes_normalizados, pesos)
    
    # Almacenar en el individuo
    individuo.fitness = fitness
    
    return fitness

def normalizar_objetivos_mejorado(componentes):
    """
    Normaliza los valores de los objetivos con factores mejorados
    
    Args:
        componentes: Diccionario con valores de cada objetivo
        
    Returns:
        Diccionario con valores normalizados
    """
    normalizados = {}
    
    # Factores de normalización CORREGIDOS basados en rangos reales
    factores_normalizacion = {
        "discrepancia_nutricional": 2.0,  # Era 1.0 → Más sensible a discrepancias
        "costo": 12.0,  # Era 15.0 → Ajustado al rango real $8-12/kg
        "eficiencia": 2.2,  # Era 2.5 → Conversión alimenticia real 1.5-2.2
        "disponibilidad": 1.0,  # Mantener en rango 0-1
        "tiempo": 60.0,  # Era 100.0 → Días hasta peso objetivo más realista
        "restricciones": 50.0  # Era 100.0 → Penalizaciones más moderadas
    }
    
    for objetivo, valor in componentes.items():
        factor = factores_normalizacion.get(objetivo, 1.0)
        # Aplicar normalización con límite superior más estricto
        normalizados[objetivo] = min(1.5, valor / factor)  # Era min(1.0, ...)
    
    return normalizados

def calcular_fitness_ponderado(componentes_normalizados, pesos_personalizados=None):
    """
    Calcula el fitness aplicando ponderaciones MEJORADAS a los objetivos
    
    Args:
        componentes_normalizados: Diccionario con componentes normalizados
        pesos_personalizados: Diccionario con pesos personalizados (opcional)
        
    Returns:
        Valor de fitness ponderado
    """
    # Pesos por defecto REBALANCEADOS (nutrición prioritaria)
    pesos_default = {
        "discrepancia_nutricional": 0.50,  # ERA 0.35 → AUMENTADO: Nutrición es crítica
        "costo": 0.25,                     # ERA 0.30 → REDUCIDO: Menos peso al costo
        "eficiencia": 0.15,                # MANTENER: Eficiencia importante
        "disponibilidad": 0.05,            # ERA 0.10 → REDUCIDO: Menos crítico
        "tiempo": 0.05,                    # ERA 0.10 → REDUCIDO: Menos crítico
        "restricciones": 2.0               # ERA 1.0 → AUMENTADO: Penalizar más violaciones
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
            
            # APLICAR PENALIZACIÓN CUADRÁTICA PARA DISCREPANCIA NUTRICIONAL
            if objetivo == "discrepancia_nutricional" and valor_normalizado > 0.3:
                # Penalización extra para discrepancias altas
                valor_normalizado = valor_normalizado * (1 + valor_normalizado)
            
            fitness += peso * valor_normalizado
    
    # Restricciones (se multiplican por factor alto)
    if "restricciones" in componentes_normalizados:
        peso_restricciones = pesos.get("restricciones", 2.0)
        fitness += peso_restricciones * componentes_normalizados["restricciones"]
    
    return fitness

def calcular_fitness_adaptativo(individuo, config_evaluacion, ingredientes_data, 
                               fase_algoritmo="inicial", restricciones_usuario=None):
    """
    Calcula fitness con pesos adaptativos MEJORADOS según la fase del algoritmo
    
    Args:
        individuo: Objeto individuo con porcentajes
        config_evaluacion: Diccionario con configuración de evaluación
        ingredientes_data: Lista de datos de ingredientes
        fase_algoritmo: Fase actual ("inicial", "intermedia", "final")
        restricciones_usuario: Objeto con restricciones del usuario (opcional)
        
    Returns:
        Valor de fitness adaptativo
    """
    # Pesos MEJORADOS según la fase del algoritmo (nutrición siempre prioritaria)
    pesos_por_fase = {
        "inicial": {
            "discrepancia_nutricional": 0.55,  # ERA 0.40 → MÁS PESO a nutrición
            "costo": 0.20,                     # ERA 0.25 → MENOS peso al costo
            "eficiencia": 0.15,
            "disponibilidad": 0.05,
            "tiempo": 0.05
        },
        "intermedia": {
            "discrepancia_nutricional": 0.50,  # MANTENER alta prioridad nutricional
            "costo": 0.25,                     # ERA 0.30 → Aumenta pero controlado
            "eficiencia": 0.15,
            "disponibilidad": 0.05,
            "tiempo": 0.05
        },
        "final": {
            "discrepancia_nutricional": 0.45,  # ERA 0.30 → MANTENER prioritario
            "costo": 0.30,                     # ERA 0.35 → Costo importante pero no dominante
            "eficiencia": 0.20,                # Aumentar peso en eficiencia
            "disponibilidad": 0.03,
            "tiempo": 0.02
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
        return 0  

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

def detectar_convergencia(historico_fitness, ventana=25, tolerancia=5e-5):
    """
    Detecta si el algoritmo ha convergido (MEJORADO)
    
    Args:
        historico_fitness: Lista con el mejor fitness por generación
        ventana: Número de generaciones a considerar (AUMENTADO: era 20)
        tolerancia: Tolerancia para considerar convergencia (AUMENTADO: era 1e-6)
        
    Returns:
        True si ha convergido, False en caso contrario
    """
    if len(historico_fitness) < ventana:
        return False
    
    # Obtener últimas 'ventana' generaciones
    ultimas_generaciones = historico_fitness[-ventana:]
    
    # Verificar si la mejora es menor que la tolerancia
    mejora = ultimas_generaciones[0] - ultimas_generaciones[-1]
    
    # MEJORA: También verificar que no haya variaciones significativas
    varianza = sum((f - sum(ultimas_generaciones)/len(ultimas_generaciones))**2 
                  for f in ultimas_generaciones) / len(ultimas_generaciones)
    
    return mejora < tolerancia and varianza < tolerancia * 10

