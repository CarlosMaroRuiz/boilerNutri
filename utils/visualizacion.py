"""
Funciones para visualización de resultados y evolución del algoritmo.

Genera gráficas de evolución de fitness, comparativas entre soluciones
y análisis de convergencia.
"""

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib.patches import Rectangle
import warnings

# Configurar estilo por defecto
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def generar_graficas(resultados, ingredientes_data, config_evaluacion=None, guardar_archivos=False):
    """
    Genera todas las gráficas del sistema
    
    Args:
        resultados: Resultado del algoritmo genético
        ingredientes_data: Lista de datos de ingredientes
        config_evaluacion: Configuración de evaluación (opcional)
        guardar_archivos: Si guardar las gráficas como archivos
        
    Returns:
        Diccionario con las figuras generadas
    """
    figuras = {}
    
    try:
        # 1. Gráfica de evolución del fitness
        if "historico_fitness" in resultados:
            fig_evolucion = grafica_evolucion_fitness(resultados["historico_fitness"])
            figuras["evolucion_fitness"] = fig_evolucion
            if guardar_archivos:
                fig_evolucion.savefig("evolucion_fitness.png", dpi=300, bbox_inches='tight')
        
        # 2. Comparativa de mejores soluciones
        if "mejores_individuos" in resultados:
            fig_comparativa = grafica_comparativa_soluciones(resultados["mejores_individuos"], ingredientes_data)
            figuras["comparativa_soluciones"] = fig_comparativa
            if guardar_archivos:
                fig_comparativa.savefig("comparativa_soluciones.png", dpi=300, bbox_inches='tight')
        
        # 3. Análisis nutricional del mejor individuo
        if "mejor_individuo" in resultados and resultados["mejor_individuo"]:
            fig_nutricional = grafica_perfil_nutricional(resultados["mejor_individuo"], 
                                                       config_evaluacion, ingredientes_data)
            figuras["perfil_nutricional"] = fig_nutricional
            if guardar_archivos:
                fig_nutricional.savefig("perfil_nutricional.png", dpi=300, bbox_inches='tight')
        
        # 4. Distribución de costos por ingrediente
        if "mejores_individuos" in resultados and resultados["mejores_individuos"]:
            fig_costos = grafica_distribucion_costos(resultados["mejores_individuos"][0], ingredientes_data)
            figuras["distribucion_costos"] = fig_costos
            if guardar_archivos:
                fig_costos.savefig("distribucion_costos.png", dpi=300, bbox_inches='tight')
        
        # 5. Métricas del algoritmo
        if "historico_metricas" in resultados:
            fig_metricas = grafica_metricas_algoritmo(resultados["historico_metricas"])
            figuras["metricas_algoritmo"] = fig_metricas
            if guardar_archivos:
                fig_metricas.savefig("metricas_algoritmo.png", dpi=300, bbox_inches='tight')
        
        print(f"✅ Se generaron {len(figuras)} gráficas exitosamente")
        
    except Exception as e:
        print(f"⚠️  Error generando gráficas: {e}")
        figuras["error"] = str(e)
    
    return figuras

def grafica_evolucion_fitness(historico_fitness):
    """
    Genera gráfica de evolución del fitness a lo largo de las generaciones
    
    Args:
        historico_fitness: Lista con el mejor fitness por generación
        
    Returns:
        Figura de matplotlib
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    generaciones = range(len(historico_fitness))
    
    # Línea principal de evolución
    ax.plot(generaciones, historico_fitness, 'b-', linewidth=2, label='Mejor Fitness')
    
    # Añadir línea de tendencia si hay suficientes datos
    if len(historico_fitness) > 10:
        z = np.polyfit(generaciones, historico_fitness, 1)
        p = np.poly1d(z)
        ax.plot(generaciones, p(generaciones), 'r--', alpha=0.7, label='Tendencia')
    
    # Destacar mejora inicial y convergencia
    if len(historico_fitness) > 1:
        mejora_total = historico_fitness[0] - historico_fitness[-1]
        mejora_pct = (mejora_total / historico_fitness[0]) * 100 if historico_fitness[0] > 0 else 0
        
        ax.text(0.02, 0.98, f'Mejora total: {mejora_total:.4f} ({mejora_pct:.1f}%)', 
                transform=ax.transAxes, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    
    ax.set_xlabel('Generación')
    ax.set_ylabel('Fitness (menor es mejor)')
    ax.set_title('Evolución del Fitness a lo Largo de las Generaciones')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Añadir marcas de fases si se puede detectar
    if len(historico_fitness) > 60:  # Solo si hay suficientes generaciones
        fase1 = len(historico_fitness) * 0.3
        fase2 = len(historico_fitness) * 0.7
        
        ax.axvline(x=fase1, color='green', linestyle=':', alpha=0.7, label='Fase Intermedia')
        ax.axvline(x=fase2, color='orange', linestyle=':', alpha=0.7, label='Fase Final')
        ax.legend()
    
    plt.tight_layout()
    return fig

def grafica_comparativa_soluciones(mejores_individuos, ingredientes_data):
    """
    Genera comparativa visual de los mejores individuos
    
    Args:
        mejores_individuos: Lista de mejores individuos
        ingredientes_data: Lista de datos de ingredientes
        
    Returns:
        Figura de matplotlib
    """
    if not mejores_individuos:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, 'No hay individuos para comparar', 
                ha='center', va='center', transform=ax.transAxes, fontsize=16)
        return fig
    
    # Tomar hasta 3 mejores individuos
    individuos_a_comparar = mejores_individuos[:3]
    nombres_ingredientes = [ing["nombre"] for ing in ingredientes_data]
    
    # Preparar datos para gráfica de barras agrupadas
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12))
    
    # Gráfica 1: Composición por ingredientes
    x = np.arange(len(nombres_ingredientes))
    width = 0.25
    
    for i, individuo in enumerate(individuos_a_comparar):
        porcentajes = [p * 100 for p in individuo.porcentajes]  # Convertir a porcentajes
        ax1.bar(x + i * width, porcentajes, width, 
                label=f'Solución {i+1} (Fitness: {individuo.fitness:.3f})')
    
    ax1.set_xlabel('Ingredientes')
    ax1.set_ylabel('Porcentaje (%)')
    ax1.set_title('Comparación de Composición entre Mejores Soluciones')
    ax1.set_xticks(x + width)
    ax1.set_xticklabels(nombres_ingredientes, rotation=45, ha='right')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Gráfica 2: Métricas comparativas
    metricas_nombres = ['Fitness', 'Costo ($/kg)']
    metricas_valores = []
    
    for individuo in individuos_a_comparar:
        valores = [individuo.fitness, getattr(individuo, 'costo_total', 0)]
        metricas_valores.append(valores)
    
    # Añadir más métricas si están disponibles
    if hasattr(individuos_a_comparar[0], 'conversion_alimenticia'):
        metricas_nombres.append('Conversión Alimenticia')
        for i, individuo in enumerate(individuos_a_comparar):
            metricas_valores[i].append(getattr(individuo, 'conversion_alimenticia', 0))
    
    if hasattr(individuos_a_comparar[0], 'dias_peso_objetivo'):
        metricas_nombres.append('Días hasta Peso Objetivo')
        for i, individuo in enumerate(individuos_a_comparar):
            metricas_valores[i].append(getattr(individuo, 'dias_peso_objetivo', 0))
    
    # Normalizar métricas para visualización
    metricas_norm = np.array(metricas_valores).T
    x_metricas = np.arange(len(metricas_nombres))
    
    for i, individuo in enumerate(individuos_a_comparar):
        ax2.plot(x_metricas, metricas_norm[:, i], 'o-', linewidth=2, markersize=8,
                label=f'Solución {i+1}')
    
    ax2.set_xlabel('Métricas')
    ax2.set_ylabel('Valor')
    ax2.set_title('Comparación de Métricas entre Mejores Soluciones')
    ax2.set_xticks(x_metricas)
    ax2.set_xticklabels(metricas_nombres, rotation=45, ha='right')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

def grafica_perfil_nutricional(individuo, config_evaluacion, ingredientes_data):
    """
    Genera gráfica del perfil nutricional vs requerimientos
    
    Args:
        individuo: Individuo a analizar
        config_evaluacion: Configuración de evaluación
        ingredientes_data: Lista de datos de ingredientes
        
    Returns:
        Figura de matplotlib
    """
    from genetic.fitness.nutricion import calcular_propiedades_nutricionales
    from conocimiento.requerimientos import obtener_requerimientos, obtener_etapa
    
    # Calcular propiedades nutricionales
    calcular_propiedades_nutricionales(individuo, ingredientes_data)
    
    # Obtener requerimientos según la edad
    if config_evaluacion and "edad_dias" in config_evaluacion:
        edad_dias = config_evaluacion["edad_dias"]
        etapa = obtener_etapa(edad_dias)
        requerimientos = obtener_requerimientos(edad_dias)
    else:
        etapa = "finalizacion"
        requerimientos = obtener_requerimientos(35)  # Por defecto 35 días
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Gráfica 1: Comparación nutricional (radar/barras)
    nutrientes = list(requerimientos.keys())
    valores_obtenidos = [individuo.propiedades_nutricionales.get(nut, 0) for nut in nutrientes]
    valores_requeridos = [requerimientos[nut] for nut in nutrientes]
    
    x = np.arange(len(nutrientes))
    width = 0.35
    
    # Convertir energía para mejor visualización
    for i, nut in enumerate(nutrientes):
        if nut == "energia":
            valores_obtenidos[i] /= 1000  # Convertir a miles
            valores_requeridos[i] /= 1000
        else:
            valores_obtenidos[i] *= 100  # Convertir a porcentajes
            valores_requeridos[i] *= 100
    
    bars1 = ax1.bar(x - width/2, valores_obtenidos, width, label='Obtenido', alpha=0.8)
    bars2 = ax1.bar(x + width/2, valores_requeridos, width, label='Requerido', alpha=0.8)
    
    # Colorear barras según cumplimiento
    for i, (obtenido, requerido) in enumerate(zip(valores_obtenidos, valores_requeridos)):
        if nutrientes[i] == "fibra":
            # Para fibra, verde si está por debajo del límite
            color = 'green' if obtenido <= requerido else 'red'
        else:
            # Para otros nutrientes, verde si está cerca del requerimiento
            ratio = obtenido / requerido if requerido > 0 else 0
            if 0.95 <= ratio <= 1.1:
                color = 'green'
            elif 0.85 <= ratio < 0.95 or 1.1 < ratio <= 1.2:
                color = 'orange'
            else:
                color = 'red'
        
        bars1[i].set_color(color)
    
    ax1.set_xlabel('Nutrientes')
    ax1.set_ylabel('Valor (%)')
    ax1.set_title(f'Perfil Nutricional vs Requerimientos (Etapa: {etapa.title()})')
    ax1.set_xticks(x)
    ax1.set_xticklabels([nut.title() for nut in nutrientes], rotation=45, ha='right')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Gráfica 2: Distribución de ingredientes (pie chart)
    ingredientes_activos = []
    porcentajes_activos = []
    
    for i, porcentaje in enumerate(individuo.porcentajes):
        if porcentaje > 0.005:  # Más de 0.5%
            if i < len(ingredientes_data):
                ingredientes_activos.append(ingredientes_data[i]["nombre"])
                porcentajes_activos.append(porcentaje * 100)
    
    if ingredientes_activos:
        # Agrupar ingredientes menores al 2% en "Otros"
        ingredientes_final = []
        porcentajes_final = []
        otros_total = 0
        
        for ing, pct in zip(ingredientes_activos, porcentajes_activos):
            if pct >= 2.0:
                ingredientes_final.append(ing)
                porcentajes_final.append(pct)
            else:
                otros_total += pct
        
        if otros_total > 0:
            ingredientes_final.append("Otros")
            porcentajes_final.append(otros_total)
        
        wedges, texts, autotexts = ax2.pie(porcentajes_final, labels=ingredientes_final, 
                                          autopct='%1.1f%%', startangle=90)
        
        # Mejorar legibilidad del texto
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
    
    ax2.set_title('Distribución de Ingredientes en la Formulación')
    
    plt.tight_layout()
    return fig

def grafica_distribucion_costos(individuo, ingredientes_data):
    """
    Genera gráfica de distribución de costos por ingrediente
    
    Args:
        individuo: Individuo a analizar
        ingredientes_data: Lista de datos de ingredientes
        
    Returns:
        Figura de matplotlib
    """
    from genetic.fitness.costo import calcular_costo_por_ingrediente
    
    # Calcular costos por ingrediente
    costos_ingrediente = calcular_costo_por_ingrediente(individuo, ingredientes_data)
    
    if not costos_ingrediente:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, 'No hay datos de costos disponibles', 
                ha='center', va='center', transform=ax.transAxes, fontsize=16)
        return fig
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # Gráfica 1: Costo por ingrediente (barras)
    ingredientes = [item["ingrediente"] for item in costos_ingrediente]
    costos_kg = [item["costo_por_kg"] for item in costos_ingrediente]
    porcentajes = [item["porcentaje"] for item in costos_ingrediente]
    
    # Crear barras con colores según el costo
    colors = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(costos_kg)))
    bars = ax1.bar(ingredientes, costos_kg, color=colors)
    
    # Añadir etiquetas de porcentaje en las barras
    for bar, pct in zip(bars, porcentajes):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{pct:.1f}%', ha='center', va='bottom', fontsize=10)
    
    ax1.set_xlabel('Ingredientes')
    ax1.set_ylabel('Costo ($/kg de formulación)')
    ax1.set_title('Contribución al Costo por Ingrediente')
    ax1.tick_params(axis='x', rotation=45)
    ax1.grid(True, alpha=0.3)
    
    # Añadir línea de costo total
    costo_total = sum(costos_kg)
    ax1.axhline(y=costo_total, color='red', linestyle='--', alpha=0.7,
                label=f'Costo Total: ${costo_total:.2f}/kg')
    ax1.legend()
    
    # Gráfica 2: Análisis costo-beneficio (scatter)
    precios_unitarios = [item["precio_unitario"] for item in costos_ingrediente]
    
    # Calcular eficiencia (porcentaje / precio unitario)
    eficiencias = [pct / precio for pct, precio in zip(porcentajes, precios_unitarios)]
    
    scatter = ax2.scatter(precios_unitarios, porcentajes, s=[e*100 for e in eficiencias], 
                         c=costos_kg, cmap='RdYlGn_r', alpha=0.7)
    
    # Añadir etiquetas
    for i, ing in enumerate(ingredientes):
        ax2.annotate(ing, (precios_unitarios[i], porcentajes[i]), 
                    xytext=(5, 5), textcoords='offset points', fontsize=9)
    
    ax2.set_xlabel('Precio Unitario ($/kg)')
    ax2.set_ylabel('Porcentaje en Formulación (%)')
    ax2.set_title('Análisis Costo-Beneficio de Ingredientes')
    ax2.grid(True, alpha=0.3)
    
    # Añadir colorbar
    cbar = plt.colorbar(scatter, ax=ax2)
    cbar.set_label('Contribución al Costo ($/kg)')
    
    plt.tight_layout()
    return fig

def grafica_metricas_algoritmo(historico_metricas):
    """
    Genera gráfica de métricas del algoritmo a lo largo de las generaciones
    
    Args:
        historico_metricas: Lista de métricas por generación
        
    Returns:
        Figura de matplotlib
    """
    if not historico_metricas:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, 'No hay métricas disponibles', 
                ha='center', va='center', transform=ax.transAxes, fontsize=16)
        return fig
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    generaciones = [m["generacion"] for m in historico_metricas]
    
    # Gráfica 1: Evolución del fitness (mejor vs promedio)
    mejor_fitness = [m["mejor_fitness"] for m in historico_metricas]
    fitness_promedio = [m["fitness_promedio"] for m in historico_metricas]
    
    ax1.plot(generaciones, mejor_fitness, 'b-', linewidth=2, label='Mejor Fitness')
    ax1.plot(generaciones, fitness_promedio, 'r--', linewidth=1, label='Fitness Promedio')
    ax1.fill_between(generaciones, mejor_fitness, fitness_promedio, alpha=0.3)
    
    ax1.set_xlabel('Generación')
    ax1.set_ylabel('Fitness')
    ax1.set_title('Evolución del Fitness: Mejor vs Promedio')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Gráfica 2: Diversidad de la población
    diversidad = [m.get("diversidad", 0) for m in historico_metricas]
    fases = [m.get("fase", "inicial") for m in historico_metricas]
    
    # Colorear según fase
    colores_fase = {'inicial': 'green', 'intermedia': 'orange', 'final': 'red'}
    for i in range(len(generaciones)-1):
        color = colores_fase.get(fases[i], 'blue')
        ax2.plot(generaciones[i:i+2], diversidad[i:i+2], color=color, linewidth=2)
    
    ax2.set_xlabel('Generación')
    ax2.set_ylabel('Diversidad')
    ax2.set_title('Evolución de la Diversidad Poblacional')
    
    # Añadir leyenda de fases
    from matplotlib.lines import Line2D
    lineas_leyenda = [Line2D([0], [0], color=color, linewidth=2) 
                     for color in colores_fase.values()]
    ax2.legend(lineas_leyenda, colores_fase.keys())
    ax2.grid(True, alpha=0.3)
    
    # Gráfica 3: Evolución del costo
    if "mejor_costo" in historico_metricas[0]:
        mejor_costo = [m["mejor_costo"] for m in historico_metricas]
        costo_promedio = [m.get("costo_promedio", 0) for m in historico_metricas]
        
        ax3.plot(generaciones, mejor_costo, 'g-', linewidth=2, label='Mejor Costo')
        if any(c > 0 for c in costo_promedio):
            ax3.plot(generaciones, costo_promedio, 'g--', linewidth=1, label='Costo Promedio')
        
        ax3.set_xlabel('Generación')
        ax3.set_ylabel('Costo ($/kg)')
        ax3.set_title('Evolución del Costo')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
    else:
        ax3.text(0.5, 0.5, 'Datos de costo no disponibles', 
                ha='center', va='center', transform=ax3.transAxes)
    
    # Gráfica 4: Número de mejores individuos encontrados
    num_mejores = [m.get("num_mejores_encontrados", 0) for m in historico_metricas]
    
    ax4.step(generaciones, num_mejores, 'purple', linewidth=2, where='post')
    ax4.fill_between(generaciones, num_mejores, step='post', alpha=0.3, color='purple')
    
    ax4.set_xlabel('Generación')
    ax4.set_ylabel('Número de Mejores Soluciones')
    ax4.set_title('Acumulación de Mejores Soluciones')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

def configurar_estilo_graficas(estilo="seaborn"):
    """
    Configura el estilo global de las gráficas
    
    Args:
        estilo: Estilo a aplicar
    """
    try:
        if estilo == "seaborn":
            plt.style.use('seaborn-v0_8')
        else:
            plt.style.use(estilo)
    except:
        warnings.warn(f"No se pudo aplicar el estilo {estilo}, usando estilo por defecto")
    
    # Configuraciones globales
    plt.rcParams['figure.figsize'] = (12, 8)
    plt.rcParams['font.size'] = 10
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['axes.titlesize'] = 14
    plt.rcParams['legend.fontsize'] = 10
    plt.rcParams['xtick.labelsize'] = 10
    plt.rcParams['ytick.labelsize'] = 10

def exportar_todas_graficas(resultados, ingredientes_data, config_evaluacion=None, 
                           directorio="graficas", formato="png"):
    """
    Exporta todas las gráficas a archivos
    
    Args:
        resultados: Resultado del algoritmo genético
        ingredientes_data: Lista de datos de ingredientes
        config_evaluacion: Configuración de evaluación
        directorio: Directorio donde guardar las gráficas
        formato: Formato de archivo (png, pdf, svg)
    """
    import os
    
    # Crear directorio si no existe
    if not os.path.exists(directorio):
        os.makedirs(directorio)
    
    # Generar y guardar gráficas
    figuras = generar_graficas(resultados, ingredientes_data, config_evaluacion, False)
    
    for nombre, figura in figuras.items():
        if nombre != "error":
            archivo = os.path.join(directorio, f"{nombre}.{formato}")
            figura.savefig(archivo, dpi=300, bbox_inches='tight')
            print(f"Gráfica guardada: {archivo}")
    
    print(f"✅ Todas las gráficas exportadas a: {directorio}")

# Configurar estilo por defecto al importar
configurar_estilo_graficas()