"""
Función objetivo: Disponibilidad local.

Evalúa qué tan fácil es obtener los ingredientes
de la formulación en proveedores locales.
"""

from conocimiento.proveedores import obtener_proveedor

def calcular_disponibilidad_local(individuo, ingredientes_data):
    """
    Calcula un factor que representa la dificultad de obtener
    los ingredientes localmente.
    
    Esta función debe ser MINIMIZADA porque:
    - Un valor bajo indica que los ingredientes son fácilmente disponibles en la localidad
    - Minimizar este valor reduce riesgos de desabastecimiento
    - Facilita la implementación práctica de la fórmula
    
    Args:
        individuo: Objeto individuo con porcentajes
        ingredientes_data: Lista de datos de ingredientes
        
    Returns:
        Factor de dificultad de obtención (menor es mejor)
    """
    factor_disponibilidad = 0
    peso_total = 0
    
    for i, porcentaje in enumerate(individuo.porcentajes):
        if porcentaje > 0 and i < len(ingredientes_data):
            ingrediente = ingredientes_data[i]
            disponibilidad = ingrediente.get("disponibilidadLocal", 0.5)
            
            # Inverso de la disponibilidad (1 - disponibilidad)
            # Mayor porcentaje de ingredientes poco disponibles aumenta este factor
            dificultad = 1 - disponibilidad
            factor_disponibilidad += porcentaje * dificultad
            peso_total += porcentaje
    
    # Normalizar por el peso total (debería ser 1, pero por seguridad)
    if peso_total > 0:
        factor_disponibilidad /= peso_total
    
    # Almacenar en el individuo
    individuo.disponibilidad_score = factor_disponibilidad
    
    return factor_disponibilidad

def evaluar_disponibilidad_ingrediente(ingrediente_id, ingredientes_data):
    """
    Evalúa la disponibilidad local de un ingrediente específico
    
    Args:
        ingrediente_id: ID del ingrediente
        ingredientes_data: Lista de datos de ingredientes
        
    Returns:
        Diccionario con información de disponibilidad
    """
    if ingrediente_id >= len(ingredientes_data):
        return None
    
    ingrediente = ingredientes_data[ingrediente_id]
    disponibilidad = ingrediente.get("disponibilidadLocal", 0.5)
    
    # Clasificar disponibilidad
    if disponibilidad >= 0.9:
        clasificacion = "Excelente"
        riesgo = "Muy bajo"
    elif disponibilidad >= 0.7:
        clasificacion = "Buena"
        riesgo = "Bajo"
    elif disponibilidad >= 0.5:
        clasificacion = "Regular"
        riesgo = "Medio"
    elif disponibilidad >= 0.3:
        clasificacion = "Limitada"
        riesgo = "Alto"
    else:
        clasificacion = "Escasa"
        riesgo = "Muy alto"
    
    return {
        "ingrediente": ingrediente["nombre"],
        "disponibilidad": disponibilidad,
        "clasificacion": clasificacion,
        "riesgo_desabastecimiento": riesgo,
        "proveedores_disponibles": len(ingrediente.get("precios", {}))
    }

def calcular_diversidad_proveedores(individuo, ingredientes_data):
    """
    Calcula la diversidad de proveedores en la formulación
    
    Args:
        individuo: Objeto individuo con porcentajes
        ingredientes_data: Lista de datos de ingredientes
        
    Returns:
        Diccionario con análisis de diversidad de proveedores
    """
    proveedores_utilizados = set()
    distribucion_proveedores = {}
    
    for i, porcentaje in enumerate(individuo.porcentajes):
        if porcentaje > 0.001 and i < len(ingredientes_data):  # Más de 0.1%
            ingrediente = ingredientes_data[i]
            
            # Encontrar el proveedor más económico para este ingrediente
            precios = ingrediente.get("precios", {})
            if precios:
                proveedor_economico = min(precios, key=precios.get)
                proveedores_utilizados.add(proveedor_economico)
                
                if proveedor_economico not in distribucion_proveedores:
                    distribucion_proveedores[proveedor_economico] = 0
                distribucion_proveedores[proveedor_economico] += porcentaje
    
    # Calcular índice de diversidad (Índice de Shannon simplificado)
    diversidad = 0
    if len(proveedores_utilizados) > 1:
        for proveedor, proporcion in distribucion_proveedores.items():
            if proporcion > 0:
                diversidad -= proporcion * (proporcion ** 0.5)  # Simplificado
    
    return {
        "num_proveedores": len(proveedores_utilizados),
        "proveedores_utilizados": list(proveedores_utilizados),
        "distribucion": distribucion_proveedores,
        "indice_diversidad": diversidad,
        "concentracion_riesgo": "Alta" if len(proveedores_utilizados) <= 1 else 
                               "Media" if len(proveedores_utilizados) == 2 else "Baja"
    }

def evaluar_riesgo_suministro(individuo, ingredientes_data):
    """
    Evalúa el riesgo general de suministro de la formulación
    
    Args:
        individuo: Objeto individuo con porcentajes
        ingredientes_data: Lista de datos de ingredientes
        
    Returns:
        Diccionario con evaluación de riesgo
    """
    riesgos = {
        "ingredientes_criticos": [],
        "concentracion_proveedor": 0,
        "disponibilidad_promedio": 0,
        "riesgo_general": "Bajo"
    }
    
    peso_total = 0
    disponibilidad_ponderada = 0
    
    # Evaluar cada ingrediente
    for i, porcentaje in enumerate(individuo.porcentajes):
        if porcentaje > 0.001 and i < len(ingredientes_data):
            ingrediente = ingredientes_data[i]
            disponibilidad = ingrediente.get("disponibilidadLocal", 0.5)
            
            disponibilidad_ponderada += porcentaje * disponibilidad
            peso_total += porcentaje
            
            # Identificar ingredientes críticos (alta participación, baja disponibilidad)
            if porcentaje > 0.1 and disponibilidad < 0.6:  # >10% y <60% disponibilidad
                riesgos["ingredientes_criticos"].append({
                    "ingrediente": ingrediente["nombre"],
                    "porcentaje": porcentaje * 100,
                    "disponibilidad": disponibilidad,
                    "riesgo": "Alto" if disponibilidad < 0.4 else "Medio"
                })
    
    # Calcular disponibilidad promedio ponderada
    if peso_total > 0:
        riesgos["disponibilidad_promedio"] = disponibilidad_ponderada / peso_total
    
    # Evaluar concentración de proveedores
    diversidad_info = calcular_diversidad_proveedores(individuo, ingredientes_data)
    riesgos["concentracion_proveedor"] = diversidad_info["num_proveedores"]
    
    # Determinar riesgo general
    if len(riesgos["ingredientes_criticos"]) > 2 or riesgos["disponibilidad_promedio"] < 0.6:
        riesgos["riesgo_general"] = "Alto"
    elif len(riesgos["ingredientes_criticos"]) > 0 or riesgos["disponibilidad_promedio"] < 0.8:
        riesgos["riesgo_general"] = "Medio"
    else:
        riesgos["riesgo_general"] = "Bajo"
    
    return riesgos

def calcular_factor_estacionalidad(individiente_data, mes_actual=None):
    """
    Calcula un factor de ajuste por estacionalidad (futuro)
    
    Args:
        ingrediente_data: Datos del ingrediente
        mes_actual: Mes actual (1-12), opcional
        
    Returns:
        Factor de ajuste por estacionalidad
    """
    # Placeholder para funcionalidad futura
    # Podría incluir variaciones estacionales de disponibilidad
    # Por ejemplo: maíz más disponible en época de cosecha
    
    factores_estacionales = {
        "Maíz": {1: 1.0, 2: 1.0, 3: 1.1, 4: 1.1, 5: 1.2, 6: 1.2,
                7: 0.9, 8: 0.8, 9: 0.8, 10: 0.9, 11: 1.0, 12: 1.0},
        "Sorgo": {1: 1.0, 2: 1.0, 3: 1.1, 4: 1.1, 5: 1.2, 6: 1.2,
                 7: 0.9, 8: 0.8, 9: 0.8, 10: 0.9, 11: 1.0, 12: 1.0}
    }
    
    if mes_actual and "nombre" in ingrediente_data:
        nombre = ingrediente_data["nombre"]
        if nombre in factores_estacionales:
            return factores_estacionales[nombre].get(mes_actual, 1.0)
    
    return 1.0  # Sin ajuste por defecto

def generar_recomendaciones_suministro(individuo, ingredientes_data):
    """
    Genera recomendaciones para mejorar la seguridad de suministro
    
    Args:
        individuo: Objeto individuo con porcentajes
        ingredientes_data: Lista de datos de ingredientes
        
    Returns:
        Lista de recomendaciones
    """
    recomendaciones = []
    riesgo_info = evaluar_riesgo_suministro(individuo, ingredientes_data)
    
    # Recomendaciones por ingredientes críticos
    for ingrediente_critico in riesgo_info["ingredientes_criticos"]:
        nombre = ingrediente_critico["ingrediente"]
        recomendaciones.append(
            f"• Considerar proveedores alternativos para {nombre} "
            f"({ingrediente_critico['porcentaje']:.1f}% de la fórmula)"
        )
        
        if ingrediente_critico["riesgo"] == "Alto":
            recomendaciones.append(
                f"• Evaluar sustitutos para {nombre} debido al alto riesgo de desabastecimiento"
            )
    
    # Recomendaciones por concentración de proveedores
    if riesgo_info["concentracion_proveedor"] <= 1:
        recomendaciones.append(
            "• Diversificar proveedores para reducir dependencia de un solo proveedor"
        )
    elif riesgo_info["concentracion_proveedor"] == 2:
        recomendaciones.append(
            "• Considerar un tercer proveedor para mayor seguridad de suministro"
        )
    
    # Recomendaciones por disponibilidad general
    if riesgo_info["disponibilidad_promedio"] < 0.7:
        recomendaciones.append(
            "• Priorizar ingredientes con mayor disponibilidad local"
        )
        recomendaciones.append(
            "• Establecer contratos de suministro para ingredientes críticos"
        )
    
    if not recomendaciones:
        recomendaciones.append("• La formulación presenta bajo riesgo de suministro")
    
    return recomendaciones