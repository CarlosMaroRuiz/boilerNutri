"""
Métodos para inicializar la población del algoritmo genético.

Contiene estrategias de inicialización que respetan restricciones
y generan diversidad en la población inicial.
"""

import random
import numpy as np
from genetic.individuo import Individuo

def crear_poblacion_inicial(tamano_poblacion, ingredientes_data, restricciones_usuario=None, 
                          estrategia="mixta", semilla=None):
    """
    Crea la población inicial del algoritmo genético
    
    Args:
        tamano_poblacion: Número de individuos en la población
        ingredientes_data: Lista de datos de ingredientes
        restricciones_usuario: Objeto con restricciones del usuario
        estrategia: Estrategia de inicialización ("aleatoria", "sesgada", "mixta")
        semilla: Semilla para reproducibilidad
        
    Returns:
        Lista de individuos inicializados
    """
    if semilla is not None:
        random.seed(semilla)
        np.random.seed(semilla)
    
    poblacion = []
    num_ingredientes = len(ingredientes_data)
    
    # Filtrar ingredientes disponibles según restricciones del usuario
    ingredientes_disponibles = []
    for i in range(num_ingredientes):
        if not restricciones_usuario or restricciones_usuario.es_ingrediente_valido(i):
            ingredientes_disponibles.append(i)
    
    if not ingredientes_disponibles:
        raise ValueError("No hay ingredientes disponibles para crear la población")
    
    # Crear individuos según la estrategia
    if estrategia == "aleatoria":
        poblacion = crear_poblacion_aleatoria(tamano_poblacion, num_ingredientes, 
                                            ingredientes_data, restricciones_usuario)
    elif estrategia == "sesgada":
        poblacion = crear_poblacion_sesgada(tamano_poblacion, num_ingredientes,
                                          ingredientes_data, restricciones_usuario)
    elif estrategia == "mixta":
        # 70% aleatoria, 20% sesgada, 10% basada en conocimiento
        num_aleatoria = int(tamano_poblacion * 0.7)
        num_sesgada = int(tamano_poblacion * 0.2)
        num_conocimiento = tamano_poblacion - num_aleatoria - num_sesgada
        
        poblacion.extend(crear_poblacion_aleatoria(num_aleatoria, num_ingredientes,
                                                 ingredientes_data, restricciones_usuario))
        poblacion.extend(crear_poblacion_sesgada(num_sesgada, num_ingredientes,
                                               ingredientes_data, restricciones_usuario))
        poblacion.extend(crear_poblacion_basada_conocimiento(num_conocimiento, num_ingredientes,
                                                           ingredientes_data, restricciones_usuario))
    else:
        raise ValueError(f"Estrategia de inicialización no reconocida: {estrategia}")
    
    # Validar y reparar individuos si es necesario
    poblacion_validada = []
    for individuo in poblacion:
        if validar_individuo(individuo, ingredientes_data, restricciones_usuario):
            poblacion_validada.append(individuo)
        else:
            individuo_reparado = reparar_individuo(individuo, ingredientes_data, restricciones_usuario)
            if individuo_reparado:
                poblacion_validada.append(individuo_reparado)
    
    # Si no tenemos suficientes individuos válidos, crear más aleatorios
    while len(poblacion_validada) < tamano_poblacion:
        nuevo_individuo = crear_individuo_aleatorio(num_ingredientes, ingredientes_data, restricciones_usuario)
        if validar_individuo(nuevo_individuo, ingredientes_data, restricciones_usuario):
            poblacion_validada.append(nuevo_individuo)
    
    return poblacion_validada[:tamano_poblacion]

def crear_poblacion_aleatoria(tamano_poblacion, num_ingredientes, ingredientes_data, restricciones_usuario=None):
    """
    Crea una población con inicialización completamente aleatoria
    
    Args:
        tamano_poblacion: Número de individuos a crear
        num_ingredientes: Número de ingredientes
        ingredientes_data: Lista de datos de ingredientes
        restricciones_usuario: Objeto con restricciones del usuario
        
    Returns:
        Lista de individuos aleatorios
    """
    poblacion = []
    
    for _ in range(tamano_poblacion):
        individuo = crear_individuo_aleatorio(num_ingredientes, ingredientes_data, restricciones_usuario)
        poblacion.append(individuo)
    
    return poblacion

def crear_individuo_aleatorio(num_ingredientes, ingredientes_data, restricciones_usuario=None):
    """
    Crea un individuo con inicialización aleatoria respetando restricciones
    
    Args:
        num_ingredientes: Número de ingredientes
        ingredientes_data: Lista de datos de ingredientes
        restricciones_usuario: Objeto con restricciones del usuario
        
    Returns:
        Individuo inicializado aleatoriamente
    """
    individuo = Individuo(num_ingredientes)
    individuo.inicializar_aleatorio(ingredientes_data, restricciones_usuario)
    return individuo

def crear_poblacion_sesgada(tamano_poblacion, num_ingredientes, ingredientes_data, restricciones_usuario=None):
    """
    Crea una población con sesgo hacia ingredientes más económicos y disponibles
    
    Args:
        tamano_poblacion: Número de individuos a crear
        num_ingredientes: Número de ingredientes
        ingredientes_data: Lista de datos de ingredientes
        restricciones_usuario: Objeto con restricciones del usuario
        
    Returns:
        Lista de individuos sesgados
    """
    poblacion = []
    
    # Calcular scores de preferencia para cada ingrediente
    scores_preferencia = calcular_scores_preferencia(ingredientes_data)
    
    for _ in range(tamano_poblacion):
        individuo = crear_individuo_sesgado(num_ingredientes, ingredientes_data, 
                                          scores_preferencia, restricciones_usuario)
        poblacion.append(individuo)
    
    return poblacion

def crear_individuo_sesgado(num_ingredientes, ingredientes_data, scores_preferencia, restricciones_usuario=None):
    """
    Crea un individuo sesgado hacia ingredientes preferidos
    
    Args:
        num_ingredientes: Número de ingredientes
        ingredientes_data: Lista de datos de ingredientes
        scores_preferencia: Scores de preferencia para cada ingrediente
        restricciones_usuario: Objeto con restricciones del usuario
        
    Returns:
        Individuo sesgado
    """
    individuo = Individuo(num_ingredientes)
    
    # Inicializar con valores sesgados
    for i in range(num_ingredientes):
        # Verificar disponibilidad según restricciones del usuario
        if restricciones_usuario and not restricciones_usuario.es_ingrediente_valido(i):
            individuo.porcentajes[i] = 0
            continue
        
        if i < len(ingredientes_data):
            # Obtener límites del ingrediente
            limites_originales = ingredientes_data[i]["limitaciones"]
            if restricciones_usuario:
                limites = restricciones_usuario.obtener_limites(i, limites_originales)
            else:
                limites = limites_originales
            
            min_val = limites["min"]
            max_val = limites["max"]
            
            # Si es ingrediente fijo
            if abs(min_val - max_val) < 1e-6:
                individuo.porcentajes[i] = min_val
            else:
                # Sesgar hacia valores más altos para ingredientes preferidos
                score = scores_preferencia.get(i, 0.5)
                
                # Usar distribución beta para sesgar
                if score > 0.7:  # Ingrediente muy preferido
                    alpha, beta = 2, 1  # Sesgo hacia valores altos
                elif score > 0.5:  # Ingrediente moderadamente preferido
                    alpha, beta = 1.5, 1.5  # Distribución más uniforme
                else:  # Ingrediente menos preferido
                    alpha, beta = 1, 2  # Sesgo hacia valores bajos
                
                valor_beta = np.random.beta(alpha, beta)
                valor_escalado = min_val + valor_beta * (max_val - min_val)
                individuo.porcentajes[i] = valor_escalado
    
    # Normalizar
    individuo.normalizar(ingredientes_data, restricciones_usuario)
    
    return individuo

def crear_poblacion_basada_conocimiento(tamano_poblacion, num_ingredientes, ingredientes_data, restricciones_usuario=None):
    """
    Crea una población basada en conocimiento experto de formulaciones típicas
    
    Args:
        tamano_poblacion: Número de individuos a crear
        num_ingredientes: Número de ingredientes
        ingredientes_data: Lista de datos de ingredientes
        restricciones_usuario: Objeto con restricciones del usuario
        
    Returns:
        Lista de individuos basados en conocimiento
    """
    poblacion = []
    
    # Plantillas de formulaciones típicas
    plantillas = generar_plantillas_conocimiento(ingredientes_data)
    
    for i in range(tamano_poblacion):
        # Seleccionar plantilla aleatoria
        plantilla = random.choice(plantillas) if plantillas else None
        
        if plantilla:
            individuo = crear_individuo_desde_plantilla(plantilla, num_ingredientes, 
                                                      ingredientes_data, restricciones_usuario)
        else:
            # Si no hay plantillas, crear aleatorio
            individuo = crear_individuo_aleatorio(num_ingredientes, ingredientes_data, restricciones_usuario)
        
        poblacion.append(individuo)
    
    return poblacion

def generar_plantillas_conocimiento(ingredientes_data):
    """
    Genera plantillas de formulaciones basadas en conocimiento experto
    
    Args:
        ingredientes_data: Lista de datos de ingredientes
        
    Returns:
        Lista de plantillas (diccionarios con porcentajes por ingrediente)
    """
    plantillas = []
    
    # Mapear ingredientes por nombre para crear plantillas
    mapa_ingredientes = {}
    for i, ingrediente in enumerate(ingredientes_data):
        nombre = ingrediente["nombre"].lower()
        mapa_ingredientes[nombre] = i
    
    # Plantilla 1: Formulación económica básica
    if "maíz" in mapa_ingredientes and "pasta de soya" in mapa_ingredientes:
        plantilla1 = {
            mapa_ingredientes["maíz"]: 0.60,
            mapa_ingredientes["pasta de soya"]: 0.25
        }
        
        # Añadir premezcla si está disponible
        for nombre in ["premezcla micro/macro minerales económica", "premezcla micro/macro minerales premium"]:
            if nombre in mapa_ingredientes:
                plantilla1[mapa_ingredientes[nombre]] = 0.02
                break
        
        # Completar con otros ingredientes disponibles
        suma_asignada = sum(plantilla1.values())
        if suma_asignada < 1.0:
            resto = 1.0 - suma_asignada
            # Distribuir resto entre ingredientes no asignados
            ingredientes_libres = [i for i in range(len(ingredientes_data)) if i not in plantilla1]
            if ingredientes_libres:
                porcentaje_libre = resto / len(ingredientes_libres)
                for i in ingredientes_libres:
                    plantilla1[i] = porcentaje_libre
        
        plantillas.append(plantilla1)
    
    # Plantilla 2: Formulación con sorgo (alternativa económica)
    if "sorgo" in mapa_ingredientes and "pasta de soya" in mapa_ingredientes:
        plantilla2 = {
            mapa_ingredientes["sorgo"]: 0.50,
            mapa_ingredientes["pasta de soya"]: 0.30
        }
        
        # Añadir maíz si está disponible
        if "maíz" in mapa_ingredientes:
            plantilla2[mapa_ingredientes["maíz"]] = 0.15
        
        # Añadir premezcla
        for nombre in ["premezcla micro/macro minerales premium", "premezcla micro/macro minerales económica"]:
            if nombre in mapa_ingredientes:
                plantilla2[mapa_ingredientes[nombre]] = 0.02
                break
        
        # Completar resto
        suma_asignada = sum(plantilla2.values())
        if suma_asignada < 1.0:
            resto = 1.0 - suma_asignada
            ingredientes_libres = [i for i in range(len(ingredientes_data)) if i not in plantilla2]
            if ingredientes_libres:
                porcentaje_libre = resto / len(ingredientes_libres)
                for i in ingredientes_libres:
                    plantilla2[i] = porcentaje_libre
        
        plantillas.append(plantilla2)
    
    # Plantilla 3: Formulación con DDG (subproducto)
    if "ddg" in mapa_ingredientes and "maíz" in mapa_ingredientes:
        plantilla3 = {
            mapa_ingredientes["maíz"]: 0.45,
            mapa_ingredientes["ddg"]: 0.10
        }
        
        if "pasta de soya" in mapa_ingredientes:
            plantilla3[mapa_ingredientes["pasta de soya"]] = 0.20
        
        # Completar resto
        suma_asignada = sum(plantilla3.values())
        if suma_asignada < 1.0:
            resto = 1.0 - suma_asignada
            ingredientes_libres = [i for i in range(len(ingredientes_data)) if i not in plantilla3]
            if ingredientes_libres:
                porcentaje_libre = resto / len(ingredientes_libres)
                for i in ingredientes_libres:
                    plantilla3[i] = porcentaje_libre
        
        plantillas.append(plantilla3)
    
    return plantillas

def crear_individuo_desde_plantilla(plantilla, num_ingredientes, ingredientes_data, restricciones_usuario=None):
    """
    Crea un individuo basado en una plantilla con variación aleatoria
    
    Args:
        plantilla: Diccionario con porcentajes base
        num_ingredientes: Número de ingredientes
        ingredientes_data: Lista de datos de ingredientes
        restricciones_usuario: Objeto con restricciones del usuario
        
    Returns:
        Individuo basado en plantilla
    """
    individuo = Individuo(num_ingredientes)
    
    # Inicializar con plantilla
    for i in range(num_ingredientes):
        if i in plantilla:
            individuo.porcentajes[i] = plantilla[i]
        else:
            individuo.porcentajes[i] = 0
    
    # Añadir variación aleatoria (±10%)
    factor_variacion = 0.1
    for i in range(num_ingredientes):
        if individuo.porcentajes[i] > 0:
            variacion = (random.random() - 0.5) * 2 * factor_variacion
            nuevo_valor = individuo.porcentajes[i] * (1 + variacion)
            individuo.porcentajes[i] = max(0, nuevo_valor)
    
    # Aplicar restricciones y normalizar
    if restricciones_usuario:
        restricciones_usuario.aplicar_restricciones_a_individuo(individuo, ingredientes_data)
    else:
        individuo.aplicar_limites(ingredientes_data)
        individuo.normalizar(ingredientes_data)
    
    return individuo

def calcular_scores_preferencia(ingredientes_data):
    """
    Calcula scores de preferencia para cada ingrediente basado en costo y disponibilidad
    
    Args:
        ingredientes_data: Lista de datos de ingredientes
        
    Returns:
        Diccionario con scores de preferencia (0-1, mayor es mejor)
    """
    scores = {}
    
    if not ingredientes_data:
        return scores
    
    # Obtener rangos de precios y disponibilidad
    precios_base = []
    disponibilidades = []
    
    for ingrediente in ingredientes_data:
        precio_base = ingrediente.get("precio_base", 0)
        disponibilidad = ingrediente.get("disponibilidadLocal", 0.5)
        
        precios_base.append(precio_base)
        disponibilidades.append(disponibilidad)
    
    if not precios_base:
        return scores
    
    precio_min = min(p for p in precios_base if p > 0)
    precio_max = max(precios_base)
    
    # Calcular scores
    for i, ingrediente in enumerate(ingredientes_data):
        precio_base = ingrediente.get("precio_base", precio_max)
        disponibilidad = ingrediente.get("disponibilidadLocal", 0.5)
        
        # Score de precio (inversamente proporcional al precio)
        if precio_max > precio_min:
            score_precio = 1 - (precio_base - precio_min) / (precio_max - precio_min)
        else:
            score_precio = 1.0
        
        # Score de disponibilidad (directamente proporcional)
        score_disponibilidad = disponibilidad
        
        # Score combinado (70% precio, 30% disponibilidad)
        score_total = 0.7 * score_precio + 0.3 * score_disponibilidad
        
        scores[i] = score_total
    
    return scores

def validar_individuo(individuo, ingredientes_data, restricciones_usuario=None):
    """
    Valida que un individuo cumple con las restricciones básicas
    
    Args:
        individuo: Individuo a validar
        ingredientes_data: Lista de datos de ingredientes
        restricciones_usuario: Objeto con restricciones del usuario
        
    Returns:
        True si el individuo es válido
    """
    # Verificar suma de porcentajes
    if not individuo.validar_suma():
        return False
    
    # Verificar restricciones del usuario si existen
    if restricciones_usuario:
        es_valido, _ = restricciones_usuario.validar_restricciones(individuo, ingredientes_data)
        if not es_valido:
            return False
    
    # Verificar límites de ingredientes
    for i, porcentaje in enumerate(individuo.porcentajes):
        if i < len(ingredientes_data):
            limites = ingredientes_data[i]["limitaciones"]
            if porcentaje < limites["min"] - 1e-6 or porcentaje > limites["max"] + 1e-6:
                return False
    
    return True

def reparar_individuo(individuo, ingredientes_data, restricciones_usuario=None):
    """
    Intenta reparar un individuo que viola restricciones
    
    Args:
        individuo: Individuo a reparar
        ingredientes_data: Lista de datos de ingredientes
        restricciones_usuario: Objeto con restricciones del usuario
        
    Returns:
        Individuo reparado o None si no se pudo reparar
    """
    try:
        individuo_reparado = individuo.clonar()
        
        # Aplicar restricciones del usuario
        if restricciones_usuario:
            restricciones_usuario.aplicar_restricciones_a_individuo(individuo_reparado, ingredientes_data)
        
        # Aplicar límites de ingredientes
        individuo_reparado.aplicar_limites(ingredientes_data, restricciones_usuario)
        
        # Normalizar
        individuo_reparado.normalizar(ingredientes_data, restricciones_usuario)
        
        # Verificar si la reparación fue exitosa
        if validar_individuo(individuo_reparado, ingredientes_data, restricciones_usuario):
            return individuo_reparado
        else:
            return None
    
    except Exception:
        return None

def generar_estadisticas_poblacion(poblacion, ingredientes_data):
    """
    Genera estadísticas de la población inicial
    
    Args:
        poblacion: Lista de individuos
        ingredientes_data: Lista de datos de ingredientes
        
    Returns:
        Diccionario con estadísticas
    """
    if not poblacion:
        return {}
    
    estadisticas = {
        "tamano_poblacion": len(poblacion),
        "ingredientes_activos": {},
        "diversidad_poblacion": 0,
        "suma_valida": 0
    }
    
    # Contar individuos con suma válida
    for individuo in poblacion:
        if individuo.validar_suma():
            estadisticas["suma_valida"] += 1
    
    # Analizar uso de ingredientes
    for i, ingrediente in enumerate(ingredientes_data):
        nombre = ingrediente["nombre"]
        usos = []
        
        for individuo in poblacion:
            if i < len(individuo.porcentajes):
                usos.append(individuo.porcentajes[i])
        
        if usos:
            estadisticas["ingredientes_activos"][nombre] = {
                "promedio": sum(usos) / len(usos),
                "minimo": min(usos),
                "maximo": max(usos),
                "individuos_que_lo_usan": sum(1 for uso in usos if uso > 0.001)
            }
    
    # Calcular diversidad (coeficiente de variación promedio)
    diversidades = []
    num_ingredientes = len(ingredientes_data)
    
    for i in range(num_ingredientes):
        valores = [ind.porcentajes[i] for ind in poblacion if i < len(ind.porcentajes)]
        if valores and len(valores) > 1:
            promedio = sum(valores) / len(valores)
            if promedio > 0:
                varianza = sum((v - promedio) ** 2 for v in valores) / len(valores)
                cv = (varianza ** 0.5) / promedio
                diversidades.append(cv)
    
    if diversidades:
        estadisticas["diversidad_poblacion"] = sum(diversidades) / len(diversidades)
    
    return estadisticas