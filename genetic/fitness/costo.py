"""
Función objetivo: Costo total.

Evalúa el costo por kilogramo de la formulación
considerando precios de diferentes proveedores.
"""

from conocimiento.proveedores import obtener_proveedor_mas_economico, obtener_proveedor

def calcular_costo_total(individuo, ingredientes_data, restricciones_usuario=None):
    """
    Calcula el costo total por kg y determina el proveedor
    más económico para cada ingrediente.
    
    Esta función debe ser MINIMIZADA porque:
    - Reducir el costo es uno de los objetivos principales del sistema
    - Un menor costo aumenta la rentabilidad de la operación
    - Minimizar el costo mientras se mantiene la calidad nutricional es el equilibrio óptimo
    
    Args:
        individuo: Objeto individuo con porcentajes
        ingredientes_data: Lista de datos de ingredientes
        restricciones_usuario: Objeto con restricciones del usuario (opcional)
        
    Returns:
        Costo total por kilogramo
    """
    costo_total = 0
    proveedor_recomendado = {}
    
    for i, porcentaje in enumerate(individuo.porcentajes):
        if porcentaje > 0 and i < len(ingredientes_data):
            ingrediente = ingredientes_data[i]
            precios = ingrediente["precios"]
            
            # Aplicar preferencias de proveedor si existen
            precios_ajustados = precios.copy()
            if restricciones_usuario and restricciones_usuario.preferencias_proveedor:
                for proveedor_clave, factor in restricciones_usuario.preferencias_proveedor.items():
                    if proveedor_clave in precios_ajustados:
                        precios_ajustados[proveedor_clave] *= factor
            
            # Encontrar el proveedor más económico
            proveedor_mas_economico, precio_minimo = obtener_proveedor_mas_economico(precios_ajustados)
            
            if proveedor_mas_economico and precio_minimo:
                # Si se aplicó factor de preferencia, usar el precio original
                precio_real = precios[proveedor_mas_economico]
                costo_total += porcentaje * precio_real
                
                # Guardar el proveedor recomendado
                proveedor_recomendado[i] = {
                    "proveedor": proveedor_mas_economico,
                    "precio": precio_real,
                    "ingrediente": ingrediente["nombre"],
                    "porcentaje": porcentaje * 100
                }
    
    # Actualizar propiedades del individuo
    individuo.costo_total = costo_total
    individuo.proveedor_recomendado = proveedor_recomendado
    
    return costo_total

def seleccionar_proveedor_optimo(ingrediente_id, ingredientes_data, restricciones_usuario=None):
    """
    Selecciona el proveedor más económico para un ingrediente específico
    
    Args:
        ingrediente_id: ID del ingrediente
        ingredientes_data: Lista de datos de ingredientes
        restricciones_usuario: Objeto con restricciones del usuario (opcional)
        
    Returns:
        Tupla (proveedor_clave, precio, nombre_proveedor)
    """
    if ingrediente_id >= len(ingredientes_data):
        return None, None, None
    
    ingrediente = ingredientes_data[ingrediente_id]
    precios = ingrediente["precios"]
    
    # Aplicar preferencias de proveedor si existen
    precios_ajustados = precios.copy()
    if restricciones_usuario and restricciones_usuario.preferencias_proveedor:
        for proveedor_clave, factor in restricciones_usuario.preferencias_proveedor.items():
            if proveedor_clave in precios_ajustados:
                precios_ajustados[proveedor_clave] *= factor
    
    # Encontrar el proveedor más económico
    proveedor_clave, _ = obtener_proveedor_mas_economico(precios_ajustados)
    
    if proveedor_clave:
        precio_real = precios[proveedor_clave]
        proveedor_info = obtener_proveedor(proveedor_clave)
        nombre_proveedor = proveedor_info["nombre"] if proveedor_info else proveedor_clave
        
        return proveedor_clave, precio_real, nombre_proveedor
    
    return None, None, None

def calcular_costo_por_ingrediente(individuo, ingredientes_data):
    """
    Calcula el costo desglosado por ingrediente
    
    Args:
        individuo: Objeto individuo con porcentajes
        ingredientes_data: Lista de datos de ingredientes
        
    Returns:
        Lista de diccionarios con costo por ingrediente
    """
    costos_por_ingrediente = []
    
    for i, porcentaje in enumerate(individuo.porcentajes):
        if porcentaje > 0.001 and i < len(ingredientes_data):  # Más de 0.1%
            ingrediente = ingredientes_data[i]
            proveedor_info = individuo.proveedor_recomendado.get(i, {})
            
            if proveedor_info:
                costo_por_kg = porcentaje * proveedor_info["precio"]
                costo_por_tonelada = costo_por_kg * 1000
                
                costos_por_ingrediente.append({
                    "ingrediente": ingrediente["nombre"],
                    "porcentaje": porcentaje * 100,
                    "precio_unitario": proveedor_info["precio"],
                    "proveedor": proveedor_info["proveedor"],
                    "costo_por_kg": costo_por_kg,
                    "costo_por_tonelada": costo_por_tonelada
                })
    
    # Ordenar por costo descendente
    costos_por_ingrediente.sort(key=lambda x: x["costo_por_kg"], reverse=True)
    
    return costos_por_ingrediente

def analizar_sensibilidad_precios(individuo, ingredientes_data, variacion_pct=10):
    """
    Analiza la sensibilidad del costo total ante variaciones en precios
    
    Args:
        individuo: Objeto individuo con porcentajes
        ingredientes_data: Lista de datos de ingredientes
        variacion_pct: Porcentaje de variación a analizar
        
    Returns:
        Diccionario con análisis de sensibilidad
    """
    costo_base = individuo.costo_total
    sensibilidad = {}
    
    for i, porcentaje in enumerate(individuo.porcentajes):
        if porcentaje > 0.001 and i < len(ingredientes_data):
            ingrediente = ingredientes_data[i]
            proveedor_info = individuo.proveedor_recomendado.get(i, {})
            
            if proveedor_info:
                precio_actual = proveedor_info["precio"]
                
                # Calcular impacto de aumento de precio
                precio_aumentado = precio_actual * (1 + variacion_pct / 100)
                impacto_aumento = porcentaje * (precio_aumentado - precio_actual)
                
                # Calcular impacto de reducción de precio
                precio_reducido = precio_actual * (1 - variacion_pct / 100)
                impacto_reduccion = porcentaje * (precio_actual - precio_reducido)
                
                sensibilidad[ingrediente["nombre"]] = {
                    "porcentaje_formulacion": porcentaje * 100,
                    "precio_actual": precio_actual,
                    "impacto_aumento": impacto_aumento,
                    "impacto_reduccion": impacto_reduccion,
                    "sensibilidad_relativa": (impacto_aumento / costo_base) * 100
                }
    
    # Ordenar por sensibilidad relativa (mayor impacto primero)
    sensibilidad_ordenada = dict(sorted(sensibilidad.items(), 
                                      key=lambda x: x[1]["sensibilidad_relativa"], 
                                      reverse=True))
    
    return sensibilidad_ordenada

def estimar_ahorro_vs_formula_tradicional(individuo, factor_comparacion=1.15):
    """
    Estima el ahorro respecto a una fórmula tradicional
    
    Args:
        individuo: Objeto individuo con porcentajes
        factor_comparacion: Factor de comparación (ej: 1.15 = 15% más cara)
        
    Returns:
        Diccionario con análisis de ahorro
    """
    costo_optimizado = individuo.costo_total
    costo_tradicional = costo_optimizado * factor_comparacion
    ahorro_absoluto = costo_tradicional - costo_optimizado
    ahorro_porcentual = (ahorro_absoluto / costo_tradicional) * 100
    
    return {
        "costo_optimizado": costo_optimizado,
        "costo_tradicional_estimado": costo_tradicional,
        "ahorro_absoluto": ahorro_absoluto,
        "ahorro_porcentual": ahorro_porcentual
    }

def calcular_costo_total_produccion(individuo, cantidad_pollos, peso_actual, peso_objetivo, 
                                  raza, edad_dias):
    """
    Calcula el costo total de alimentación para toda la producción
    
    Args:
        individuo: Objeto individuo con porcentajes
        cantidad_pollos: Número total de pollos
        peso_actual: Peso actual promedio en kg
        peso_objetivo: Peso objetivo en kg
        raza: Nombre de la raza
        edad_dias: Edad actual en días
        
    Returns:
        Diccionario con costos totales de producción
    """
    from conocimiento.razas import estimar_dias_hasta_peso
    
    # Estimar días hasta peso objetivo
    dias_hasta_objetivo = estimar_dias_hasta_peso(peso_actual, peso_objetivo, raza, edad_dias)
    
    if not dias_hasta_objetivo:
        return {"error": "No se pudo estimar el tiempo hasta peso objetivo"}
    
    # Estimar consumo diario por ave según edad (datos aproximados)
    consumo_total_kg = 0
    for dia_offset in range(dias_hasta_objetivo + 1):
        edad_dia = edad_dias + dia_offset
        
        if edad_dia <= 7:
            consumo_diario_g = 20
        elif edad_dia <= 14:
            consumo_diario_g = 45
        elif edad_dia <= 21:
            consumo_diario_g = 80
        elif edad_dia <= 28:
            consumo_diario_g = 115
        elif edad_dia <= 35:
            consumo_diario_g = 150
        else:
            consumo_diario_g = 180
        
        consumo_total_kg += (consumo_diario_g / 1000) * cantidad_pollos
    
    # Calcular costos
    costo_por_kg = individuo.costo_total
    costo_total_alimentacion = consumo_total_kg * costo_por_kg
    costo_por_pollo = costo_total_alimentacion / cantidad_pollos
    
    return {
        "dias_hasta_objetivo": dias_hasta_objetivo,
        "consumo_total_kg": consumo_total_kg,
        "consumo_promedio_por_pollo": consumo_total_kg / cantidad_pollos,
        "costo_por_kg": costo_por_kg,
        "costo_total_alimentacion": costo_total_alimentacion,
        "costo_por_pollo": costo_por_pollo
    }