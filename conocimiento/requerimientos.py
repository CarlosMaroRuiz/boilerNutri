"""
Requerimientos nutricionales para pollos según etapa de crecimiento.

Define los valores objetivo de nutrientes para cada fase:
iniciación, crecimiento y finalización.
"""

# Requerimientos nutricionales por etapa (CORREGIDOS)
REQUERIMIENTOS_NUTRICIONALES = {
    "iniciacion": {  # 1-21 días 
        "proteina": 0.22,       # 22% de proteína
        "energia": 3000,        # 3000 kcal/kg
        "lisina": 0.0130,       # 1.30% de lisina
        "metionina": 0.0052,    # 0.52% de metionina
        "calcio": 0.0100,       # 1.00% de calcio
        "fosforo": 0.0050,      # 0.50% de fósforo disponible
        "fibra": 0.04           # Máximo 4% de fibra
    },
    "crecimiento": { # 22-35 días 
        "proteina": 0.21,       # 21% de proteína
        "energia": 3050,        # 3050 kcal/kg
        "lisina": 0.0120,       # 1.20% de lisina
        "metionina": 0.0050,    # 0.50% de metionina
        "calcio": 0.0090,       # 0.90% de calcio
        "fosforo": 0.0045,      # 0.45% de fósforo disponible
        "fibra": 0.04           # Máximo 4% de fibra
    },
    "finalizacion": { # 36-42 días 
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
    if edad_dias <= 21:  # CORREGIDO: era <= 10
        return REQUERIMIENTOS_NUTRICIONALES["iniciacion"]
    elif edad_dias <= 35:  # CORREGIDO: era <= 24
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
    if edad_dias <= 21:  # CORREGIDO: era <= 10
        return "iniciacion"
    elif edad_dias <= 35:  # CORREGIDO: era <= 24
        return "crecimiento"
    else:
        return "finalizacion"

def validar_requerimientos():
    """
    Valida que los requerimientos nutricionales sean consistentes
    
    Returns:
        True si son válidos, False en caso contrario
    """
    for etapa, reqs in REQUERIMIENTOS_NUTRICIONALES.items():
        # Verificar que todos los nutrientes estén presentes
        nutrientes_esperados = ["proteina", "energia", "lisina", "metionina", "calcio", "fosforo", "fibra"]
        for nutriente in nutrientes_esperados:
            if nutriente not in reqs:
                print(f"⚠️ Falta nutriente '{nutriente}' en etapa '{etapa}'")
                return False
        
        # Verificar rangos lógicos
        if reqs["proteina"] < 0.15 or reqs["proteina"] > 0.25:
            print(f"⚠️ Proteína fuera de rango en etapa '{etapa}': {reqs['proteina']}")
            return False
            
        if reqs["energia"] < 2800 or reqs["energia"] > 3200:
            print(f"⚠️ Energía fuera de rango en etapa '{etapa}': {reqs['energia']}")
            return False
    
    print("✅ Requerimientos nutricionales validados correctamente")
    return True

def comparar_etapas():
    """
    Muestra una comparación de requerimientos entre etapas
    """
    print("\n📊 COMPARACIÓN DE REQUERIMIENTOS POR ETAPA:")
    print("=" * 60)
    
    nutrientes = ["proteina", "energia", "lisina", "metionina", "calcio", "fosforo", "fibra"]
    etapas = ["iniciacion", "crecimiento", "finalizacion"]
    
    # Encabezado
    print(f"{'Nutriente':<12} {'Iniciación':<12} {'Crecimiento':<12} {'Finalización':<12}")
    print("-" * 60)
    
    for nutriente in nutrientes:
        valores = []
        for etapa in etapas:
            valor = REQUERIMIENTOS_NUTRICIONALES[etapa][nutriente]
            if nutriente == "energia":
                valores.append(f"{valor:,.0f}")
            elif nutriente in ["proteina", "fibra"]:
                valores.append(f"{valor:.1%}")
            else:
                valores.append(f"{valor:.2%}")
        
        print(f"{nutriente.capitalize():<12} {valores[0]:<12} {valores[1]:<12} {valores[2]:<12}")

def obtener_rango_edad_etapa(etapa):
    """
    Obtiene el rango de días para una etapa específica
    
    Args:
        etapa: Nombre de la etapa
        
    Returns:
        Tuple con (día_inicio, día_fin)
    """
    rangos = {
        "iniciacion": (1, 21),
        "crecimiento": (22, 35),
        "finalizacion": (36, 42)
    }
    
    return rangos.get(etapa, (0, 0))

# Ejecutar validación al importar el módulo
if __name__ == "__main__":
    validar_requerimientos()
    comparar_etapas()