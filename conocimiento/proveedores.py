"""
Información de proveedores locales de ingredientes.

Contiene datos de contacto, factores de precios
y disponibilidad de cada proveedor.
"""

# Proveedores locales
PROVEEDORES = [
    {
        "id": 1,
        "nombre": "Veterinaria Buenavista",
        "clave": "veterinaria_buenavista",
        "descripcion": "Proveedor local con buen inventario",
        "factor_precio": 1.02,  # 2% más caro que el precio base promedio
        "ubicacion": "Tuxtla Gutiérrez, Chiapas",
        "confiabilidad": 0.9,   # 90% de confiabilidad
        "tiempo_entrega": 2     # días
    },
    {
        "id": 2,
        "nombre": "Veterinaria Don Paco",
        "clave": "veterinaria_don_paco",
        "descripcion": "Mejor precio en general",
        "factor_precio": 0.98,  # 2% más barato que el precio base promedio
        "ubicacion": "Tuxtla Gutiérrez, Chiapas",
        "confiabilidad": 0.85,  # 85% de confiabilidad
        "tiempo_entrega": 1     # días
    },
    {
        "id": 3,
        "nombre": "Veterinaria Don Edilberto Albores Urbina",
        "clave": "veterinaria_don_edilberto",
        "descripcion": "Proveedor local con disponibilidad constante",
        "factor_precio": 1.00,  # Precio base promedio
        "ubicacion": "Tuxtla Gutiérrez, Chiapas",
        "confiabilidad": 0.95,  # 95% de confiabilidad
        "tiempo_entrega": 1     # días
    }
]

def obtener_proveedor(clave_proveedor):
    """
    Obtiene la información de un proveedor específico
    
    Args:
        clave_proveedor: Clave del proveedor (ej: "veterinaria_buenavista")
        
    Returns:
        Diccionario con información del proveedor o None si no se encuentra
    """
    for proveedor in PROVEEDORES:
        if proveedor["clave"] == clave_proveedor:
            return proveedor
    return None

def obtener_proveedor_mas_economico(precios):
    """
    Encuentra el proveedor más económico para un ingrediente
    
    Args:
        precios: Diccionario con precios por proveedor
        
    Returns:
        Tupla (clave_proveedor, precio_minimo)
    """
    if not precios:
        return None, None
    
    clave_minimo = min(precios, key=precios.get)
    precio_minimo = precios[clave_minimo]
    
    return clave_minimo, precio_minimo

def calcular_costo_total_con_proveedor(porcentajes_ingredientes, ingredientes_data):
    """
    Calcula el costo total optimizando la selección de proveedores
    
    Args:
        porcentajes_ingredientes: Lista de porcentajes de cada ingrediente
        ingredientes_data: Lista de datos de ingredientes
        
    Returns:
        Tupla (costo_total, proveedores_recomendados)
    """
    costo_total = 0
    proveedores_recomendados = {}
    
    for i, porcentaje in enumerate(porcentajes_ingredientes):
        if porcentaje > 0 and i < len(ingredientes_data):
            ingrediente = ingredientes_data[i]
            precios = ingrediente["precios"]
            
            # Encontrar el proveedor más económico
            clave_proveedor, precio_minimo = obtener_proveedor_mas_economico(precios)
            
            if clave_proveedor and precio_minimo:
                costo_total += porcentaje * precio_minimo
                proveedores_recomendados[i] = {
                    "proveedor": clave_proveedor,
                    "precio": precio_minimo,
                    "ingrediente": ingrediente["nombre"]
                }
    
    return costo_total, proveedores_recomendados

def generar_resumen_compras(proveedores_recomendados, cantidad_total_kg):
    """
    Genera un resumen de compras agrupado por proveedor
    
    Args:
        proveedores_recomendados: Diccionario con proveedores recomendados
        cantidad_total_kg: Cantidad total de alimento a producir en kg
        
    Returns:
        Diccionario con resumen de compras por proveedor
    """
    resumen_por_proveedor = {}
    
    for ingrediente_id, info in proveedores_recomendados.items():
        clave_proveedor = info["proveedor"]
        
        if clave_proveedor not in resumen_por_proveedor:
            proveedor_info = obtener_proveedor(clave_proveedor)
            resumen_por_proveedor[clave_proveedor] = {
                "nombre": proveedor_info["nombre"] if proveedor_info else clave_proveedor,
                "ingredientes": [],
                "costo_total": 0
            }
        
        cantidad_ingrediente = cantidad_total_kg * (info.get("porcentaje", 0) / 100)
        costo_ingrediente = cantidad_ingrediente * info["precio"]
        
        resumen_por_proveedor[clave_proveedor]["ingredientes"].append({
            "nombre": info["ingrediente"],
            "cantidad_kg": cantidad_ingrediente,
            "precio_unitario": info["precio"],
            "costo_total": costo_ingrediente
        })
        
        resumen_por_proveedor[clave_proveedor]["costo_total"] += costo_ingrediente
    
    return resumen_por_proveedor