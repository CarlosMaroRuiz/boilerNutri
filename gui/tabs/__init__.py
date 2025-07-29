"""
Módulo de pestañas para la interfaz gráfica de boilerNutri
ACTUALIZADO para incluir funcionalidades de evolución de fitness
"""

# Importaciones principales de las pestañas
from .parametros_tab import ParametrosTab
from .ingredientes_tab import IngredientesTab
from .optimizacion_tab import OptimizacionTab  # Ahora incluye evolución de fitness
from .resultados_tab import ResultadosTab

# Verificar disponibilidad de dependencias para fitness evolution
try:
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    import warnings
    warnings.warn("Matplotlib no disponible - algunas funcionalidades de visualización pueden estar limitadas")

# Información del módulo
__version__ = "1.1.0"  # Actualizada por nueva funcionalidad de fitness evolution
__all__ = [
    'ParametrosTab',
    'IngredientesTab', 
    'OptimizacionTab',
    'ResultadosTab'
]

def verificar_dependencias():
    """
    Verifica que todas las dependencias necesarias estén disponibles
    """
    dependencias = {
        'tkinter': True,  # Siempre disponible en Python estándar
        'matplotlib': MATPLOTLIB_AVAILABLE,
        'numpy': True  # Asumido disponible
    }
    
    print("🔍 Verificando dependencias de GUI:")
    for dep, disponible in dependencias.items():
        status = "✅" if disponible else "❌"
        print(f"  {status} {dep}")
    
    if not MATPLOTLIB_AVAILABLE:
        print("\n⚠️  Recomendación: Instale matplotlib para visualización completa:")
        print("   pip install matplotlib>=3.0")
    
    return all(dependencias.values())

def obtener_info_tabs():
    """
    Obtiene información sobre las pestañas disponibles
    """
    tabs_info = {
        'ParametrosTab': {
            'descripcion': 'Configuración de parámetros de producción',
            'funcionalidades': [
                'Selección de raza de pollos',
                'Configuración de pesos y edad',
                'Parámetros de producción'
            ]
        },
        'IngredientesTab': {
            'descripcion': 'Gestión de ingredientes disponibles',
            'funcionalidades': [
                'Selección de ingredientes',
                'Visualización de precios y nutrición',
                'Actualización de disponibilidad'
            ]
        },
        'OptimizacionTab': {
            'descripcion': 'Ejecución y monitoreo de optimización',
            'funcionalidades': [
                'Control del algoritmo genético',
                'Monitoreo en tiempo real',
                'Visualización de evolución de fitness',  # NUEVO
                'Métricas de convergencia',              # NUEVO
                'Reportes de evolución'                  # NUEVO
            ],
            'nuevas_funcionalidades': [  # DESTACAR LO NUEVO
                'Gráficas de evolución de fitness en tiempo real',
                'Tracking de diversidad poblacional',
                'Análisis de convergencia automático',
                'Exportación de gráficas de evolución',
                'Reportes detallados de métricas'
            ]
        },
        'ResultadosTab': {
            'descripcion': 'Visualización y exportación de resultados',
            'funcionalidades': [
                'Comparación de mejores soluciones',
                'Análisis nutricional detallado',
                'Exportación de reportes',
                'Gráficas de composición'
            ]
        }
    }
    
    return tabs_info

def crear_tabs_en_notebook(notebook, main_window):
    """
    Función de conveniencia para crear todas las pestañas en un notebook
    
    Args:
        notebook: ttk.Notebook donde agregar las pestañas
        main_window: Referencia a la ventana principal
    
    Returns:
        dict: Diccionario con referencias a todas las pestañas creadas
    """
    try:
        # Crear pestañas
        tabs = {}
        
        # Pestaña 1: Parámetros
        tabs['parametros'] = ParametrosTab(notebook, main_window)
        notebook.add(tabs['parametros'].frame, text="📊 Configuración de Producción")
        
        # Pestaña 2: Ingredientes  
        tabs['ingredientes'] = IngredientesTab(notebook, main_window)
        notebook.add(tabs['ingredientes'].frame, text="🌾 Ingredientes Disponibles")
        
        # Pestaña 3: Optimización (con evolución de fitness)
        tabs['optimizacion'] = OptimizacionTab(notebook, main_window)
        tab_text = "🧬 Optimización"
        if MATPLOTLIB_AVAILABLE:
            tab_text += " + Evolución"  # Indicar funcionalidad extra
        notebook.add(tabs['optimizacion'].frame, text=tab_text)
        
        # Pestaña 4: Resultados
        tabs['resultados'] = ResultadosTab(notebook, main_window)
        notebook.add(tabs['resultados'].frame, text="📈 Resultados")
        
        print(f"✅ {len(tabs)} pestañas creadas exitosamente")
        
        if MATPLOTLIB_AVAILABLE:
            print("🎯 Funcionalidades de evolución de fitness habilitadas")
        
        return tabs
        
    except Exception as e:
        print(f"❌ Error creando pestañas: {e}")
        raise

def mostrar_ayuda_evoluccion_fitness():
    """
    Muestra información de ayuda sobre las nuevas funcionalidades de evolución de fitness
    """
    ayuda = """
    🧬 NUEVA FUNCIONALIDAD: EVOLUCIÓN DE FITNESS
    
    📈 ¿Qué es?
    Sistema de visualización en tiempo real que muestra cómo evoluciona
    el algoritmo genético durante la optimización.
    
    📊 Gráficas Incluidas:
    • Evolución del Fitness: Mejor, promedio y peor fitness por generación
    • Diversidad Poblacional: Qué tan diversa es la población
    • Métricas de Convergencia: Cuándo y cómo converge el algoritmo
    
    🔧 Funcionalidades:
    • Visualización en tiempo real durante optimización
    • Exportación de gráficas en múltiples formatos
    • Reportes automáticos de métricas de evolución
    • Detección de convergencia prematura
    • Análisis de estabilidad del algoritmo
    
    💡 Cómo usar:
    1. Configure sus parámetros en la pestaña de Configuración
    2. Vaya a la pestaña de Optimización + Evolución
    3. Inicie la optimización y observe las gráficas en tiempo real
    4. Use los botones para guardar gráficas o ver reportes detallados
    
    📋 Métricas Disponibles:
    • Tasa de mejora promedio
    • Generaciones sin mejora
    • Nivel de estabilidad
    • Diversidad poblacional
    • Detección de convergencia prematura
    """
    
    return ayuda

# Inicialización del módulo
if __name__ == "__main__":
    # Si se ejecuta directamente, mostrar información
    print("🖥️  Módulo de pestañas de boilerNutri")
    print(f"📌 Versión: {__version__}")
    
    verificar_dependencias()
    
    print("\n📋 Pestañas disponibles:")
    tabs_info = obtener_info_tabs()
    for nombre, info in tabs_info.items():
        print(f"\n🔹 {nombre}")
        print(f"   {info['descripcion']}")
        if 'nuevas_funcionalidades' in info:
            print("   ✨ Nuevas funcionalidades:")
            for func in info['nuevas_funcionalidades']:
                print(f"     • {func}")
    
    if MATPLOTLIB_AVAILABLE:
        print("\n" + mostrar_ayuda_evoluccion_fitness())