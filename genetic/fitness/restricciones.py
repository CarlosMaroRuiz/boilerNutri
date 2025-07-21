"""
Manejo de restricciones y penalizaciones.

Evalúa si la formulación cumple con todas las restricciones
y calcula penalizaciones para violaciones.
"""

def verificar_restricciones(individuo, ingredientes_data, restricciones_usuario=None):
    """
    Verifica si la formulación cumple con todas las restricciones.
    
    Esta función debe ser MINIMIZADA (0 = sin violaciones) porque:
    - Un valor de cero indica que se cumplen todas las restricciones
    - Valores positivos indican violaciones de restricciones que deben ser eliminadas
    - Las restricciones garantizan la seguridad y factibilidad de la formulación
    
    Args:
        individuo: Objeto individuo con porcentajes
        ingredientes_data: Lista de datos de ingredientes
        restricciones_usuario: Objeto con restricciones del usuario (opcional)
        
    Returns:
        Valor total de penalización por violaciones (0 = sin violaciones)
    """
    penalizacion_total = 0
    
    # 1. Verificar límites de ingredientes
    penalizacion_total += verificar_limites_ingredientes(individuo, ingredientes_data, restricciones_usuario)
    
    # 2. Verificar que la suma sea exactamente 1
    penalizacion_total += verificar_suma_porcentajes(individuo)
    
    # 3. Verificar ingredientes excluidos por el usuario
    if restricciones_usuario:
        penalizacion_total += verificar_exclusiones_usuario(individuo, ingredientes_data, restricciones_usuario)
    
    # 4. Verificar presupuesto máximo
    if restricciones_usuario and restricciones_usuario.presupuesto_maximo:
        penalizacion_total += verificar_presupuesto_maximo(individuo, restricciones_usuario)
    
    # 5. Verificar restricciones nutricionales críticas
    penalizacion_total += verificar_restricciones_nutricionales_criticas(individuo, ingredientes_data)
    
    # Almacenar en el individuo
    individuo.penalizacion_restricciones = penalizacion_total
    
    return penalizacion_total

def verificar_limites_ingredientes(individuo, ingredientes_data, restricciones_usuario=None):
    """
    Verifica los límites mínimos y máximos de cada ingrediente
    
    Args:
        individuo: Objeto individuo con porcentajes
        ingredientes_data: Lista de datos de ingredientes
        restricciones_usuario: Objeto con restricciones del usuario (opcional)
        
    Returns:
        Penalización por violación de límites
    """
    penalizacion = 0
    
    for i, porcentaje in enumerate(individuo.porcentajes):
        if i >= len(ingredientes_data):
            continue
        
        # Obtener límites efectivos
        limites_originales = ingredientes_data[i]["limitaciones"]
        if restricciones_usuario:
            limites = restricciones_usuario.obtener_limites(i, limites_originales)
        else:
            limites = limites_originales
        
        min_val = limites["min"]
        max_val = limites["max"]
        
        # Penalizar violaciones de límites
        if porcentaje < min_val:
            violacion = min_val - porcentaje
            penalizacion += 100 * violacion  # Penalización alta por déficit
        elif porcentaje > max_val:
            violacion = porcentaje - max_val
            penalizacion += 100 * violacion  # Penalización alta por exceso
    
    return penalizacion

def verificar_suma_porcentajes(individuo, tolerancia=1e-6):
    """
    Verifica que la suma de porcentajes sea exactamente 1
    
    Args:
        individuo: Objeto individuo con porcentajes
        tolerancia: Tolerancia para la verificación
        
    Returns:
        Penalización por suma incorrecta
    """
    suma = sum(individuo.porcentajes)
    desviacion = abs(suma - 1.0)
    
    if desviacion > tolerancia:
        return 1000 * desviacion  # Penalización muy alta para suma incorrecta
    
    return 0

def verificar_exclusiones_usuario(individuo, ingredientes_data, restricciones_usuario):
    """
    Verifica que no se usen ingredientes excluidos por el usuario
    
    Args:
        individuo: Objeto individuo con porcentajes
        ingredientes_data: Lista de datos de ingredientes
        restricciones_usuario: Objeto con restricciones del usuario
        
    Returns:
        Penalización por uso de ingredientes excluidos
    """
    penalizacion = 0
    
    for i, porcentaje in enumerate(individuo.porcentajes):
        if porcentaje > 1e-6:  # Ingrediente con uso significativo
            if not restricciones_usuario.es_ingrediente_valido(i):
                # Penalización severa por usar ingrediente excluido
                penalizacion += 500 * porcentaje
    
    return penalizacion

def verificar_presupuesto_maximo(individuo, restricciones_usuario):
    """
    Verifica que el costo no exceda el presupuesto máximo
    
    Args:
        individuo: Objeto individuo con porcentajes
        restricciones_usuario: Objeto con restricciones del usuario
        
    Returns:
        Penalización por exceso de presupuesto
    """
    if not hasattr(individuo, 'costo_total') or individuo.costo_total == 0:
        return 0
    
    presupuesto_maximo = restricciones_usuario.presupuesto_maximo
    exceso = individuo.costo_total - presupuesto_maximo
    
    if exceso > 0:
        # Penalización proporcional al exceso
        return 200 * (exceso / presupuesto_maximo)
    
    return 0

def verificar_restricciones_nutricionales_criticas(individuo, ingredientes_data):
    """
    Verifica restricciones nutricionales críticas para la salud animal
    
    Args:
        individuo: Objeto individuo con porcentajes
        ingredientes_data: Lista de datos de ingredientes
        
    Returns:
        Penalización por violaciones nutricionales críticas
    """
    from genetic.fitness.nutricion import calcular_propiedades_nutricionales
    
    # Asegurar que las propiedades estén calculadas
    if not hasattr(individuo, 'propiedades_nutricionales') or not individuo.propiedades_nutricionales:
        calcular_propiedades_nutricionales(individuo, ingredientes_data)
    
    penalizacion = 0
    
    # Restricción crítica: contenido mínimo de proteína
    proteina = individuo.propiedades_nutricionales.get("proteina", 0)
    if proteina < 0.15:  # Menos del 15% de proteína es crítico
        deficit = 0.15 - proteina
        penalizacion += 300 * deficit  # Penalización severa
    
    # Restricción crítica: contenido máximo de fibra
    fibra = individuo.propiedades_nutricionales.get("fibra", 0)
    if fibra > 0.08:  # Más del 8% de fibra es problemático
        exceso = fibra - 0.08
        penalizacion += 200 * exceso
    
    # Restricción crítica: energía mínima
    energia = individuo.propiedades_nutricionales.get("energia", 0)
    if energia < 2500:  # Menos de 2500 kcal/kg es insuficiente
        deficit = (2500 - energia) / 2500
        penalizacion += 250 * deficit
    
    # Restricción crítica: balance de calcio y fósforo
    calcio = individuo.propiedades_nutricionales.get("calcio", 0)
    fosforo = individuo.propiedades_nutricionales.get("fosforo", 0)
    
    if calcio > 0 and fosforo > 0:
        ratio_ca_p = calcio / fosforo
        if ratio_ca_p < 1.0 or ratio_ca_p > 3.0:  # Ratio fuera de rango seguro
            penalizacion += 150  # Penalización fija por desequilibrio
    
    return penalizacion

def calcular_penalizacion(tipo_violacion, magnitud, severidad="media"):
    """
    Calcula la penalización para una violación específica
    
    Args:
        tipo_violacion: Tipo de violación ("limite", "suma", "exclusion", etc.)
        magnitud: Magnitud de la violación
        severidad: Severidad de la violación ("baja", "media", "alta", "critica")
        
    Returns:
        Valor de penalización
    """
    # Factores base por tipo de violación
    factores_base = {
        "limite": 100,
        "suma": 1000,
        "exclusion": 500,
        "presupuesto": 200,
        "nutricional_critica": 300,
        "nutricional_menor": 50
    }
    
    # Multiplicadores por severidad
    multiplicadores_severidad = {
        "baja": 0.5,
        "media": 1.0,
        "alta": 2.0,
        "critica": 5.0
    }
    
    factor_base = factores_base.get(tipo_violacion, 100)
    multiplicador = multiplicadores_severidad.get(severidad, 1.0)
    
    return factor_base * magnitud * multiplicador

def es_formulacion_factible(individuo, ingredientes_data, restricciones_usuario=None, 
                           tolerancia_penalizacion=10):
    """
    Determina si una formulación es factible (penalización baja)
    
    Args:
        individuo: Objeto individuo con porcentajes
        ingredientes_data: Lista de datos de ingredientes
        restricciones_usuario: Objeto con restricciones del usuario (opcional)
        tolerancia_penalizacion: Penalización máxima tolerable
        
    Returns:
        True si la formulación es factible, False en caso contrario
    """
    penalizacion = verificar_restricciones(individuo, ingredientes_data, restricciones_usuario)
    return penalizacion <= tolerancia_penalizacion

def generar_reporte_violaciones(individuo, ingredientes_data, restricciones_usuario=None):
    """
    Genera un reporte detallado de todas las violaciones
    
    Args:
        individuo: Objeto individuo con porcentajes
        ingredientes_data: Lista de datos de ingredientes
        restricciones_usuario: Objeto con restricciones del usuario (opcional)
        
    Returns:
        Diccionario con reporte de violaciones
    """
    violaciones = {
        "limite_ingredientes": [],
        "suma_incorrecta": False,
        "ingredientes_excluidos": [],
        "presupuesto_excedido": False,
        "nutricionales_criticas": [],
        "penalizacion_total": 0
    }
    
    # Verificar límites de ingredientes
    for i, porcentaje in enumerate(individuo.porcentajes):
        if i >= len(ingredientes_data):
            continue
        
        limites_originales = ingredientes_data[i]["limitaciones"]
        if restricciones_usuario:
            limites = restricciones_usuario.obtener_limites(i, limites_originales)
        else:
            limites = limites_originales
        
        if porcentaje < limites["min"] or porcentaje > limites["max"]:
            violaciones["limite_ingredientes"].append({
                "ingrediente": ingredientes_data[i]["nombre"],
                "porcentaje_actual": porcentaje * 100,
                "min_permitido": limites["min"] * 100,
                "max_permitido": limites["max"] * 100
            })
    
    # Verificar suma de porcentajes
    suma = sum(individuo.porcentajes)
    if abs(suma - 1.0) > 1e-6:
        violaciones["suma_incorrecta"] = True
        violaciones["suma_actual"] = suma
    
    # Verificar ingredientes excluidos
    if restricciones_usuario:
        for i, porcentaje in enumerate(individuo.porcentajes):
            if porcentaje > 1e-6 and not restricciones_usuario.es_ingrediente_valido(i):
                if i < len(ingredientes_data):
                    violaciones["ingredientes_excluidos"].append({
                        "ingrediente": ingredientes_data[i]["nombre"],
                        "porcentaje": porcentaje * 100
                    })
    
    # Verificar presupuesto
    if (restricciones_usuario and restricciones_usuario.presupuesto_maximo and 
        hasattr(individuo, 'costo_total')):
        if individuo.costo_total > restricciones_usuario.presupuesto_maximo:
            violaciones["presupuesto_excedido"] = True
            violaciones["costo_actual"] = individuo.costo_total
            violaciones["presupuesto_maximo"] = restricciones_usuario.presupuesto_maximo
    
    # Calcular penalización total
    violaciones["penalizacion_total"] = verificar_restricciones(individuo, ingredientes_data, 
                                                              restricciones_usuario)
    
    return violaciones

def aplicar_reparacion_restricciones(individuo, ingredientes_data, restricciones_usuario=None):
    """
    Intenta reparar violaciones de restricciones en un individuo
    
    Args:
        individuo: Objeto individuo con porcentajes
        ingredientes_data: Lista de datos de ingredientes
        restricciones_usuario: Objeto con restricciones del usuario (opcional)
        
    Returns:
        True si se pudo reparar, False en caso contrario
    """
    # Aplicar límites de ingredientes
    individuo.aplicar_limites(ingredientes_data, restricciones_usuario)
    
    # Eliminar ingredientes excluidos
    if restricciones_usuario:
        for i in range(len(individuo.porcentajes)):
            if not restricciones_usuario.es_ingrediente_valido(i):
                individuo.porcentajes[i] = 0
    
    # Renormalizar
    individuo.normalizar(ingredientes_data, restricciones_usuario)
    
    # Verificar si la reparación fue exitosa
    penalizacion_final = verificar_restricciones(individuo, ingredientes_data, restricciones_usuario)
    
    return penalizacion_final < 10  # Tolerancia para reparación exitosa

def obtener_grado_factibilidad(individuo, ingredientes_data, restricciones_usuario=None):
    """
    Obtiene un grado de factibilidad (0-1, donde 1 es completamente factible)
    
    Args:
        individuo: Objeto individuo con porcentajes
        ingredientes_data: Lista de datos de ingredientes
        restricciones_usuario: Objeto con restricciones del usuario (opcional)
        
    Returns:
        Grado de factibilidad entre 0 y 1
    """
    penalizacion = verificar_restricciones(individuo, ingredientes_data, restricciones_usuario)
    
    # Mapear penalización a grado de factibilidad
    if penalizacion == 0:
        return 1.0
    elif penalizacion <= 10:
        return 0.9
    elif penalizacion <= 50:
        return 0.7
    elif penalizacion <= 100:
        return 0.5
    elif penalizacion <= 200:
        return 0.3
    else:
        return 0.0