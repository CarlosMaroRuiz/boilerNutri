"""
Función objetivo: Eficiencia alimenticia.

Estima la conversión alimenticia (kg alimento/kg ganancia)
basada en la calidad nutricional de la formulación.
"""

from conocimiento.razas import obtener_conversion_alimenticia
from genetic.fitness.nutricion import calcular_discrepancia_nutricional, obtener_etapa

def estimar_eficiencia_alimenticia(individuo, raza, edad_dias, ingredientes_data):
    """
    Estima la eficiencia de conversión alimenticia.
    
    Esta función debe ser MINIMIZADA porque:
    - Un valor bajo de conversión alimenticia significa que se necesita menos alimento para producir un kg de carne
    - Minimizar este valor reduce los costos de alimentación totales
    - Refleja directamente la eficiencia económica de la fórmula
    
    Args:
        individuo: Objeto individuo con porcentajes
        raza: Nombre de la raza
        edad_dias: Edad actual en días
        ingredientes_data: Lista de datos de ingredientes
        
    Returns:
        Conversión alimenticia estimada (kg alimento/kg ganancia)
    """
    # Obtener conversión base para la raza y edad
    conversion_base = obtener_conversion_base(raza, edad_dias)
    
    if conversion_base is None:
        return 2.0  # Valor por defecto alto si no se encuentra la raza
    
    # Determinar etapa según edad
    etapa = obtener_etapa(edad_dias)
    
    # Calcular discrepancia nutricional
    discrepancia = calcular_discrepancia_nutricional(individuo, etapa, ingredientes_data)
    
    # Ajustar según balance nutricional
    # Una formulación con balance perfecto mantiene la conversión base
    # Una mala formulación puede empeorar la conversión hasta en un 25%
    factor_ajuste = 1.0 + min(0.25, discrepancia * 1.5)
    
    # Considerar factores adicionales específicos
    factor_calidad = calcular_factor_calidad_nutricional(individuo, etapa, ingredientes_data)
    factor_digestibilidad = calcular_factor_digestibilidad(individuo, ingredientes_data)
    
    # Aplicar factores de ajuste
    conversion_ajustada = conversion_base * factor_ajuste * factor_calidad * factor_digestibilidad
    
    # Almacenar en el individuo
    individuo.conversion_alimenticia = conversion_ajustada
    
    return conversion_ajustada

def obtener_conversion_base(raza, edad_dias):
    """
    Obtiene la conversión alimenticia base para una raza y edad
    
    Args:
        raza: Nombre de la raza
        edad_dias: Edad en días
        
    Returns:
        Conversión alimenticia base o None si no se encuentra
    """
    return obtener_conversion_alimenticia(raza, edad_dias)

def calcular_factor_calidad_nutricional(individuo, etapa, ingredientes_data):
    """
    Calcula un factor de ajuste basado en la calidad nutricional
    
    Args:
        individuo: Objeto individuo con porcentajes
        etapa: Etapa de crecimiento
        ingredientes_data: Lista de datos de ingredientes
        
    Returns:
        Factor de ajuste (1.0 = neutro, >1.0 = empeora eficiencia)
    """
    from conocimiento.requerimientos import REQUERIMIENTOS_NUTRICIONALES
    
    if not hasattr(individuo, 'propiedades_nutricionales') or not individuo.propiedades_nutricionales:
        from genetic.fitness.nutricion import calcular_propiedades_nutricionales
        calcular_propiedades_nutricionales(individuo, ingredientes_data)
    
    requerimientos = REQUERIMIENTOS_NUTRICIONALES.get(etapa, {})
    factor = 1.0
    
    # Evaluar balance de aminoácidos esenciales
    aminoacidos = ["lisina", "metionina"]
    for aminoacido in aminoacidos:
        if aminoacido in requerimientos and aminoacido in individuo.propiedades_nutricionales:
            requerido = requerimientos[aminoacido]
            obtenido = individuo.propiedades_nutricionales[aminoacido]
            
            if obtenido < requerido * 0.95:  # Déficit significativo
                deficit = (requerido - obtenido) / requerido
                factor += deficit * 0.1  # Aumentar factor por déficit
    
    # Evaluar nivel de energía
    if "energia" in requerimientos and "energia" in individuo.propiedades_nutricionales:
        energia_requerida = requerimientos["energia"]
        energia_obtenida = individuo.propiedades_nutricionales["energia"]
        
        if energia_obtenida < energia_requerida * 0.95:
            deficit_energia = (energia_requerida - energia_obtenida) / energia_requerida
            factor += deficit_energia * 0.15  # Mayor impacto del déficit energético
        elif energia_obtenida > energia_requerida * 1.1:
            exceso_energia = (energia_obtenida - energia_requerida * 1.1) / energia_requerida
            factor += exceso_energia * 0.05  # Menor impacto del exceso energético
    
    return min(1.3, factor)  # Limitar el factor máximo

def calcular_factor_digestibilidad(individuo, ingredientes_data):
    """
    Calcula un factor basado en la digestibilidad de los ingredientes
    
    Args:
        individuo: Objeto individuo con porcentajes
        ingredientes_data: Lista de datos de ingredientes
        
    Returns:
        Factor de digestibilidad (1.0 = neutro, >1.0 = menor digestibilidad)
    """
    # Factores de digestibilidad por ingrediente (valores aproximados)
    factores_digestibilidad = {
        "Maíz": 0.92,
        "Pasta de Soya": 0.88,
        "DDG (Granos Secos de Destilería)": 0.75,  # Menor digestibilidad
        "Sorgo": 0.85,
        "Premezcla Micro/Macro Minerales Económica": 1.0,
        "Premezcla Micro/Macro Minerales Premium": 1.0
    }
    
    digestibilidad_promedio = 0
    peso_total = 0
    
    for i, porcentaje in enumerate(individuo.porcentajes):
        if porcentaje > 0 and i < len(ingredientes_data):
            nombre_ingrediente = ingredientes_data[i]["nombre"]
            factor = factores_digestibilidad.get(nombre_ingrediente, 0.85)  # Valor por defecto
            
            digestibilidad_promedio += porcentaje * factor
            peso_total += porcentaje
    
    if peso_total > 0:
        digestibilidad_promedio /= peso_total
    else:
        digestibilidad_promedio = 0.85
    
    # Convertir a factor de ajuste (mayor digestibilidad = menor factor)
    factor_ajuste = 1.0 + (0.90 - digestibilidad_promedio)  # Referencia: 90% digestibilidad óptima
    
    return max(1.0, min(1.2, factor_ajuste))

def calcular_factor_fibra(individuo, etapa, ingredientes_data):
    """
    Calcula un factor de penalización por exceso de fibra
    
    Args:
        individuo: Objeto individuo con porcentajes
        etapa: Etapa de crecimiento
        ingredientes_data: Lista de datos de ingredientes
        
    Returns:
        Factor de penalización por fibra (1.0 = óptimo, >1.0 = exceso de fibra)
    """
    from conocimiento.requerimientos import REQUERIMIENTOS_NUTRICIONALES
    
    if not hasattr(individuo, 'propiedades_nutricionales') or not individuo.propiedades_nutricionales:
        from genetic.fitness.nutricion import calcular_propiedades_nutricionales
        calcular_propiedades_nutricionales(individuo, ingredientes_data)
    
    requerimientos = REQUERIMIENTOS_NUTRICIONALES.get(etapa, {})
    
    if "fibra" not in requerimientos or "fibra" not in individuo.propiedades_nutricionales:
        return 1.0
    
    fibra_maxima = requerimientos["fibra"]
    fibra_obtenida = individuo.propiedades_nutricionales["fibra"]
    
    if fibra_obtenida <= fibra_maxima:
        return 1.0  # Dentro del límite aceptable
    
    # Penalizar exceso de fibra
    exceso_relativo = (fibra_obtenida - fibra_maxima) / fibra_maxima
    factor_penalizacion = 1.0 + exceso_relativo * 0.2  # 20% de penalización por exceso relativo
    
    return min(1.3, factor_penalizacion)  # Limitar penalización máxima

def estimar_ganancia_peso_diaria(individuo, raza, edad_dias, ingredientes_data):
    """
    Estima la ganancia de peso diaria basada en la eficiencia alimenticia
    
    Args:
        individuo: Objeto individuo con porcentajes
        raza: Nombre de la raza
        edad_dias: Edad actual en días
        ingredientes_data: Lista de datos de ingredientes
        
    Returns:
        Ganancia de peso diaria estimada en gramos
    """
    # Estimar consumo diario según edad
    if edad_dias <= 7:
        consumo_diario_g = 20
    elif edad_dias <= 14:
        consumo_diario_g = 45
    elif edad_dias <= 21:
        consumo_diario_g = 80
    elif edad_dias <= 28:
        consumo_diario_g = 115
    elif edad_dias <= 35:
        consumo_diario_g = 150
    else:
        consumo_diario_g = 180
    
    # Obtener conversión alimenticia
    conversion = estimar_eficiencia_alimenticia(individuo, raza, edad_dias, ingredientes_data)
    
    # Calcular ganancia diaria
    if conversion > 0:
        ganancia_diaria_g = consumo_diario_g / conversion
    else:
        ganancia_diaria_g = 0
    
    return ganancia_diaria_g

def proyectar_rendimiento_periodo(individuo, raza, edad_inicial, dias_periodo, ingredientes_data):
    """
    Proyecta el rendimiento durante un período específico
    
    Args:
        individuo: Objeto individuo con porcentajes
        raza: Nombre de la raza
        edad_inicial: Edad inicial en días
        dias_periodo: Duración del período en días
        ingredientes_data: Lista de datos de ingredientes
        
    Returns:
        Diccionario con proyección de rendimiento
    """
    proyeccion = {
        "consumo_total": 0,
        "ganancia_total": 0,
        "conversion_promedio": 0,
        "detalle_diario": []
    }
    
    conversiones_diarias = []
    
    for dia in range(dias_periodo):
        edad_dia = edad_inicial + dia
        
        # Estimar consumo diario
        if edad_dia <= 7:
            consumo_g = 20
        elif edad_dia <= 14:
            consumo_g = 45
        elif edad_dia <= 21:
            consumo_g = 80
        elif edad_dia <= 28:
            consumo_g = 115
        elif edad_dia <= 35:
            consumo_g = 150
        else:
            consumo_g = 180
        
        # Calcular conversión para esta edad
        conversion = estimar_eficiencia_alimenticia(individuo, raza, edad_dia, ingredientes_data)
        ganancia_g = consumo_g / conversion if conversion > 0 else 0
        
        proyeccion["consumo_total"] += consumo_g
        proyeccion["ganancia_total"] += ganancia_g
        conversiones_diarias.append(conversion)
        
        proyeccion["detalle_diario"].append({
            "dia": dia + 1,
            "edad": edad_dia,
            "consumo_g": consumo_g,
            "ganancia_g": ganancia_g,
            "conversion": conversion
        })
    
    # Calcular conversión promedio ponderada
    if proyeccion["ganancia_total"] > 0:
        proyeccion["conversion_promedio"] = proyeccion["consumo_total"] / proyeccion["ganancia_total"]
    else:
        proyeccion["conversion_promedio"] = max(conversiones_diarias) if conversiones_diarias else 2.0
    
    return proyeccion