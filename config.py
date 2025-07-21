"""
Configuración global del proyecto boilerNutri.

Contiene parámetros del algoritmo genético, ponderaciones de objetivos,
y otras configuraciones del sistema.
"""

import os
from datetime import datetime

# Información del sistema
SISTEMA_INFO = {
    "nombre": "boilerNutri",
    "version": "1.0.0",
    "descripcion": "Sistema de optimización de formulaciones de alimentos para pollos",
    "autor": "Sistema boilerNutri",
    "fecha_version": "2024-07-20"
}

# Configuración del Algoritmo Genético
ALGORITMO_CONFIG = {
    "tamano_poblacion": 100,
    "num_generaciones": 200,
    "prob_cruza": 0.8,
    "prob_mutacion": 0.2,
    "intensidad_mutacion": 0.1,
    "tamano_torneo": 3,
    "elitismo": 5,
    "criterio_convergencia": {
        "ventana": 30,
        "tolerancia": 1e-6,
        "generaciones_minimas": 50
    }
}

# Ponderaciones de la función de fitness multiobjetivo
PESOS_FITNESS = {
    "discrepancia_nutricional": 0.35,
    "costo": 0.30,
    "eficiencia": 0.20,
    "disponibilidad": 0.10,
    "tiempo": 0.05
}

# Configuración de fases del algoritmo
FASES_CONFIG = {
    "inicial": {
        "inicio": 0.0,
        "fin": 0.3,
        "alpha_blx": 0.7,
        "intensidad_mutacion": 0.3,
        "tamano_torneo": 3,
        "descripcion": "Exploración amplia del espacio de soluciones"
    },
    "intermedia": {
        "inicio": 0.3,
        "fin": 0.7,
        "alpha_blx": 0.5,
        "intensidad_mutacion": 0.2,
        "tamano_torneo": 4,
        "descripcion": "Balance entre exploración y explotación"
    },
    "final": {
        "inicio": 0.7,
        "fin": 1.0,
        "alpha_blx": 0.3,
        "intensidad_mutacion": 0.1,
        "tamano_torneo": 5,
        "descripcion": "Refinamiento y explotación de soluciones prometedoras"
    }
}

# Configuración de objetivos del sistema
OBJETIVOS_CONFIG = {
    "nutricion": {
        "peso": 0.35,
        "tolerancia_optima": 0.03,    # 3%
        "tolerancia_aceptable": 0.10,  # 10%
        "prioridad": "critica"
    },
    "costo": {
        "peso": 0.30,
        "factor_normalizacion": 15.0,  # Rango esperado 0-15 $/kg
        "prioridad": "alta"
    },
    "eficiencia": {
        "peso": 0.20,
        "factor_normalizacion": 2.5,   # Rango esperado 1.0-2.5
        "prioridad": "alta"
    },
    "disponibilidad": {
        "peso": 0.10,
        "umbral_critico": 0.3,         # Disponibilidad mínima aceptable
        "prioridad": "media"
    },
    "tiempo": {
        "peso": 0.05,
        "factor_normalizacion": 100.0, # Rango esperado 0-100 días
        "prioridad": "baja"
    }
}

# Configuración de restricciones
RESTRICCIONES_CONFIG = {
    "penalizacion_base": 1000,
    "tolerancia_suma": 1e-6,
    "factores_penalizacion": {
        "limite_ingrediente": 100,
        "suma_incorrecta": 1000,
        "ingrediente_excluido": 500,
        "presupuesto_excedido": 200,
        "nutricional_critica": 300
    }
}

# Configuración de archivos y directorios
ARCHIVOS_CONFIG = {
    "directorio_base": os.getcwd(),
    "directorio_reportes": "reportes",
    "directorio_graficas": "graficas",
    "directorio_configuraciones": "configuraciones",
    "directorio_datos": "datos",
    "formatos_exportacion": ["txt", "json", "csv"],
    "codificacion": "utf-8"
}

# Configuración de visualización
VISUALIZACION_CONFIG = {
    "estilo_default": "seaborn",
    "dpi": 300,
    "formato_imagen": "png",
    "tamaño_figura": (12, 8),
    "colores_fases": {
        "inicial": "green",
        "intermedia": "orange", 
        "final": "red"
    },
    "paleta_colores": "husl"
}

# Configuración de logging
LOGGING_CONFIG = {
    "nivel": "INFO",
    "formato": "%(asctime)s - %(levelname)s - %(message)s",
    "archivo_log": "boilernutri.log",
    "rotacion_archivos": True,
    "tamaño_maximo": "10MB",
    "respaldo_archivos": 3
}

# Configuración de rendimiento
RENDIMIENTO_CONFIG = {
    "usar_multiproceso": False,
    "num_procesos": None,  # None = auto-detectar
    "cache_evaluaciones": True,
    "optimizaciones_memoria": True,
    "mostrar_progreso": True,
    "frecuencia_reporte": 20  # Cada 20 generaciones
}

# Configuración de validación
VALIDACION_CONFIG = {
    "validar_entradas": True,
    "validar_restricciones": True,
    "tolerancia_numerica": 1e-10,
    "verificar_consistencia": True,
    "modo_estricto": False
}

# Constantes del sistema
PRECISION_PORCENTAJES = 1e-6
PENALIZACION_RESTRICCIONES = 1000

# Rangos de validación
RANGOS_VALIDACION = {
    "edad_dias": (1, 70),
    "peso_kg": (0.02, 5.0),
    "cantidad_pollos": (1, 100000),
    "presupuesto_kg": (1.0, 50.0),
    "capacidad_planta": (1.0, 10000.0)
}

# Configuración de ingredientes
INGREDIENTES_CONFIG = {
    "porcentaje_minimo_significativo": 0.001,  # 0.1%
    "porcentaje_maximo_individual": 1.0,       # 100%
    "numero_maximo_ingredientes": 20,
    "verificar_disponibilidad": True
}

# Configuración de proveedores
PROVEEDORES_CONFIG = {
    "verificar_precios": True,
    "factor_variacion_maxima": 0.5,  # 50% variación máxima en precios
    "proveedores_minimos": 1,
    "proveedores_recomendados": 3
}

def obtener_configuracion_completa():
    """
    Obtiene toda la configuración del sistema
    
    Returns:
        Diccionario con toda la configuración
    """
    return {
        "sistema": SISTEMA_INFO,
        "algoritmo": ALGORITMO_CONFIG,
        "pesos_fitness": PESOS_FITNESS,
        "fases": FASES_CONFIG,
        "objetivos": OBJETIVOS_CONFIG,
        "restricciones": RESTRICCIONES_CONFIG,
        "archivos": ARCHIVOS_CONFIG,
        "visualizacion": VISUALIZACION_CONFIG,
        "logging": LOGGING_CONFIG,
        "rendimiento": RENDIMIENTO_CONFIG,
        "validacion": VALIDACION_CONFIG,
        "rangos": RANGOS_VALIDACION,
        "ingredientes": INGREDIENTES_CONFIG,
        "proveedores": PROVEEDORES_CONFIG
    }

def validar_configuracion():
    """
    Valida que toda la configuración sea coherente
    
    Returns:
        Tupla (es_valido, lista_errores)
    """
    errores = []
    
    # Validar pesos de fitness
    suma_pesos = sum(PESOS_FITNESS.values())
    if abs(suma_pesos - 1.0) > 0.01:
        errores.append(f"Los pesos de fitness no suman 1.0 (suma actual: {suma_pesos:.3f})")
    
    # Validar fases
    fases_ordenadas = sorted(FASES_CONFIG.items(), key=lambda x: x[1]["inicio"])
    for i, (nombre, config) in enumerate(fases_ordenadas):
        if config["inicio"] >= config["fin"]:
            errores.append(f"Fase {nombre}: inicio >= fin")
        
        if i > 0:
            fase_anterior = fases_ordenadas[i-1][1]
            if config["inicio"] != fase_anterior["fin"]:
                errores.append(f"Gap entre fases {fases_ordenadas[i-1][0]} y {nombre}")
    
    # Validar rangos
    for parametro, (minimo, maximo) in RANGOS_VALIDACION.items():
        if minimo >= maximo:
            errores.append(f"Rango inválido para {parametro}: {minimo} >= {maximo}")
    
    # Validar configuración de algoritmo
    if ALGORITMO_CONFIG["tamano_poblacion"] < 10:
        errores.append("Tamaño de población muy pequeño (< 10)")
    
    if ALGORITMO_CONFIG["num_generaciones"] < 10:
        errores.append("Número de generaciones muy pequeño (< 10)")
    
    if not (0.0 <= ALGORITMO_CONFIG["prob_cruza"] <= 1.0):
        errores.append("Probabilidad de cruza fuera de rango [0,1]")
    
    if not (0.0 <= ALGORITMO_CONFIG["prob_mutacion"] <= 1.0):
        errores.append("Probabilidad de mutación fuera de rango [0,1]")
    
    return len(errores) == 0, errores

def crear_configuracion_personalizada(**kwargs):
    """
    Crea una configuración personalizada
    
    Args:
        **kwargs: Parámetros de configuración a personalizar
        
    Returns:
        Diccionario con configuración personalizada
    """
    config = obtener_configuracion_completa()
    
    # Actualizar configuración con parámetros personalizados
    for clave, valor in kwargs.items():
        if "." in clave:
            # Manejo de claves anidadas (ej: "algoritmo.tamano_poblacion")
            partes = clave.split(".")
            seccion = config
            for parte in partes[:-1]:
                if parte in seccion:
                    seccion = seccion[parte]
                else:
                    break
            else:
                seccion[partes[-1]] = valor
        else:
            # Clave de primer nivel
            if clave in config:
                if isinstance(config[clave], dict) and isinstance(valor, dict):
                    config[clave].update(valor)
                else:
                    config[clave] = valor
    
    return config

def generar_configuracion_por_tamaño(tamaño_problema):
    """
    Genera configuración optimizada según el tamaño del problema
    
    Args:
        tamaño_problema: "pequeño", "mediano", "grande"
        
    Returns:
        Diccionario con configuración optimizada
    """
    configuraciones = {
        "pequeño": {
            "algoritmo.tamano_poblacion": 50,
            "algoritmo.num_generaciones": 100,
            "rendimiento.mostrar_progreso": True,
            "rendimiento.frecuencia_reporte": 10
        },
        "mediano": {
            "algoritmo.tamano_poblacion": 100,
            "algoritmo.num_generaciones": 200,
            "rendimiento.mostrar_progreso": True,
            "rendimiento.frecuencia_reporte": 20
        },
        "grande": {
            "algoritmo.tamano_poblacion": 200,
            "algoritmo.num_generaciones": 500,
            "rendimiento.usar_multiproceso": True,
            "rendimiento.mostrar_progreso": True,
            "rendimiento.frecuencia_reporte": 50
        }
    }
    
    if tamaño_problema not in configuraciones:
        raise ValueError(f"Tamaño de problema no reconocido: {tamaño_problema}")
    
    return crear_configuracion_personalizada(**configuraciones[tamaño_problema])

def exportar_configuracion(archivo, config=None):
    """
    Exporta la configuración a un archivo JSON
    
    Args:
        archivo: Ruta del archivo donde exportar
        config: Configuración a exportar (usa la actual si es None)
    """
    import json
    
    if config is None:
        config = obtener_configuracion_completa()
    
    try:
        with open(archivo, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False, default=str)
        print(f"✅ Configuración exportada a: {archivo}")
    except Exception as e:
        print(f"❌ Error exportando configuración: {e}")

def cargar_configuracion(archivo):
    """
    Carga configuración desde un archivo JSON
    
    Args:
        archivo: Ruta del archivo de configuración
        
    Returns:
        Diccionario con configuración cargada
    """
    import json
    
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"✅ Configuración cargada desde: {archivo}")
        return config
    except FileNotFoundError:
        print(f"❌ Archivo de configuración no encontrado: {archivo}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error parseando configuración: {e}")
        return None

def inicializar_directorios():
    """
    Crea los directorios necesarios para el sistema
    """
    directorios = [
        ARCHIVOS_CONFIG["directorio_reportes"],
        ARCHIVOS_CONFIG["directorio_graficas"],
        ARCHIVOS_CONFIG["directorio_configuraciones"],
        ARCHIVOS_CONFIG["directorio_datos"]
    ]
    
    for directorio in directorios:
        try:
            if not os.path.exists(directorio):
                os.makedirs(directorio)
                print(f"📁 Directorio creado: {directorio}")
        except Exception as e:
            print(f"⚠️  No se pudo crear directorio {directorio}: {e}")

def mostrar_informacion_sistema():
    """
    Muestra información del sistema y configuración actual
    """
    print("=" * 60)
    print(f"🐔 {SISTEMA_INFO['nombre']} v{SISTEMA_INFO['version']}")
    print(f"📝 {SISTEMA_INFO['descripcion']}")
    print("=" * 60)
    print(f"Configuración del algoritmo:")
    print(f"  • Población: {ALGORITMO_CONFIG['tamano_poblacion']} individuos")
    print(f"  • Generaciones: {ALGORITMO_CONFIG['num_generaciones']}")
    print(f"  • Probabilidad de cruza: {ALGORITMO_CONFIG['prob_cruza']}")
    print(f"  • Probabilidad de mutación: {ALGORITMO_CONFIG['prob_mutacion']}")
    print(f"  • Elitismo: {ALGORITMO_CONFIG['elitismo']} individuos")
    
    print(f"\nPesos de objetivos:")
    for objetivo, peso in PESOS_FITNESS.items():
        print(f"  • {objetivo.replace('_', ' ').title()}: {peso:.1%}")
    
    # Validar configuración
    es_valido, errores = validar_configuracion()
    if es_valido:
        print(f"\n✅ Configuración válida")
    else:
        print(f"\n❌ Errores en configuración:")
        for error in errores:
            print(f"   • {error}")
    
    print("=" * 60)

# Ejecutar validación al cargar el módulo
_es_valido, _errores = validar_configuracion()
if not _es_valido:
    import warnings
    warnings.warn(f"Configuración tiene errores: {'; '.join(_errores)}")