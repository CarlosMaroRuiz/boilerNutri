"""
Módulo simplificado para visualización de evolución de fitness
Enfocado únicamente en mostrar la evolución del algoritmo genético
"""

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from collections import deque


class FitnessEvolutionChart:
    """
    Gráfica simple para mostrar la evolución del fitness
    """
    
    def __init__(self, parent_frame, max_puntos=100):
        self.parent_frame = parent_frame
        self.max_puntos = max_puntos
        
        # Datos de seguimiento
        self.generaciones = []
        self.mejor_fitness = []
        self.promedio_fitness = []
        self.peor_fitness = []
        
        # Configurar matplotlib
        plt.style.use('default')
        self.fig, self.ax = plt.subplots(1, 1, figsize=(10, 6))
        self.fig.patch.set_facecolor('white')
        
        # Configurar ejes
        self.ax.set_title('Evolución del Fitness del Algoritmo Genético', fontsize=14, fontweight='bold')
        self.ax.set_xlabel('Generación')
        self.ax.set_ylabel('Valor de Fitness')
        self.ax.grid(True, alpha=0.3)
        
        # Líneas de la gráfica
        self.line_mejor, = self.ax.plot([], [], 'g-', linewidth=2.5, label='Mejor Fitness', marker='o', markersize=3)
        self.line_promedio, = self.ax.plot([], [], 'b-', linewidth=1.5, label='Fitness Promedio')
        self.line_peor, = self.ax.plot([], [], 'r-', linewidth=1, alpha=0.7, label='Peor Fitness')
        
        # Área de relleno entre mejor y peor
        self.fill_area = None
        
        # Leyenda
        self.ax.legend(loc='lower right')
        
        # Canvas para tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, parent_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        
        plt.tight_layout()
        self.canvas.draw()
    
    def agregar_punto(self, generacion, mejor, promedio, peor):
        """
        Agrega un nuevo punto a la gráfica
        
        Args:
            generacion: Número de generación
            mejor: Mejor fitness de la generación
            promedio: Fitness promedio de la generación  
            peor: Peor fitness de la generación
        """
        try:
            # Agregar nuevos datos
            self.generaciones.append(generacion)
            self.mejor_fitness.append(mejor)
            self.promedio_fitness.append(promedio)
            self.peor_fitness.append(peor)
            
            # Mantener solo los últimos N puntos para performance
            if len(self.generaciones) > self.max_puntos:
                self.generaciones = self.generaciones[-self.max_puntos:]
                self.mejor_fitness = self.mejor_fitness[-self.max_puntos:]
                self.promedio_fitness = self.promedio_fitness[-self.max_puntos:]
                self.peor_fitness = self.peor_fitness[-self.max_puntos:]
            
            # Actualizar gráfica
            self._actualizar_grafica()
            
        except Exception as e:
            print(f"Error agregando punto: {e}")
    
    def _actualizar_grafica(self):
        """Actualiza la visualización de la gráfica"""
        try:
            if len(self.generaciones) == 0:
                return
            
            # Actualizar líneas
            self.line_mejor.set_data(self.generaciones, self.mejor_fitness)
            self.line_promedio.set_data(self.generaciones, self.promedio_fitness)
            self.line_peor.set_data(self.generaciones, self.peor_fitness)
            
            # Actualizar área de relleno
            if self.fill_area:
                self.fill_area.remove()
            self.fill_area = self.ax.fill_between(self.generaciones, self.mejor_fitness, self.peor_fitness, 
                                                 alpha=0.2, color='gray', label='Rango de Fitness')
            
            # Ajustar límites de ejes
            if len(self.generaciones) >= 2:
                # Eje X
                margen_x = max(1, (max(self.generaciones) - min(self.generaciones)) * 0.02)
                self.ax.set_xlim(min(self.generaciones) - margen_x, max(self.generaciones) + margen_x)
                
                # Eje Y
                todos_fitness = self.mejor_fitness + self.promedio_fitness + self.peor_fitness
                if todos_fitness:
                    y_min, y_max = min(todos_fitness), max(todos_fitness)
                    if y_max != y_min:
                        margen_y = (y_max - y_min) * 0.1
                        self.ax.set_ylim(y_min - margen_y, y_max + margen_y)
                    else:
                        self.ax.set_ylim(y_min - 0.1, y_max + 0.1)
            
            # Redibujar
            self.canvas.draw_idle()
            
        except Exception as e:
            print(f"Error actualizando gráfica: {e}")
    
    def limpiar(self):
        """Limpia todos los datos y reinicia la gráfica"""
        try:
            # Limpiar datos
            self.generaciones.clear()
            self.mejor_fitness.clear()
            self.promedio_fitness.clear()
            self.peor_fitness.clear()
            
            # Limpiar líneas
            self.line_mejor.set_data([], [])
            self.line_promedio.set_data([], [])
            self.line_peor.set_data([], [])
            
            # Remover área de relleno
            if self.fill_area:
                self.fill_area.remove()
                self.fill_area = None
            
            # Resetear límites de ejes
            self.ax.set_xlim(0, 10)
            self.ax.set_ylim(0, 1)
            
            # Redibujar
            self.canvas.draw()
            print("✅ Gráfica de fitness limpiada")
            
        except Exception as e:
            print(f"Error limpiando gráfica: {e}")
    
    def obtener_metricas(self):
        """
        Obtiene métricas básicas de la evolución
        
        Returns:
            dict: Métricas calculadas
        """
        if not self.mejor_fitness:
            return {}
        
        try:
            return {
                'total_generaciones': len(self.generaciones),
                'mejor_fitness_actual': self.mejor_fitness[-1],
                'mejor_fitness_inicial': self.mejor_fitness[0],
                'mejora_total': self.mejor_fitness[-1] - self.mejor_fitness[0],
                'promedio_actual': self.promedio_fitness[-1],
                'tendencia': 'mejorando' if len(self.mejor_fitness) > 1 and self.mejor_fitness[-1] > self.mejor_fitness[-2] else 'estable'
            }
        except Exception as e:
            print(f"Error calculando métricas: {e}")
            return {}
    
    def exportar_grafica(self, archivo):
        """
        Exporta la gráfica a un archivo
        
        Args:
            archivo: Ruta donde guardar el archivo
        
        Returns:
            bool: True si se guardó correctamente
        """
        try:
            self.fig.savefig(archivo, dpi=300, bbox_inches='tight', 
                           facecolor='white', edgecolor='none')
            print(f"✅ Gráfica exportada a: {archivo}")
            return True
        except Exception as e:
            print(f"❌ Error exportando gráfica: {e}")
            return False


class FitnessDataGenerator:
    """
    Generador mejorado de datos de fitness para simulación
    """
    
    def __init__(self, fitness_inicial=0.3, fitness_objetivo=0.95, ruido=0.05):
        self.fitness_inicial = fitness_inicial
        self.fitness_objetivo = fitness_objetivo
        self.ruido = ruido
        self.generacion_actual = 0
        self.mejor_historico = fitness_inicial
        self.estancamiento = 0
    
    def generar_poblacion(self, tamano_poblacion, max_generaciones):
        """
        Genera datos realistas de una población para una generación
        
        Args:
            tamano_poblacion: Número de individuos en la población
            max_generaciones: Total de generaciones planeadas
            
        Returns:
            tuple: (mejor_fitness, promedio_fitness, peor_fitness)
        """
        try:
            # Progreso basado en generación actual
            progreso = min(self.generacion_actual / max_generaciones, 1.0)
            
            # Fitness base que mejora gradualmente
            fitness_base = self.fitness_inicial + (self.fitness_objetivo - self.fitness_inicial) * progreso
            
            # Generar población con distribución realista
            poblacion_fitness = []
            
            for i in range(tamano_poblacion):
                if i == 0:  # Mejor individuo
                    fitness = min(fitness_base + np.random.uniform(0.05, 0.15), self.fitness_objetivo)
                    # Evitar que el mejor baje
                    fitness = max(fitness, self.mejor_historico)
                    self.mejor_historico = max(self.mejor_historico, fitness)
                elif i < tamano_poblacion * 0.2:  # Elite (top 20%)
                    fitness = fitness_base + np.random.uniform(0, 0.1)
                elif i < tamano_poblacion * 0.6:  # Población media
                    fitness = fitness_base + np.random.uniform(-0.1, 0.05)
                else:  # Población baja
                    fitness = fitness_base + np.random.uniform(-0.2, 0)
                
                # Agregar ruido realista
                fitness += np.random.normal(0, self.ruido)
                
                # Clamp valores
                fitness = max(0.1, min(fitness, 1.0))
                poblacion_fitness.append(fitness)
            
            # Ordenar descendente
            poblacion_fitness.sort(reverse=True)
            
            # Calcular métricas
            mejor = poblacion_fitness[0]
            promedio = np.mean(poblacion_fitness)
            peor = poblacion_fitness[-1]
            
            # Actualizar contador
            self.generacion_actual += 1
            
            # Simular convergencia
            if abs(mejor - self.mejor_historico) < 0.001:
                self.estancamiento += 1
            else:
                self.estancamiento = 0
            
            return mejor, promedio, peor
            
        except Exception as e:
            print(f"Error generando población: {e}")
            return 0.5, 0.4, 0.3
    
    def reset(self):
        """Reinicia el generador"""
        self.generacion_actual = 0
        self.mejor_historico = self.fitness_inicial
        self.estancamiento = 0


def crear_grafica_fitness(parent_frame, max_puntos=100):
    """
    Función de conveniencia para crear una gráfica de fitness
    
    Args:
        parent_frame: Frame de tkinter donde mostrar la gráfica
        max_puntos: Máximo número de puntos a mostrar
        
    Returns:
        FitnessEvolutionChart: Instancia de la gráfica
    """
    try:
        return FitnessEvolutionChart(parent_frame, max_puntos)
    except Exception as e:
        print(f"❌ Error creando gráfica de fitness: {e}")
        return None


def crear_generador_datos(fitness_inicial=0.3, fitness_objetivo=0.9):
    """
    Función de conveniencia para crear un generador de datos
    
    Args:
        fitness_inicial: Fitness inicial de la población
        fitness_objetivo: Fitness objetivo a alcanzar
        
    Returns:
        FitnessDataGenerator: Instancia del generador
    """
    return FitnessDataGenerator(fitness_inicial, fitness_objetivo)