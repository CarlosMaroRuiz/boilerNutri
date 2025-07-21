"""
Operadores de selección para el algoritmo genético.

Implementa diferentes métodos de selección de padres
para la reproducción.
"""

import random
import math

def seleccionar_padre(poblacion, metodo="torneo", tamano_torneo=3, **kwargs):
    """
    Selecciona un individuo de la población para reproducción
    
    Args:
        poblacion: Lista de individuos
        metodo: Método de selección ("torneo", "ruleta", "ranking")
        tamano_torneo: Tamaño del torneo para selección por torneo
        **kwargs: Argumentos adicionales para métodos específicos
        
    Returns:
        Individuo seleccionado
    """
    if not poblacion:
        return None
    
    if metodo == "torneo":
        return seleccion_torneo(poblacion, tamano_torneo)
    elif metodo == "ruleta":
        return seleccion_ruleta(poblacion)
    elif metodo == "ranking":
        return seleccion_ranking(poblacion)
    elif metodo == "elitista":
        return seleccion_elitista(poblacion, kwargs.get("top_n", 1))[0]
    else:
        # Por defecto, selección por torneo
        return seleccion_torneo(poblacion, tamano_torneo)

def seleccion_torneo(poblacion, tamano_torneo=3):
    """
    Selecciona un individuo usando selección por torneo.
    Selecciona al individuo con menor fitness (mejor) entre un subconjunto aleatorio.
    
    Args:
        poblacion: Lista de individuos
        tamano_torneo: Número de individuos que participan en el torneo
        
    Returns:
        Individuo ganador del torneo
    """
    # Asegurar que el tamaño del torneo no exceda el tamaño de la población
    tamano_torneo = min(tamano_torneo, len(poblacion))
    
    # Seleccionar individuos aleatorios para el torneo
    participantes = random.sample(poblacion, tamano_torneo)
    
    # Seleccionar el mejor (menor fitness)
    ganador = min(participantes, key=lambda ind: ind.fitness)
    
    return ganador

def seleccion_ruleta(poblacion):
    """
    Selecciona un individuo usando selección por ruleta (proporcional al fitness)
    
    Args:
        poblacion: Lista de individuos
        
    Returns:
        Individuo seleccionado
    """
    if not poblacion:
        return None
    
    # Convertir fitness (minimización) a probabilidades de selección
    # Usar el inverso del fitness para que menores valores tengan mayor probabilidad
    fitness_values = [ind.fitness for ind in poblacion]
    max_fitness = max(fitness_values)
    
    # Calcular probabilidades inversas
    probabilidades = []
    for fitness in fitness_values:
        # Evitar división por cero
        if fitness == 0:
            prob = max_fitness + 1
        else:
            prob = max_fitness - fitness + 1
        probabilidades.append(prob)
    
    # Normalizar probabilidades
    suma_probabilidades = sum(probabilidades)
    if suma_probabilidades == 0:
        return random.choice(poblacion)
    
    probabilidades = [p / suma_probabilidades for p in probabilidades]
    
    # Selección usando ruleta
    r = random.random()
    suma_acumulada = 0
    
    for i, prob in enumerate(probabilidades):
        suma_acumulada += prob
        if r <= suma_acumulada:
            return poblacion[i]
    
    # En caso de error de redondeo, devolver el último
    return poblacion[-1]

def seleccion_ranking(poblacion, presion_selectiva=2.0):
    """
    Selecciona un individuo usando selección por ranking
    
    Args:
        poblacion: Lista de individuos
        presion_selectiva: Presión selectiva (1.0-2.0, donde 2.0 es máxima presión)
        
    Returns:
        Individuo seleccionado
    """
    if not poblacion:
        return None
    
    # Ordenar población por fitness (mejor primero)
    poblacion_ordenada = sorted(poblacion, key=lambda ind: ind.fitness)
    n = len(poblacion_ordenada)
    
    # Calcular probabilidades basadas en ranking
    probabilidades = []
    for i in range(n):
        # Ranking: el mejor tiene rank n, el peor tiene rank 1
        rank = n - i
        prob = (2 - presion_selectiva) / n + (2 * (presion_selectiva - 1) * (rank - 1)) / (n * (n - 1))
        probabilidades.append(prob)
    
    # Selección usando las probabilidades calculadas
    r = random.random()
    suma_acumulada = 0
    
    for i, prob in enumerate(probabilidades):
        suma_acumulada += prob
        if r <= suma_acumulada:
            return poblacion_ordenada[i]
    
    return poblacion_ordenada[-1]

def seleccion_elitista(poblacion, num_elite):
    """
    Selecciona los mejores individuos (elitismo)
    
    Args:
        poblacion: Lista de individuos
        num_elite: Número de individuos elite a seleccionar
        
    Returns:
        Lista de individuos elite
    """
    if not poblacion:
        return []
    
    # Ordenar por fitness (mejor primero) y tomar los primeros
    poblacion_ordenada = sorted(poblacion, key=lambda ind: ind.fitness)
    num_elite = min(num_elite, len(poblacion_ordenada))
    
    return poblacion_ordenada[:num_elite]

def seleccion_diversa(poblacion, num_seleccionar, metodo_diversidad="distancia"):
    """
    Selecciona individuos promoviendo diversidad
    
    Args:
        poblacion: Lista de individuos
        num_seleccionar: Número de individuos a seleccionar
        metodo_diversidad: Método para medir diversidad
        
    Returns:
        Lista de individuos diversos
    """
    if not poblacion or num_seleccionar <= 0:
        return []
    
    seleccionados = []
    candidatos = poblacion.copy()
    
    # Seleccionar el mejor primero
    mejor = min(candidatos, key=lambda ind: ind.fitness)
    seleccionados.append(mejor)
    candidatos.remove(mejor)
    
    # Seleccionar los demás promoviendo diversidad
    while len(seleccionados) < num_seleccionar and candidatos:
        mejor_candidato = None
        mejor_score = -float('inf')
        
        for candidato in candidatos:
            # Calcular score combinando fitness y diversidad
            score_fitness = 1.0 / (1.0 + candidato.fitness)  # Mejor fitness = mayor score
            score_diversidad = calcular_diversidad_individuo(candidato, seleccionados)
            
            score_total = 0.7 * score_fitness + 0.3 * score_diversidad
            
            if score_total > mejor_score:
                mejor_score = score_total
                mejor_candidato = candidato
        
        if mejor_candidato:
            seleccionados.append(mejor_candidato)
            candidatos.remove(mejor_candidato)
        else:
            break
    
    return seleccionados

def calcular_diversidad_individuo(individuo, grupo_referencia):
    """
    Calcula qué tan diverso es un individuo respecto a un grupo
    
    Args:
        individuo: Individuo a evaluar
        grupo_referencia: Grupo de individuos de referencia
        
    Returns:
        Score de diversidad (mayor = más diverso)
    """
    if not grupo_referencia:
        return 1.0
    
    # Calcular distancia promedio a los individuos del grupo
    distancias = []
    
    for ref in grupo_referencia:
        distancia = calcular_distancia_individuos(individuo, ref)
        distancias.append(distancia)
    
    return sum(distancias) / len(distancias)

def calcular_distancia_individuos(individuo1, individuo2):
    """
    Calcula la distancia entre dos individuos basada en sus porcentajes
    
    Args:
        individuo1: Primer individuo
        individuo2: Segundo individuo
        
    Returns:
        Distancia euclidiana entre los individuos
    """
    if len(individuo1.porcentajes) != len(individuo2.porcentajes):
        return 0
    
    suma_cuadrados = 0
    for i in range(len(individuo1.porcentajes)):
        diferencia = individuo1.porcentajes[i] - individuo2.porcentajes[i]
        suma_cuadrados += diferencia ** 2
    
    return math.sqrt(suma_cuadrados)

def ajustar_presion_selectiva(fase_actual, presion_inicial=1.5, presion_final=2.0):
    """
    Ajusta la presión selectiva según la fase del algoritmo
    
    Args:
        fase_actual: Fase actual ("inicial", "intermedia", "final")
        presion_inicial: Presión selectiva en fase inicial
        presion_final: Presión selectiva en fase final
        
    Returns:
        Presión selectiva ajustada
    """
    if fase_actual == "inicial":
        return presion_inicial
    elif fase_actual == "intermedia":
        return (presion_inicial + presion_final) / 2
    else:  # fase final
        return presion_final

def seleccionar_padres_adaptativo(poblacion, fase_algoritmo="inicial", num_padres=2):
    """
    Selecciona padres con estrategia adaptativa según la fase
    
    Args:
        poblacion: Lista de individuos
        fase_algoritmo: Fase actual del algoritmo
        num_padres: Número de padres a seleccionar
        
    Returns:
        Lista de padres seleccionados
    """
    padres = []
    
    if fase_algoritmo == "inicial":
        # En fase inicial, priorizar diversidad
        for _ in range(num_padres):
            if random.random() < 0.7:  # 70% torneo, 30% ruleta
                padre = seleccion_torneo(poblacion, tamano_torneo=3)
            else:
                padre = seleccion_ruleta(poblacion)
            padres.append(padre)
    
    elif fase_algoritmo == "intermedia":
        # En fase intermedia, balance entre calidad y diversidad
        for _ in range(num_padres):
            if random.random() < 0.8:  # 80% torneo, 20% ranking
                padre = seleccion_torneo(poblacion, tamano_torneo=4)
            else:
                padre = seleccion_ranking(poblacion, presion_selectiva=1.7)
            padres.append(padre)
    
    else:  # fase final
        # En fase final, priorizar calidad
        for _ in range(num_padres):
            if random.random() < 0.9:  # 90% torneo con mayor presión
                padre = seleccion_torneo(poblacion, tamano_torneo=5)
            else:
                padre = seleccion_ranking(poblacion, presion_selectiva=2.0)
            padres.append(padre)
    
    return padres

def calcular_metricas_seleccion(poblacion, seleccionados):
    """
    Calcula métricas sobre el proceso de selección
    
    Args:
        poblacion: Población original
        seleccionados: Individuos seleccionados
        
    Returns:
        Diccionario con métricas de selección
    """
    if not poblacion or not seleccionados:
        return {}
    
    fitness_poblacion = [ind.fitness for ind in poblacion]
    fitness_seleccionados = [ind.fitness for ind in seleccionados]
    
    metricas = {
        "fitness_promedio_poblacion": sum(fitness_poblacion) / len(fitness_poblacion),
        "fitness_promedio_seleccionados": sum(fitness_seleccionados) / len(fitness_seleccionados),
        "mejor_fitness_poblacion": min(fitness_poblacion),
        "mejor_fitness_seleccionados": min(fitness_seleccionados),
        "presion_selectiva": len(poblacion) / len(seleccionados) if seleccionados else 0
    }
    
    # Calcular mejora por selección
    metricas["mejora_seleccion"] = (
        metricas["fitness_promedio_poblacion"] - metricas["fitness_promedio_seleccionados"]
    )
    
    return metricas