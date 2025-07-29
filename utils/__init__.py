"""
Paquete de utilidades para boilerNutri
ACTUALIZADO para incluir visualización de evolución de fitness
"""

import os
import warnings
from datetime import datetime

# Importaciones principales
from .visualizacion import *
from .reporte import *
from .entrada_usuario import *

# Nuevas importaciones para evolución de fitness
try:
    from .fitness_evolution import (
        FitnessEvolutionTracker,
        FitnessEvolutionPlot, 
        FitnessMetrics,
        crear_visualizador_fitness
    )
    FITNESS_EVOLUTION_AVAILABLE = True
except ImportError as e:
    warnings.warn(f"Módulo de evolución de fitness no disponible: {e}")
    FITNESS_EVOLUTION_AVAILABLE = False

# Información del paquete actualizada
__version__ = "1.1.0"  # Incrementada por nueva funcionalidad
__author__ = "Sistema boilerNutri"
__description__ = "Utilidades para visualización, reportes, entrada de usuario y evolución de fitness"

def inicializar_utilidades():
    """
    Inicializa el sistema de utilidades completo
    Incluye configuración de directorios y validación de dependencias
    """
    print("🔧 Inicializando utilidades de boilerNutri...")
    
    try:
        # Crear directorios necesarios
        directorios = [
            "reportes",
            "graficas", 
            "graficas/evolucion",  # Nuevo directorio para gráficas de evolución
            "configuraciones",
            "datos",
            "temp"
        ]
        
        for directorio in directorios:
            if not os.path.exists(directorio):
                os.makedirs(directorio)
                print(f"📁 Directorio creado: {directorio}")
        
        # Verificar disponibilidad de módulos
        modulos_status = {
            "Visualización": True,
            "Reportes": True,
            "Entrada de Usuario": True,
            "Evolución de Fitness": FITNESS_EVOLUTION_AVAILABLE
        }
        
        print("\n📊 Estado de módulos:")
        for modulo, disponible in modulos_status.items():
            status = "✅" if disponible else "❌"
            print(f"  {status} {modulo}")
        
        if not FITNESS_EVOLUTION_AVAILABLE:
            print("\n⚠️  Algunas funcionalidades de evolución de fitness no estarán disponibles")
            print("   Instale matplotlib >= 3.0 para funcionalidad completa")
        
        print("✅ Utilidades inicializadas correctamente\n")
        
    except Exception as e:
        print(f"❌ Error inicializando utilidades: {e}")
        raise

def obtener_info_sistema():
    """
    Obtiene información completa del sistema de utilidades
    """
    info = {
        'version': __version__,
        'autor': __author__,
        'descripcion': __description__,
        'modulos_disponibles': {
            'visualizacion': True,
            'reportes': True, 
            'entrada_usuario': True,
            'fitness_evolution': FITNESS_EVOLUTION_AVAILABLE
        },
        'directorios': [
            "reportes",
            "graficas",
            "graficas/evolucion",
            "configuraciones", 
            "datos",
            "temp"
        ]
    }
    
    return info

def generar_reporte_completo(resultados, ingredientes_data, config_evaluacion, 
                           fitness_tracker=None, exportar_archivos=True, incluir_graficas=True):
    """
    Genera un reporte completo incluyendo evolución de fitness
    ACTUALIZADO para incluir datos de evolución
    
    Args:
        resultados: Resultados de optimización
        ingredientes_data: Datos de ingredientes utilizados
        config_evaluacion: Configuración de evaluación utilizada
        fitness_tracker: Tracker de evolución de fitness (opcional)
        exportar_archivos: Si exportar archivos de reporte
        incluir_graficas: Si incluir gráficas en el reporte
    
    Returns:
        Diccionario con reporte completo
    """
    try:
        print("📄 Generando reporte completo...")
        
        # Generar reporte base
        reporte_completo = generar_reporte_final(resultados, config_evaluacion)
        
        # Agregar información de evolución si está disponible
        if fitness_tracker and FITNESS_EVOLUTION_AVAILABLE:
            print("📈 Incluyendo análisis de evolución de fitness...")
            
            # Obtener datos de evolución
            datos_evolucion = fitness_tracker.obtener_datos_actuales()
            metricas_evolucion = FitnessMetrics.calcular_convergencia(datos_evolucion['mejor_fitness'])
            reporte_evolucion = FitnessMetrics.generar_reporte_evolucion(fitness_tracker)
            
            # Agregar al reporte
            reporte_completo['evolucion_algoritmo'] = {
                'datos': datos_evolucion,
                'metricas': metricas_evolucion,
                'reporte_texto': reporte_evolucion,
                'generaciones_ejecutadas': len(datos_evolucion['generaciones']),
                'convergencia_detectada': FitnessMetrics.detectar_convergencia_prematura(fitness_tracker)
            }
        
        # Exportar archivos si se solicita
        archivos_generados = []
        if exportar_archivos:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Reporte principal
            archivo_reporte = f"reportes/reporte_optimizacion_{timestamp}.json"
            with open(archivo_reporte, 'w', encoding='utf-8') as f:
                import json
                json.dump(reporte_completo, f, indent=2, ensure_ascii=False, default=str)
            archivos_generados.append(archivo_reporte)
            
            # Gráficas
            if incluir_graficas:
                # Gráficas principales de soluciones
                if 'graficas' in locals():
                    exportar_todas_graficas(resultados, ingredientes_data, config_evaluacion)
                    archivos_generados.extend([
                        "graficas/evolucion_fitness.png",
                        "graficas/comparativa_soluciones.png", 
                        "graficas/perfil_nutricional.png",
                        "graficas/distribucion_costos.png",
                        "graficas/metricas_algoritmo.png"
                    ])
                
                # Gráfica de evolución de fitness específica
                if fitness_tracker and FITNESS_EVOLUTION_AVAILABLE:
                    try:
                        # Crear gráfica temporal para exportar
                        import matplotlib.pyplot as plt
                        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
                        
                        datos = datos_evolucion
                        
                        # Plot de fitness
                        ax1.plot(datos['generaciones'], datos['mejor_fitness'], 'g-', linewidth=2, label='Mejor')
                        ax1.plot(datos['generaciones'], datos['promedio_fitness'], 'b-', linewidth=1.5, label='Promedio')
                        ax1.plot(datos['generaciones'], datos['peor_fitness'], 'r-', linewidth=1, alpha=0.7, label='Peor')
                        ax1.set_title('Evolución del Fitness')
                        ax1.set_xlabel('Generación')
                        ax1.set_ylabel('Fitness')
                        ax1.grid(True, alpha=0.3)
                        ax1.legend()
                        
                        # Plot de diversidad
                        ax2.plot(datos['generaciones'], datos['diversidad'], 'm-', linewidth=1.5, label='Diversidad')
                        ax2.set_title('Diversidad de la Población')
                        ax2.set_xlabel('Generación')
                        ax2.set_ylabel('Diversidad')
                        ax2.grid(True, alpha=0.3)
                        ax2.legend()
                        
                        plt.tight_layout()
                        
                        archivo_evolucion = f"graficas/evolucion/evolucion_fitness_{timestamp}.png"
                        plt.savefig(archivo_evolucion, dpi=300, bbox_inches='tight')
                        plt.close()
                        
                        archivos_generados.append(archivo_evolucion)
                        print(f"💾 Gráfica de evolución guardada: {archivo_evolucion}")
                        
                    except Exception as e:
                        print(f"⚠️  No se pudo generar gráfica de evolución: {e}")
            
            reporte_completo["archivos_generados"] = archivos_generados
        
        # Mostrar resumen en consola
        imprimir_resumen_consola(reporte_completo)
        
        print(f"✅ Reporte completo generado exitosamente")
        if exportar_archivos:
            print(f"📁 Archivos generados: {len(archivos_generados)}")
        
        return reporte_completo
        
    except Exception as e:
        print(f"❌ Error generando reporte completo: {e}")
        reporte_completo = {"error": str(e)}
        return reporte_completo

def limpiar_archivos_temporales():
    """
    Limpia archivos temporales generados por el sistema
    ACTUALIZADO para incluir archivos de evolución
    """
    import glob
    
    archivos_a_limpiar = [
        "*.tmp",
        "*.temp",
        "__pycache__/*",
        "*.pyc",
        "temp/*",
        "graficas/temp_*"  # Archivos temporales de gráficas
    ]
    
    archivos_eliminados = 0
    
    for patron in archivos_a_limpiar:
        for archivo in glob.glob(patron, recursive=True):
            try:
                if os.path.isfile(archivo):
                    os.remove(archivo)
                    archivos_eliminados += 1
            except Exception as e:
                warnings.warn(f"No se pudo eliminar {archivo}: {e}")
    
    if archivos_eliminados > 0:
        print(f"🧹 Se eliminaron {archivos_eliminados} archivos temporales")

def crear_ejemplo_uso_fitness():
    """
    Crea un ejemplo de uso del sistema de evolución de fitness
    Útil para testing y demostración
    """
    if not FITNESS_EVOLUTION_AVAILABLE:
        print("❌ Módulo de evolución de fitness no disponible")
        return None
    
    try:
        # Crear tracker de ejemplo
        tracker = FitnessEvolutionTracker(max_generations=50)
        
        # Simular algunas generaciones
        import random
        for gen in range(30):
            # Simular población con fitness creciente
            fitness_poblacion = [random.uniform(0.3 + gen*0.01, 0.8 + gen*0.01) for _ in range(20)]
            fitness_poblacion = sorted(fitness_poblacion, reverse=True)
            
            tracker.agregar_generacion(gen, fitness_poblacion)
        
        # Generar reporte de ejemplo
        reporte = FitnessMetrics.generar_reporte_evolucion(tracker)
        
        print("📊 Ejemplo de reporte de evolución generado:")
        print(reporte[:300] + "..." if len(reporte) > 300 else reporte)
        
        return tracker
        
    except Exception as e:
        print(f"❌ Error creando ejemplo: {e}")
        return None

# Ejecutar inicialización al importar el paquete
try:
    inicializar_utilidades()
except Exception as e:
    warnings.warn(f"Error inicializando utilidades: {e}")

# Función de conveniencia para integración fácil en GUI
def integrar_fitness_evolution_en_gui(parent_frame, algoritmo_config):
    """
    Función de conveniencia para integrar evolución de fitness en GUI existente
    
    Args:
        parent_frame: Frame de tkinter donde mostrar
        algoritmo_config: Configuración del algoritmo genético
    
    Returns:
        tuple: (tracker, plot) o (None, None) si no está disponible
    """
    if not FITNESS_EVOLUTION_AVAILABLE:
        print("⚠️  Evolución de fitness no disponible - usando placeholder")
        return None, None
    
    try:
        max_gen = algoritmo_config.get('num_generaciones', 100)
        return crear_visualizador_fitness(parent_frame, max_gen, real_time=True)
    except Exception as e:
        print(f"❌ Error integrando evolución de fitness: {e}")
        return None, None

# Compatibilidad hacia atrás
if FITNESS_EVOLUTION_AVAILABLE:
    # Hacer disponibles las clases principales
    __all__ = [
        'FitnessEvolutionTracker',
        'FitnessEvolutionPlot', 
        'FitnessMetrics',
        'crear_visualizador_fitness',
        'generar_reporte_completo',
        'integrar_fitness_evolution_en_gui',
        'obtener_info_sistema'
    ]
else:
    __all__ = [
        'generar_reporte_completo',
        'obtener_info_sistema'
    ]