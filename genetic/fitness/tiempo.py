"""
Función objetivo: Tiempo hasta peso objetivo.

Estima el tiempo necesario para alcanzar el peso de venta
basado en la calidad de la formulación.
"""

from conocimiento.razas import  estimar_dias_hasta_peso
from genetic.fitness.eficiencia import estimar_ganancia_peso_diaria

def estimar_tiempo_peso_objetivo(individuo, peso_actual, peso_objetivo, raza, edad_dias, ingredientes_data):
    """
    Estima los días necesarios para alcanzar el peso objetivo.
    
    Esta función debe ser MINIMIZADA porque:
    - Menor tiempo hasta el peso objetivo reduce costos operativos
    - Acelera el ciclo de producción y aumenta la rentabilidad
    - Reduce riesgos asociados con períodos de crianza prolongados
    
    Args:
        individuo: Objeto individuo con porcentajes
        peso_actual: Peso actual promedio en kg
        peso_objetivo: Peso objetivo en kg
        raza: Nombre de la raza
        edad_dias: Edad actual en días
        ingredientes_data: Lista de datos de ingredientes
        
    Returns:
        Número estimado de días hasta alcanzar el peso objetivo
    """
    # Validar entradas
    if peso_actual >= peso_objetivo:
        individuo.dias_peso_objetivo = 0
        return 0
    
    if peso_actual <= 0 or peso_objetivo <= 0:
        individuo.dias_peso_objetivo = 999  # Valor alto para penalizar
        return 999
    
    # Estimar usando curvas de la raza como baseline
    dias_baseline = estimar_dias_hasta_peso(peso_actual, peso_objetivo, raza, edad_dias)
    
    if dias_baseline is None:
        # Si no se puede estimar con las curvas, usar método alternativo
        dias_estimados = estimar_tiempo_alternativo(individuo, peso_actual, peso_objetivo, 
                                                  raza, edad_dias, ingredientes_data)
    else:
        # Ajustar el baseline según la calidad de la formulación
        factor_ajuste = calcular_factor_ajuste_tiempo(individuo, raza, edad_dias, ingredientes_data)
        dias_estimados = dias_baseline * factor_ajuste
    
    # Asegurar que el resultado sea realista
    dias_estimados = max(1, min(dias_estimados, 200))  # Entre 1 y 200 días
    
    # Almacenar en el individuo
    individuo.dias_peso_objetivo = dias_estimados
    
    return dias_estimados

def calcular_ganancia_diaria(formulacion, raza, edad_dias, ingredientes_data):
    """
    Calcula la ganancia de peso diaria esperada
    
    Args:
        formulacion: Objeto individuo con porcentajes
        raza: Nombre de la raza
        edad_dias: Edad actual en días
        ingredientes_data: Lista de datos de ingredientes
        
    Returns:
        Ganancia de peso diaria en gramos
    """
    return estimar_ganancia_peso_diaria(formulacion, raza, edad_dias, ingredientes_data)

def calcular_factor_ajuste_tiempo(individuo, raza, edad_dias, ingredientes_data):
    """
    Calcula un factor de ajuste del tiempo basado en la calidad nutricional
    
    Args:
        individuo: Objeto individuo con porcentajes
        raza: Nombre de la raza
        edad_dias: Edad actual en días
        ingredientes_data: Lista de datos de ingredientes
        
    Returns:
        Factor de ajuste (1.0 = normal, >1.0 = más tiempo, <1.0 = menos tiempo)
    """
    from genetic.fitness.nutricion import calcular_discrepancia_nutricional, obtener_etapa
    from genetic.fitness.eficiencia import estimar_eficiencia_alimenticia
    
    # Determinar etapa
    etapa = obtener_etapa(edad_dias)
    
    # Factor base
    factor = 1.0
    
    # Ajuste por discrepancia nutricional
    discrepancia = calcular_discrepancia_nutricional(individuo, etapa, ingredientes_data)
    factor += discrepancia * 0.3  # Hasta 30% más tiempo por mala nutrición
    
    # Ajuste por eficiencia alimenticia
    conversion = estimar_eficiencia_alimenticia(individuo, raza, edad_dias, ingredientes_data)
    if conversion > 0:
        from conocimiento.razas import obtener_conversion_alimenticia
        conversion_base = obtener_conversion_alimenticia(raza, edad_dias)
        
        if conversion_base:
            ratio_conversion = conversion / conversion_base
            # Si la conversión empeora, el tiempo aumenta
            factor *= (ratio_conversion ** 0.5)  # Efecto moderado
    
    # Ajuste por balance de aminoácidos críticos
    factor_aminoacidos = calcular_factor_aminoacidos(individuo, etapa, ingredientes_data)
    factor *= factor_aminoacidos
    
    # Ajuste por nivel energético
    factor_energia = calcular_factor_energia(individuo, etapa, ingredientes_data)
    factor *= factor_energia
    
    # Limitar el factor a rangos razonables
    return max(0.8, min(2.0, factor))

def calcular_factor_aminoacidos(individuo, etapa, ingredientes_data):
    """
    Calcula factor de ajuste basado en aminoácidos esenciales
    
    Args:
        individuo: Objeto individuo con porcentajes
        etapa: Etapa de crecimiento
        ingredientes_data: Lista de datos de ingredientes
        
    Returns:
        Factor de ajuste por aminoácidos
    """
    from conocimiento.requerimientos import REQUERIMIENTOS_NUTRICIONALES
    from genetic.fitness.nutricion import calcular_propiedades_nutricionales
    
    if not hasattr(individuo, 'propiedades_nutricionales') or not individuo.propiedades_nutricionales:
        calcular_propiedades_nutricionales(individuo, ingredientes_data)
    
    requerimientos = REQUERIMIENTOS_NUTRICIONALES.get(etapa, {})
    factor = 1.0
    
    # Aminoácidos críticos para el crecimiento
    aminoacidos_criticos = ["lisina", "metionina"]
    
    for aminoacido in aminoacidos_criticos:
        if aminoacido in requerimientos and aminoacido in individuo.propiedades_nutricionales:
            requerido = requerimientos[aminoacido]
            obtenido = individuo.propiedades_nutricionales[aminoacido]
            
            if obtenido < requerido * 0.9:  # Déficit significativo
                deficit = (requerido - obtenido) / requerido
                factor += deficit * 0.2  # Hasta 20% más tiempo por déficit
    
    return factor

def calcular_factor_energia(individuo, etapa, ingredientes_data):
    """
    Calcula factor de ajuste basado en contenido energético
    
    Args:
        individuo: Objeto individuo con porcentajes
        etapa: Etapa de crecimiento
        ingredientes_data: Lista de datos de ingredientes
        
    Returns:
        Factor de ajuste por energía
    """
    from conocimiento.requerimientos import REQUERIMIENTOS_NUTRICIONALES
    from genetic.fitness.nutricion import calcular_propiedades_nutricionales
    
    if not hasattr(individuo, 'propiedades_nutricionales') or not individuo.propiedades_nutricionales:
        calcular_propiedades_nutricionales(individuo, ingredientes_data)
    
    requerimientos = REQUERIMIENTOS_NUTRICIONALES.get(etapa, {})
    
    if "energia" not in requerimientos or "energia" not in individuo.propiedades_nutricionales:
        return 1.0
    
    energia_requerida = requerimientos["energia"]
    energia_obtenida = individuo.propiedades_nutricionales["energia"]
    
    ratio_energia = energia_obtenida / energia_requerida
    
    if ratio_energia < 0.95:  # Déficit energético
        deficit = 0.95 - ratio_energia
        return 1.0 + deficit * 0.5  # Hasta 50% más tiempo por déficit energético severo
    elif ratio_energia > 1.1:  # Exceso energético (menos eficiente)
        exceso = ratio_energia - 1.1
        return 1.0 + exceso * 0.1  # Pequeña penalización por exceso
    
    return 1.0  # Rango óptimo

def estimar_tiempo_alternativo(individuo, peso_actual, peso_objetivo, raza, edad_dias, ingredientes_data):
    """
    Método alternativo para estimar tiempo cuando no hay curvas de referencia
    
    Args:
        individuo: Objeto individuo con porcentajes
        peso_actual: Peso actual en kg
        peso_objetivo: Peso objetivo en kg
        raza: Nombre de la raza
        edad_dias: Edad actual en días
        ingredientes_data: Lista de datos de ingredientes
        
    Returns:
        Días estimados hasta peso objetivo
    """
    # Ganancia de peso diaria estimada basada en edad y formulación
    ganancia_diaria_base = calcular_ganancia_base_por_edad(edad_dias)
    
    # Ajustar por calidad de la formulación
    from genetic.fitness.nutricion import calcular_discrepancia_nutricional, obtener_etapa
    
    etapa = obtener_etapa(edad_dias)
    discrepancia = calcular_discrepancia_nutricional(individuo, etapa, ingredientes_data)
    
    # Reducir ganancia diaria según discrepancia nutricional
    factor_reduccion = 1.0 - min(0.5, discrepancia)  # Hasta 50% de reducción
    ganancia_diaria_ajustada = ganancia_diaria_base * factor_reduccion
    
    # Calcular días necesarios
    peso_a_ganar = peso_objetivo - peso_actual
    
    if ganancia_diaria_ajustada > 0:
        dias_estimados = (peso_a_ganar * 1000) / ganancia_diaria_ajustada  # Convertir kg a g
    else:
        dias_estimados = 999  # Valor alto si no hay ganancia
    
    return max(1, dias_estimados)

def calcular_ganancia_base_por_edad(edad_dias):
    """
    Calcula ganancia de peso base según edad (valores típicos)
    
    Args:
        edad_dias: Edad en días
        
    Returns:
        Ganancia diaria base en gramos
    """
    if edad_dias <= 7:
        return 15  # g/día
    elif edad_dias <= 14:
        return 35  # g/día
    elif edad_dias <= 21:
        return 55  # g/día
    elif edad_dias <= 28:
        return 70  # g/día
    elif edad_dias <= 35:
        return 80  # g/día
    else:
        return 85  # g/día

def proyectar_curva_crecimiento(individuo, peso_inicial, edad_inicial, dias_proyeccion, 
                               raza, ingredientes_data):
    """
    Proyecta la curva de crecimiento con la formulación propuesta
    
    Args:
        individuo: Objeto individuo con porcentajes
        peso_inicial: Peso inicial en kg
        edad_inicial: Edad inicial en días
        dias_proyeccion: Días a proyectar
        raza: Nombre de la raza
        ingredientes_data: Lista de datos de ingredientes
        
    Returns:
        Lista con proyección día a día
    """
    proyeccion = []
    peso_actual = peso_inicial
    
    for dia in range(dias_proyeccion + 1):
        edad_dia = edad_inicial + dia
        
        if dia == 0:
            # Día inicial
            ganancia_g = 0
        else:
            # Calcular ganancia para este día
            ganancia_g = calcular_ganancia_diaria(individuo, raza, edad_dia, ingredientes_data)
            peso_actual += ganancia_g / 1000  # Convertir g a kg
        
        proyeccion.append({
            "dia": dia,
            "edad": edad_dia,
            "peso_kg": peso_actual,
            "ganancia_diaria_g": ganancia_g
        })
    
    return proyeccion

def calcular_eficiencia_temporal(individuo, peso_actual, peso_objetivo, raza, edad_dias, ingredientes_data):
    """
    Calcula la eficiencia temporal de la formulación
    
    Args:
        individuo: Objeto individuo con porcentajes
        peso_actual: Peso actual en kg
        peso_objetivo: Peso objetivo en kg
        raza: Nombre de la raza
        edad_dias: Edad actual en días
        ingredientes_data: Lista de datos de ingredientes
        
    Returns:
        Diccionario con métricas de eficiencia temporal
    """
    dias_estimados = estimar_tiempo_peso_objetivo(individuo, peso_actual, peso_objetivo, 
                                                raza, edad_dias, ingredientes_data)
    
    # Calcular métricas
    peso_a_ganar = peso_objetivo - peso_actual
    ganancia_diaria_promedio = (peso_a_ganar * 1000) / dias_estimados if dias_estimados > 0 else 0
    
    # Comparar con estándar de la raza
    dias_baseline = estimar_dias_hasta_peso(peso_actual, peso_objetivo, raza, edad_dias)
    ventaja_temporal = 0
    
    if dias_baseline:
        ventaja_temporal = dias_baseline - dias_estimados
        eficiencia_relativa = (dias_baseline / dias_estimados) if dias_estimados > 0 else 0
    else:
        eficiencia_relativa = 1.0
    
    return {
        "dias_estimados": dias_estimados,
        "dias_baseline": dias_baseline,
        "ventaja_temporal": ventaja_temporal,
        "eficiencia_relativa": eficiencia_relativa,
        "ganancia_diaria_promedio": ganancia_diaria_promedio,
        "peso_a_ganar": peso_a_ganar
    }

def optimizar_tiempo_vs_costo(individuos, peso_actual, peso_objetivo, raza, edad_dias, ingredientes_data):
    """
    Analiza el balance tiempo vs costo para múltiples formulaciones
    
    Args:
        individuos: Lista de individuos a analizar
        peso_actual: Peso actual en kg
        peso_objetivo: Peso objetivo en kg
        raza: Nombre de la raza
        edad_dias: Edad actual en días
        ingredientes_data: Lista de datos de ingredientes
        
    Returns:
        Lista de análisis ordenada por eficiencia global
    """
    analisis = []
    
    for i, individuo in enumerate(individuos):
        # Calcular métricas temporales
        dias = estimar_tiempo_peso_objetivo(individuo, peso_actual, peso_objetivo, 
                                          raza, edad_dias, ingredientes_data)
        
        # Calcular costo total del período
        from genetic.fitness.costo import calcular_costo_total_produccion
        costo_info = calcular_costo_total_produccion(individuo, 1, peso_actual, peso_objetivo, 
                                                   raza, edad_dias)
        
        if "error" not in costo_info:
            costo_total_periodo = costo_info["costo_por_pollo"]
            
            # Calcular eficiencia global (considerando tiempo y costo)
            if dias > 0:
                eficiencia_global = (peso_objetivo - peso_actual) / (dias * costo_info["costo_por_kg"])
            else:
                eficiencia_global = 0
            
            analisis.append({
                "individuo_id": i,
                "dias_estimados": dias,
                "costo_por_kg": individuo.costo_total,
                "costo_total_periodo": costo_total_periodo,
                "eficiencia_global": eficiencia_global,
                "fitness": individuo.fitness
            })
    
    # Ordenar por eficiencia global descendente
    analisis.sort(key=lambda x: x["eficiencia_global"], reverse=True)
    
    return analisis