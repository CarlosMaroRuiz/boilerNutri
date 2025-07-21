"""
Información de razas de pollos disponibles.

Contiene curvas de crecimiento, conversión alimenticia
y características específicas de cada raza.
"""

# Información de razas disponibles
RAZAS_POLLOS = [
    {
        "id": 1,
        "nombre": "Ross",
        "descripcion": "Raza con buenas ganancias en la región",
        "curvas_crecimiento": {
            "peso_inicial": 0.045,  # 45g al nacer
            "pesos_referencia": {
                # día: peso en kg
                7: 0.185,
                14: 0.465,
                21: 0.925,
                28: 1.480,
                35: 2.110,
                42: 2.690
            },
            "conversion_alimenticia": {
                # día: conversión (kg alimento/kg ganancia)
                7: 0.85,
                14: 1.10,
                21: 1.34,
                28: 1.49,
                35: 1.63,
                42: 1.76
            }
        }
    },
    {
        "id": 2,
        "nombre": "Cobb",
        "descripcion": "Segunda raza más común en la región",
        "curvas_crecimiento": {
            "peso_inicial": 0.042,  # 42g al nacer
            "pesos_referencia": {
                # día: peso en kg
                7: 0.179,
                14: 0.450,
                21: 0.915,
                28: 1.470,
                35: 2.100,
                42: 2.680
            },
            "conversion_alimenticia": {
                # día: conversión (kg alimento/kg ganancia)
                7: 0.86,
                14: 1.12,
                21: 1.35,
                28: 1.50,
                35: 1.64,
                42: 1.78
            }
        }
    }
]

def obtener_raza(nombre_raza):
    """
    Obtiene la información de una raza específica
    
    Args:
        nombre_raza: Nombre de la raza (ej: "Ross", "Cobb")
        
    Returns:
        Diccionario con información de la raza o None si no se encuentra
    """
    for raza in RAZAS_POLLOS:
        if raza["nombre"].lower() == nombre_raza.lower():
            return raza
    return None

def obtener_peso_esperado(nombre_raza, edad_dias):
    """
    Obtiene el peso esperado para una raza y edad específica
    
    Args:
        nombre_raza: Nombre de la raza
        edad_dias: Edad en días
        
    Returns:
        Peso esperado en kg o None si no se encuentra
    """
    raza = obtener_raza(nombre_raza)
    if not raza:
        return None
    
    pesos = raza["curvas_crecimiento"]["pesos_referencia"]
    
    # Buscar el día más cercano
    if edad_dias in pesos:
        return pesos[edad_dias]
    
    # Interpolación lineal si no existe el día exacto
    dias_disponibles = sorted(pesos.keys())
    
    if edad_dias < dias_disponibles[0]:
        return raza["curvas_crecimiento"]["peso_inicial"]
    
    if edad_dias > dias_disponibles[-1]:
        return pesos[dias_disponibles[-1]]
    
    # Encontrar los días que rodean la edad
    for i in range(len(dias_disponibles) - 1):
        if dias_disponibles[i] <= edad_dias <= dias_disponibles[i + 1]:
            dia_menor = dias_disponibles[i]
            dia_mayor = dias_disponibles[i + 1]
            peso_menor = pesos[dia_menor]
            peso_mayor = pesos[dia_mayor]
            
            # Interpolación lineal
            factor = (edad_dias - dia_menor) / (dia_mayor - dia_menor)
            return peso_menor + factor * (peso_mayor - peso_menor)
    
    return None

def obtener_conversion_alimenticia(nombre_raza, edad_dias):
    """
    Obtiene la conversión alimenticia esperada para una raza y edad específica
    
    Args:
        nombre_raza: Nombre de la raza
        edad_dias: Edad en días
        
    Returns:
        Conversión alimenticia o None si no se encuentra
    """
    raza = obtener_raza(nombre_raza)
    if not raza:
        return None
    
    conversiones = raza["curvas_crecimiento"]["conversion_alimenticia"]
    
    # Buscar el día más cercano
    if edad_dias in conversiones:
        return conversiones[edad_dias]
    
    # Usar el día más cercano
    dias_disponibles = list(conversiones.keys())
    dia_mas_cercano = min(dias_disponibles, key=lambda x: abs(x - edad_dias))
    return conversiones[dia_mas_cercano]

def estimar_dias_hasta_peso(peso_actual, peso_objetivo, nombre_raza, edad_actual):
    """
    Estima los días necesarios para alcanzar un peso objetivo
    
    Args:
        peso_actual: Peso actual en kg
        peso_objetivo: Peso objetivo en kg
        nombre_raza: Nombre de la raza
        edad_actual: Edad actual en días
        
    Returns:
        Número estimado de días hasta alcanzar el peso objetivo
    """
    raza = obtener_raza(nombre_raza)
    if not raza:
        return None
    
    pesos = raza["curvas_crecimiento"]["pesos_referencia"]
    dias_disponibles = sorted(pesos.keys())
    
    # Buscar en qué día se alcanza el peso objetivo
    for dia in dias_disponibles:
        if pesos[dia] >= peso_objetivo:
            return max(0, dia - edad_actual)
    
    # Si no se encuentra en los datos, estimar basado en la tendencia
    # Usar los últimos dos puntos para proyectar
    if len(dias_disponibles) >= 2:
        ultimo_dia = dias_disponibles[-1]
        penultimo_dia = dias_disponibles[-2]
        ultimo_peso = pesos[ultimo_dia]
        penultimo_peso = pesos[penultimo_dia]
        
        if ultimo_peso >= peso_objetivo:
            return max(0, ultimo_dia - edad_actual)
        
        # Calcular tasa de crecimiento diaria
        tasa_crecimiento = (ultimo_peso - penultimo_peso) / (ultimo_dia - penultimo_dia)
        
        if tasa_crecimiento > 0:
            dias_adicionales = (peso_objetivo - ultimo_peso) / tasa_crecimiento
            return max(0, int(ultimo_dia + dias_adicionales - edad_actual))
    
    return None