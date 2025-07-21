"""
Función objetivo: Discrepancia nutricional.

Evalúa qué tan cerca está la formulación de cumplir
los requerimientos nutricionales de referencia.
"""

from conocimiento.requerimientos import REQUERIMIENTOS_NUTRICIONALES

def calcular_propiedades_nutricionales(individuo, ingredientes_data):
    """
    Calcula las propiedades nutricionales de una formulación
    
    Args:
        individuo: Objeto individuo con porcentajes
        ingredientes_data: Lista de datos de ingredientes
        
    Returns:
        Diccionario con propiedades nutricionales calculadas
    """
    # Inicializar propiedades con ceros
    propiedades = {
        "proteina": 0,
        "energia": 0,
        "lisina": 0,
        "metionina": 0,
        "calcio": 0,
        "fosforo": 0,
        "fibra": 0
    }
    
    # Calcular aporte de cada ingrediente
    for i in range(min(len(individuo.porcentajes), len(ingredientes_data))):
        porcentaje = individuo.porcentajes[i]
        if porcentaje > 0:
            ingrediente = ingredientes_data[i]
            for nutriente, valor in ingrediente["nutrientes"].items():
                if nutriente in propiedades:
                    propiedades[nutriente] += porcentaje * valor
    
    # Actualizar las propiedades del individuo
    individuo.propiedades_nutricionales = propiedades
    return propiedades

def calcular_discrepancia_nutricional(individuo, etapa, ingredientes_data):
    """
    Calcula la discrepancia entre el perfil nutricional obtenido
    y los requerimientos de referencia.
    
    Esta función debe ser MINIMIZADA porque:
    - Un valor bajo indica que la fórmula se acerca más a los requerimientos nutricionales ideales
    - Cero sería una coincidencia perfecta con los requerimientos
    - Valores altos indican mayores desviaciones que podrían afectar el rendimiento de las aves
    
    Args:
        individuo: Objeto individuo con porcentajes
        etapa: Etapa de crecimiento ("iniciacion", "crecimiento", "finalizacion")
        ingredientes_data: Lista de datos de ingredientes
        
    Returns:
        Valor de discrepancia nutricional (menor es mejor)
    """
    # Calcular propiedades nutricionales primero
    calcular_propiedades_nutricionales(individuo, ingredientes_data)
    
    discrepancia_total = 0
    num_nutrientes = 0
    requerimientos = REQUERIMIENTOS_NUTRICIONALES.get(etapa, {})
    
    if not requerimientos:
        return 100  # Penalización alta si no hay requerimientos definidos
    
    for nutriente, valor_referencia in requerimientos.items():
        if nutriente in individuo.propiedades_nutricionales:
            valor_obtenido = individuo.propiedades_nutricionales[nutriente]
            
            # Diferentes tipos de nutrientes tienen diferentes modos de evaluación
            if nutriente == "fibra":
                # Para fibra, solo penalizar si excede el máximo
                if valor_obtenido > valor_referencia:
                    discrepancia = (valor_obtenido - valor_referencia) / valor_referencia
                    discrepancia_total += discrepancia ** 2  # Penalización cuadrática para excesos grandes
                else:
                    discrepancia = 0
                    
            elif nutriente == "energia":
                # Para energía, permitir un rango de ±3%
                if valor_obtenido < valor_referencia * 0.97:
                    discrepancia = (valor_referencia * 0.97 - valor_obtenido) / valor_referencia
                elif valor_obtenido > valor_referencia * 1.03:
                    discrepancia = (valor_obtenido - valor_referencia * 1.03) / valor_referencia
                else:
                    discrepancia = 0
                    
            else:
                # Para proteínas y aminoácidos, penalizar más el déficit que el exceso
                if valor_obtenido < valor_referencia:
                    # Déficit: penalización mayor (factor 1.5)
                    discrepancia = 1.5 * (valor_referencia - valor_obtenido) / valor_referencia
                elif valor_obtenido > valor_referencia * 1.1:  # Permitir hasta 10% de exceso
                    # Exceso moderado
                    discrepancia = (valor_obtenido - valor_referencia * 1.1) / valor_referencia
                else:
                    # Dentro del rango aceptable
                    discrepancia = 0
            
            discrepancia_total += discrepancia
            num_nutrientes += 1
    
    # Evitar división por cero
    if num_nutrientes == 0:
        return 100  # Penalización alta si no se evaluó ningún nutriente
    
    return discrepancia_total / num_nutrientes

def evaluar_balance_nutricional(individuo, etapa, ingredientes_data):
    """
    Evalúa el balance nutricional general de la formulación
    
    Args:
        individuo: Objeto individuo con porcentajes
        etapa: Etapa de crecimiento
        ingredientes_data: Lista de datos de ingredientes
        
    Returns:
        Diccionario con análisis detallado del balance nutricional
    """
    calcular_propiedades_nutricionales(individuo, ingredientes_data)
    
    requerimientos = REQUERIMIENTOS_NUTRICIONALES.get(etapa, {})
    analisis = {}
    
    for nutriente, valor_referencia in requerimientos.items():
        if nutriente in individuo.propiedades_nutricionales:
            valor_obtenido = individuo.propiedades_nutricionales[nutriente]
            
            # Calcular diferencia porcentual
            if valor_referencia != 0:
                diferencia_pct = ((valor_obtenido - valor_referencia) / valor_referencia) * 100
            else:
                diferencia_pct = 0
            
            # Determinar estado
            if nutriente == "fibra":
                if valor_obtenido <= valor_referencia:
                    estado = "Óptimo"
                elif valor_obtenido <= valor_referencia * 1.1:
                    estado = "Aceptable"
                else:
                    estado = "Excesivo"
            elif nutriente == "energia":
                if abs(diferencia_pct) <= 3:
                    estado = "Óptimo"
                elif abs(diferencia_pct) <= 7:
                    estado = "Aceptable"
                else:
                    estado = "Fuera de rango"
            else:
                if abs(diferencia_pct) <= 3:
                    estado = "Óptimo"
                elif abs(diferencia_pct) <= 10:
                    estado = "Aceptable"
                elif valor_obtenido < valor_referencia:
                    estado = "Deficiente"
                else:
                    estado = "Excesivo"
            
            analisis[nutriente] = {
                "valor_obtenido": valor_obtenido,
                "valor_referencia": valor_referencia,
                "diferencia_pct": diferencia_pct,
                "estado": estado
            }
    
    return analisis

def calcular_score_nutricional(individuo, etapa, ingredientes_data):
    """
    Calcula un score nutricional general (0-100, donde 100 es perfecto)
    
    Args:
        individuo: Objeto individuo con porcentajes
        etapa: Etapa de crecimiento
        ingredientes_data: Lista de datos de ingredientes
        
    Returns:
        Score nutricional entre 0 y 100
    """
    discrepancia = calcular_discrepancia_nutricional(individuo, etapa, ingredientes_data)
    
    # Convertir discrepancia a score (menor discrepancia = mayor score)
    # Usando función exponencial inversa para mapear discrepancia a score
    if discrepancia <= 0:
        return 100
    elif discrepancia >= 1:
        return 0
    else:
        # Mapeo exponencial: score = 100 * e^(-5 * discrepancia)
        import math
        return max(0, min(100, 100 * math.exp(-5 * discrepancia)))

def identificar_limitantes_nutricionales(individuo, etapa, ingredientes_data):
    """
    Identifica los nutrientes que están más lejos de los requerimientos
    
    Args:
        individuo: Objeto individuo con porcentajes
        etapa: Etapa de crecimiento
        ingredientes_data: Lista de datos de ingredientes
        
    Returns:
        Lista de nutrientes ordenados por severidad de la deficiencia/exceso
    """
    analisis = evaluar_balance_nutricional(individuo, etapa, ingredientes_data)
    
    limitantes = []
    for nutriente, info in analisis.items():
        if info["estado"] in ["Deficiente", "Excesivo", "Fuera de rango"]:
            severidad = abs(info["diferencia_pct"])
            limitantes.append({
                "nutriente": nutriente,
                "estado": info["estado"],
                "severidad": severidad,
                "diferencia_pct": info["diferencia_pct"]
            })
    
    # Ordenar por severidad (mayor primero)
    limitantes.sort(key=lambda x: x["severidad"], reverse=True)
    
    return limitantes