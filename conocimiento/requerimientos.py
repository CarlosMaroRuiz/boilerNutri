"""
Requerimientos nutricionales para pollos según etapa de crecimiento.

Define los valores objetivo de nutrientes para cada fase:
iniciación, crecimiento y finalización.
"""

# Requerimientos nutricionales por etapa
REQUERIMIENTOS_NUTRICIONALES = {
    "iniciacion": {  # 1-10 días
        "proteina": 0.22,       # 22% de proteína
        "energia": 3000,        # 3000 kcal/kg
        "lisina": 0.0130,       # 1.30% de lisina
        "metionina": 0.0052,    # 0.52% de metionina
        "calcio": 0.0100,       # 1.00% de calcio
        "fosforo": 0.0050,      # 0.50% de fósforo disponible
        "fibra": 0.04           # Máximo 4% de fibra
    },
    "crecimiento": { # 11-24 días
        "proteina": 0.21,       # 21% de proteína
        "energia": 3050,        # 3050 kcal/kg
        "lisina": 0.0120,       # 1.20% de lisina
        "metionina": 0.0050,    # 0.50% de metionina
        "calcio": 0.0090,       # 0.90% de calcio
        "fosforo": 0.0045,      # 0.45% de fósforo disponible
        "fibra": 0.04           # Máximo 4% de fibra
    },
    "finalizacion": { # 25-42 días
        "proteina": 0.19,       # 19% de proteína
        "energia": 3100,        # 3100 kcal/kg
        "lisina": 0.0105,       # 1.05% de lisina
        "metionina": 0.0048,    # 0.48% de metionina
        "calcio": 0.0085,       # 0.85% de calcio
        "fosforo": 0.0042,      # 0.42% de fósforo disponible
        "fibra": 0.035          # Máximo 3.5% de fibra
    }
}

def obtener_requerimientos(edad_dias):
    """
    Obtiene los requerimientos nutricionales según la edad
    
    Args:
        edad_dias: Edad de los pollos en días
        
    Returns:
        Diccionario con requerimientos nutricionales
    """
    if edad_dias <= 10:
        return REQUERIMIENTOS_NUTRICIONALES["iniciacion"]
    elif edad_dias <= 24:
        return REQUERIMIENTOS_NUTRICIONALES["crecimiento"]
    else:
        return REQUERIMIENTOS_NUTRICIONALES["finalizacion"]

def obtener_etapa(edad_dias):
    """
    Determina la etapa de crecimiento según la edad
    
    Args:
        edad_dias: Edad de los pollos en días
        
    Returns:
        String con la etapa ("iniciacion", "crecimiento", "finalizacion")
    """
    if edad_dias <= 10:
        return "iniciacion"
    elif edad_dias <= 24:
        return "crecimiento"
    else:
        return "finalizacion"