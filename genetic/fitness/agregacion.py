from genetic.fitness.nutricion import calcular_discrepancia_nutricional
from genetic.fitness.costo import calcular_costo_total
from genetic.fitness.eficiencia import estimar_eficiencia_alimenticia
from genetic.fitness.disponibilidad import calcular_disponibilidad_local
from genetic.fitness.tiempo import estimar_tiempo_peso_objetivo
from genetic.fitness.restricciones import verificar_restricciones
from conocimiento.requerimientos import obtener_etapa

def calcular_fitness(individuo, config_evaluacion, ingredientes_data, restricciones_usuario=None):
  
    raza = config_evaluacion.get("raza", "Ross")
    edad_dias = config_evaluacion.get("edad_dias", 35)
    peso_actual = config_evaluacion.get("peso_actual", 1.5)
    peso_objetivo = config_evaluacion.get("peso_objetivo", 2.5)
    pesos = config_evaluacion.get("pesos", {})
    
    # Determinar etapa según edad
    etapa = obtener_etapa(edad_dias)
    
    
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
    
    componentes_normalizados = normalizar_objetivos_mejorado(componentes)
    
    # Aplicar ponderaciones
    fitness = calcular_fitness_ponderado(componentes_normalizados, pesos)
    
    # Almacenar en el individuo
    individuo.fitness = fitness
    
    return fitness

def calcular_fitness_adaptativo(individuo, config_evaluacion, ingredientes_data, 
                               restricciones_usuario=None, fase="inicial", generacion=0):
    """
    Calcula el fitness con pesos adaptativos según la fase del algoritmo.
    
    Args:
        individuo: Objeto individuo con porcentajes
        config_evaluacion: Diccionario con configuración de evaluación
        ingredientes_data: Lista de datos de ingredientes
        restricciones_usuario: Objeto con restricciones del usuario (opcional)
        fase: Fase actual del algoritmo ("inicial", "intermedia", "final")
        generacion: Número de generación actual
        
    Returns:
        Valor de fitness global adaptativo (menor es mejor)
    """
    # Obtener pesos adaptativos según la fase
    pesos_adaptativos = obtener_pesos_por_fase(fase, generacion)
    
    # Actualizar configuración con pesos adaptativos
    config_adaptativa = config_evaluacion.copy()
    config_adaptativa["pesos"] = pesos_adaptativos
    
    # Calcular fitness con pesos adaptativos
    return calcular_fitness(individuo, config_adaptativa, ingredientes_data, restricciones_usuario)

def obtener_pesos_por_fase(fase, generacion=0):
    """
    Obtiene pesos adaptativos según la fase del algoritmo.
    
    Args:
        fase: Fase actual ("inicial", "intermedia", "final")
        generacion: Número de generación actual
        
    Returns:
        Diccionario con pesos adaptativos
    """
    if fase == "inicial":
       
        return {
            "discrepancia_nutricional": 0.45,  
            "costo": 0.20,                     
            "eficiencia": 0.15,
            "disponibilidad": 0.10,
            "tiempo": 0.10
        }
    elif fase == "intermedia":
        # Fase intermedia: Balance equilibrado
        return {
            "discrepancia_nutricional": 0.35,
            "costo": 0.30,                     # Incrementar importancia del costo
            "eficiencia": 0.15,
            "disponibilidad": 0.10,
            "tiempo": 0.10
        }
    else:  # fase == "final"
        # Fase final: Optimización fina, priorizar costo y eficiencia
        return {
            "discrepancia_nutricional": 0.30,
            "costo": 0.35,                     # Mayor prioridad al costo
            "eficiencia": 0.20,                # Mayor prioridad a eficiencia
            "disponibilidad": 0.10,
            "tiempo": 0.05                     # Menor prioridad al tiempo
        }

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
    Calcula el fitness aplicando ponderaciones
    
    Args:
        componentes_normalizados: Componentes ya normalizados
        pesos_personalizados: Pesos específicos (opcional)
        
    Returns:
        Valor de fitness ponderado
    """
    # Pesos por defecto
    pesos_default = {
        "discrepancia_nutricional": 0.35,
        "costo": 0.30,
        "eficiencia": 0.15,
        "disponibilidad": 0.10,
        "tiempo": 0.10
    }
    
    # Usar pesos personalizados si se proporcionan
    pesos = pesos_personalizados if pesos_personalizados else pesos_default
    
    fitness = 0
    
    # Sumar componentes ponderados
    for componente, valor in componentes_normalizados.items():
        if componente == "restricciones":
            # Las restricciones se suman directamente como penalización
            fitness += valor
        else:
            # Los demás objetivos se ponderan
            peso = pesos.get(componente, 0)
            fitness += peso * valor
    
    return fitness

def evaluar_poblacion(poblacion, config_evaluacion, ingredientes_data, 
                     restricciones_usuario=None, fase="inicial", generacion=0):
    """
    Evalúa toda una población de individuos
    
    Args:
        poblacion: Lista de individuos
        config_evaluacion: Configuración de evaluación
        ingredientes_data: Datos de ingredientes
        restricciones_usuario: Restricciones del usuario (opcional)
        fase: Fase actual del algoritmo
        generacion: Generación actual
    """
    for individuo in poblacion:
        calcular_fitness_adaptativo(
            individuo, config_evaluacion, ingredientes_data, 
            restricciones_usuario, fase, generacion
        )
    
    # Ordenar por fitness (menor es mejor)
    poblacion.sort(key=lambda ind: ind.fitness)

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

def calcular_metricas_poblacion(poblacion):
    """
    Calcula métricas estadísticas de la población
    
    Args:
        poblacion: Lista de individuos evaluados
        
    Returns:
        Diccionario con métricas de la población
    """
    if not poblacion:
        return {}
    
    fitness_values = [ind.fitness for ind in poblacion]
    costo_values = [getattr(ind, 'costo_total', 0) for ind in poblacion]
    
    metricas = {
        "fitness": {
            "mejor": min(fitness_values),
            "peor": max(fitness_values),
            "promedio": sum(fitness_values) / len(fitness_values)
        }
    }
    
    if any(costo_values):
        metricas["costo"] = {
            "mejor": min(c for c in costo_values if c > 0),
            "peor": max(costo_values),
            "promedio": sum(costo_values) / len(costo_values)
        }
    
    # Calcular diversidad (desviación estándar del fitness)
    promedio_fitness = metricas["fitness"]["promedio"]
    varianza = sum((f - promedio_fitness) ** 2 for f in fitness_values) / len(fitness_values)
    metricas["diversidad"] = varianza ** 0.5
    
    return metricas