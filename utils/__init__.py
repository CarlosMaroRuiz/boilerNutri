"""
Paquete de utilidades para el sistema boilerNutri.

Contiene funciones para visualización, generación de reportes
y procesamiento de entradas del usuario.
"""

from .visualizacion import (
    generar_graficas, 
    grafica_evolucion_fitness, 
    grafica_comparativa_soluciones,
    grafica_perfil_nutricional,
    configurar_estilo_graficas,
    exportar_todas_graficas
)

from .reporte import (
    generar_reporte_completo,
    generar_tabla_formula,
    generar_analisis_nutricional,
    generar_plan_implementacion,
    generar_analisis_economico,
    exportar_reporte_texto,
    exportar_reporte_json,
    imprimir_resumen_consola
)

from .entrada_usuario import (
    procesar_entradas,
    capturar_parametros_produccion,
    validar_parametros_produccion,
    validar_coherencia_entradas,
    cargar_parametros_desde_archivo,
    guardar_parametros_en_archivo,
    mostrar_resumen_parametros
)

__all__ = [
    # Visualización
    'generar_graficas',
    'grafica_evolucion_fitness',
    'grafica_comparativa_soluciones', 
    'grafica_perfil_nutricional',
    'configurar_estilo_graficas',
    'exportar_todas_graficas',
    
    # Reportes
    'generar_reporte_completo',
    'generar_tabla_formula',
    'generar_analisis_nutricional',
    'generar_plan_implementacion',
    'generar_analisis_economico',
    'exportar_reporte_texto',
    'exportar_reporte_json',
    'imprimir_resumen_consola',
    
    # Entrada de usuario
    'procesar_entradas',
    'capturar_parametros_produccion',
    'validar_parametros_produccion',
    'validar_coherencia_entradas',
    'cargar_parametros_desde_archivo',
    'guardar_parametros_en_archivo',
    'mostrar_resumen_parametros'
]

# Configuración de utilidades
CONFIGURACION_UTILS = {
    "formato_graficas_default": "png",
    "dpi_graficas": 300,
    "estilo_graficas_default": "seaborn",
    "directorio_reportes": "reportes",
    "directorio_graficas": "graficas",
    "codificacion_archivos": "utf-8"
}

def obtener_configuracion_utils():
    """
    Obtiene la configuración actual de utilidades
    
    Returns:
        Diccionario con configuración
    """
    return CONFIGURACION_UTILS.copy()

def configurar_utilidades(nueva_configuracion):
    """
    Actualiza la configuración de utilidades
    
    Args:
        nueva_configuracion: Diccionario con nueva configuración
    """
    global CONFIGURACION_UTILS
    CONFIGURACION_UTILS.update(nueva_configuracion)

def verificar_dependencias():
    """
    Verifica que todas las dependencias necesarias estén disponibles
    
    Returns:
        Tupla (dependencias_ok, lista_faltantes)
    """
    dependencias_requeridas = [
        ('matplotlib', 'Visualización de gráficas'),
        ('numpy', 'Operaciones numéricas'),
        ('json', 'Manejo de archivos JSON')
    ]
    
    dependencias_opcionales = [
        ('seaborn', 'Estilos avanzados de gráficas'),
        ('pandas', 'Análisis de datos (opcional)')
    ]
    
    faltantes = []
    
    # Verificar dependencias requeridas
    for modulo, descripcion in dependencias_requeridas:
        try:
            __import__(modulo)
        except ImportError:
            faltantes.append(f"{modulo} - {descripcion}")
    
    # Verificar dependencias opcionales (solo advertencia)
    opcionales_faltantes = []
    for modulo, descripcion in dependencias_opcionales:
        try:
            __import__(modulo)
        except ImportError:
            opcionales_faltantes.append(f"{modulo} - {descripcion}")
    
    if opcionales_faltantes:
        import warnings
        warnings.warn(f"Dependencias opcionales no encontradas: {', '.join(opcionales_faltantes)}")
    
    return len(faltantes) == 0, faltantes

def inicializar_utilidades():
    """
    Inicializa las utilidades del sistema
    """
    # Verificar dependencias
    deps_ok, faltantes = verificar_dependencias()
    
    if not deps_ok:
        raise ImportError(f"Dependencias faltantes: {', '.join(faltantes)}")
    
    # Configurar visualización
    try:
        configurar_estilo_graficas(CONFIGURACION_UTILS["estilo_graficas_default"])
    except Exception as e:
        import warnings
        warnings.warn(f"No se pudo configurar estilo de gráficas: {e}")
    
    # Crear directorios si no existen
    import os
    for directorio in [CONFIGURACION_UTILS["directorio_reportes"], 
                      CONFIGURACION_UTILS["directorio_graficas"]]:
        if not os.path.exists(directorio):
            try:
                os.makedirs(directorio)
            except Exception as e:
                import warnings
                warnings.warn(f"No se pudo crear directorio {directorio}: {e}")

def generar_reporte_sistema_completo(resultados, ingredientes_data, config_evaluacion, 
                                   restricciones_usuario=None, incluir_graficas=True,
                                   exportar_archivos=True):
    """
    Genera un reporte completo del sistema incluyendo gráficas
    
    Args:
        resultados: Resultados del algoritmo genético
        ingredientes_data: Lista de datos de ingredientes
        config_evaluacion: Configuración de evaluación
        restricciones_usuario: Restricciones del usuario
        incluir_graficas: Si incluir gráficas en el reporte
        exportar_archivos: Si exportar archivos del reporte
        
    Returns:
        Diccionario con reporte completo y rutas de archivos generados
    """
    print("📊 Generando reporte completo del sistema...")
    
    reporte_completo = {
        "reporte_datos": None,
        "graficas": None,
        "archivos_generados": []
    }
    
    try:
        # Generar reporte de datos
        reporte_datos = generar_reporte_completo(resultados, ingredientes_data, 
                                               config_evaluacion, restricciones_usuario)
        reporte_completo["reporte_datos"] = reporte_datos
        
        # Generar gráficas si se solicita
        if incluir_graficas:
            graficas = generar_graficas(resultados, ingredientes_data, config_evaluacion)
            reporte_completo["graficas"] = graficas
        
        # Exportar archivos si se solicita
        if exportar_archivos:
            archivos_generados = []
            
            # Exportar reporte en texto
            archivo_texto = "reporte_optimizacion.txt"
            exportar_reporte_texto(reporte_datos, archivo_texto)
            archivos_generados.append(archivo_texto)
            
            # Exportar reporte en JSON
            archivo_json = "reporte_optimizacion.json"
            exportar_reporte_json(reporte_datos, archivo_json)
            archivos_generados.append(archivo_json)
            
            # Exportar gráficas si están disponibles
            if incluir_graficas and graficas:
                exportar_todas_graficas(resultados, ingredientes_data, config_evaluacion)
                archivos_generados.extend([
                    "graficas/evolucion_fitness.png",
                    "graficas/comparativa_soluciones.png",
                    "graficas/perfil_nutricional.png",
                    "graficas/distribucion_costos.png",
                    "graficas/metricas_algoritmo.png"
                ])
            
            reporte_completo["archivos_generados"] = archivos_generados
        
        # Mostrar resumen en consola
        imprimir_resumen_consola(reporte_datos)
        
        print(f"✅ Reporte completo generado exitosamente")
        if exportar_archivos:
            print(f"📁 Archivos generados: {len(reporte_completo['archivos_generados'])}")
        
        return reporte_completo
        
    except Exception as e:
        print(f"❌ Error generando reporte completo: {e}")
        reporte_completo["error"] = str(e)
        return reporte_completo

def limpiar_archivos_temporales():
    """
    Limpia archivos temporales generados por el sistema
    """
    import os
    import glob
    
    archivos_a_limpiar = [
        "*.tmp",
        "*.temp",
        "__pycache__/*",
        "*.pyc"
    ]
    
    archivos_eliminados = 0
    
    for patron in archivos_a_limpiar:
        for archivo in glob.glob(patron, recursive=True):
            try:
                if os.path.isfile(archivo):
                    os.remove(archivo)
                    archivos_eliminados += 1
            except Exception as e:
                import warnings
                warnings.warn(f"No se pudo eliminar {archivo}: {e}")
    
    if archivos_eliminados > 0:
        print(f"🧹 Se eliminaron {archivos_eliminados} archivos temporales")

# Ejecutar inicialización al importar el paquete
try:
    inicializar_utilidades()
except Exception as e:
    import warnings
    warnings.warn(f"Error inicializando utilidades: {e}")

# Información del paquete
__version__ = "1.0.0"
__author__ = "Sistema boilerNutri"
__description__ = "Utilidades para visualización, reportes y entrada de usuario"