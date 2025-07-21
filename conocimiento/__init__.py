"""
Paquete de base de conocimiento para optimización de alimentos para pollos.

Este paquete contiene todos los datos del dominio específico:
ingredientes, requerimientos nutricionales, razas y proveedores.
"""

from .ingredientes import INGREDIENTES
from .requerimientos import REQUERIMIENTOS_NUTRICIONALES, obtener_requerimientos, obtener_etapa
from .razas import RAZAS_POLLOS, obtener_raza, obtener_peso_esperado, obtener_conversion_alimenticia, estimar_dias_hasta_peso
from .proveedores import PROVEEDORES, obtener_proveedor, obtener_proveedor_mas_economico, calcular_costo_total_con_proveedor
from .restricciones_usuario import RestriccionesUsuario

__all__ = [
    # Datos principales
    'INGREDIENTES',
    'REQUERIMIENTOS_NUTRICIONALES', 
    'RAZAS_POLLOS',
    'PROVEEDORES',
    
    # Funciones de acceso a requerimientos
    'obtener_requerimientos',
    'obtener_etapa',
    
    # Funciones de acceso a razas
    'obtener_raza',
    'obtener_peso_esperado',
    'obtener_conversion_alimenticia',
    'estimar_dias_hasta_peso',
    
    # Funciones de acceso a proveedores
    'obtener_proveedor',
    'obtener_proveedor_mas_economico',
    'calcular_costo_total_con_proveedor',
    
    # Restricciones de usuario
    'RestriccionesUsuario'
]

def cargar_base_conocimiento():
    """
    Carga y valida toda la base de conocimiento
    
    Returns:
        Diccionario con todos los datos de conocimiento
    """
    return {
        "ingredientes": INGREDIENTES,
        "requerimientos": REQUERIMIENTOS_NUTRICIONALES,
        "razas": RAZAS_POLLOS,
        "proveedores": PROVEEDORES
    }

def validar_consistencia_datos():
    """
    Valida la consistencia de los datos de conocimiento
    
    Returns:
        Tupla (es_valido, lista_errores)
    """
    errores = []
    
    # Validar que hay ingredientes
    if not INGREDIENTES:
        errores.append("No hay ingredientes definidos")
    
    # Validar estructura de ingredientes
    for i, ingrediente in enumerate(INGREDIENTES):
        if "nombre" not in ingrediente:
            errores.append(f"Ingrediente {i} sin nombre")
        
        if "nutrientes" not in ingrediente:
            errores.append(f"Ingrediente {i} sin información nutricional")
        
        if "precios" not in ingrediente:
            errores.append(f"Ingrediente {i} sin información de precios")
        
        if "limitaciones" not in ingrediente:
            errores.append(f"Ingrediente {i} sin limitaciones definidas")
    
    # Validar que hay requerimientos nutricionales
    if not REQUERIMIENTOS_NUTRICIONALES:
        errores.append("No hay requerimientos nutricionales definidos")
    
    etapas_requeridas = ["iniciacion", "crecimiento", "finalizacion"]
    for etapa in etapas_requeridas:
        if etapa not in REQUERIMIENTOS_NUTRICIONALES:
            errores.append(f"Falta etapa '{etapa}' en requerimientos nutricionales")
    
    # Validar que hay razas
    if not RAZAS_POLLOS:
        errores.append("No hay razas de pollos definidas")
    
    # Validar que hay proveedores
    if not PROVEEDORES:
        errores.append("No hay proveedores definidos")
    
    return len(errores) == 0, errores

def obtener_resumen_conocimiento():
    """
    Obtiene un resumen de la base de conocimiento
    
    Returns:
        Diccionario con resumen
    """
    resumen = {
        "ingredientes": {
            "total": len(INGREDIENTES),
            "nombres": [ing["nombre"] for ing in INGREDIENTES]
        },
        "requerimientos": {
            "etapas": list(REQUERIMIENTOS_NUTRICIONALES.keys()),
            "nutrientes": list(REQUERIMIENTOS_NUTRICIONALES["iniciacion"].keys()) if REQUERIMIENTOS_NUTRICIONALES else []
        },
        "razas": {
            "total": len(RAZAS_POLLOS),
            "nombres": [raza["nombre"] for raza in RAZAS_POLLOS]
        },
        "proveedores": {
            "total": len(PROVEEDORES),
            "nombres": [prov["nombre"] for prov in PROVEEDORES]
        }
    }
    
    return resumen

def buscar_ingrediente_por_nombre(nombre):
    """
    Busca un ingrediente por su nombre
    
    Args:
        nombre: Nombre del ingrediente a buscar
        
    Returns:
        Ingrediente encontrado o None
    """
    nombre_lower = nombre.lower()
    for ingrediente in INGREDIENTES:
        if ingrediente["nombre"].lower() == nombre_lower:
            return ingrediente
    return None

def obtener_ingredientes_por_categoria():
    """
    Agrupa ingredientes por categoría nutricional
    
    Returns:
        Diccionario con ingredientes agrupados
    """
    categorias = {
        "cereales": [],
        "proteinas": [], 
        "minerales": [],
        "otros": []
    }
    
    for i, ingrediente in enumerate(INGREDIENTES):
        nombre = ingrediente["nombre"].lower()
        nutrientes = ingrediente.get("nutrientes", {})
        proteina = nutrientes.get("proteina", 0)
        
        if any(cereal in nombre for cereal in ["maíz", "sorgo", "trigo"]):
            categorias["cereales"].append((i, ingrediente))
        elif proteina > 0.25:  # Más del 25% de proteína
            categorias["proteinas"].append((i, ingrediente))
        elif any(mineral in nombre for mineral in ["mineral", "premezcla", "vitamina"]):
            categorias["minerales"].append((i, ingrediente))
        else:
            categorias["otros"].append((i, ingrediente))
    
    return categorias

# Ejecutar validación al importar
_es_valido, _errores = validar_consistencia_datos()
if not _es_valido:
    import warnings
    warnings.warn(f"Problemas en base de conocimiento: {'; '.join(_errores)}")

# Información del paquete
__version__ = "1.0.0"
__author__ = "Sistema boilerNutri"
__description__ = "Base de conocimiento para formulación de alimentos para pollos"