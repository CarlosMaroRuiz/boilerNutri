"""
Pestaña de optimización con algoritmos genéticos
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
import time

from config import ALGORITMO_CONFIG
from ..utils import generar_resultados_simulados


class OptimizacionTab:
    """Pestaña para ejecutar y monitorear la optimización"""
    
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.frame = ttk.Frame(parent)
        
        self.crear_interfaz()
    
    def crear_interfaz(self):
        """Crea la interfaz de la pestaña"""
        # Frame principal
        main_frame = ttk.Frame(self.frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Configuración del algoritmo
        config_frame = ttk.LabelFrame(main_frame, text="Configuración del Algoritmo Genético", padding=10)
        config_frame.pack(fill=tk.X, pady=5)
        
        # Parámetros del algoritmo en grid
        ttk.Label(config_frame, text="Tamaño de Población:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(config_frame, textvariable=self.main_window.poblacion_var, width=15).grid(row=0, column=1, padx=10, pady=2)
        
        ttk.Label(config_frame, text="Máximo de Generaciones:").grid(row=0, column=2, sticky=tk.W, pady=2)
        ttk.Entry(config_frame, textvariable=self.main_window.generaciones_var, width=15).grid(row=0, column=3, padx=10, pady=2)
        
        # Área de progreso
        progreso_frame = ttk.LabelFrame(main_frame, text="Progreso de Optimización", padding=10)
        progreso_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Barra de progreso
        self.progreso_bar = ttk.Progressbar(progreso_frame, variable=self.main_window.progreso_var, maximum=100)
        self.progreso_bar.pack(fill=tk.X, pady=5)
        
        # Labels de información
        info_frame = ttk.Frame(progreso_frame)
        info_frame.pack(fill=tk.X, pady=5)
        
        self.generacion_actual_label = ttk.Label(info_frame, text="Generación: 0/0")
        self.generacion_actual_label.pack(side=tk.LEFT)
        
        self.mejor_fitness_label = ttk.Label(info_frame, text="Mejor Fitness: --")
        self.mejor_fitness_label.pack(side=tk.RIGHT)
        
        # Gráfico de evolución
        self.fig, self.ax = plt.subplots(figsize=(8, 4))
        self.ax.set_title("Evolución del Fitness")
        self.ax.set_xlabel("Generación")
        self.ax.set_ylabel("Fitness")
        self.ax.grid(True)
        
        self.canvas = FigureCanvasTkAgg(self.fig, progreso_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Botones de control
        botones_frame = ttk.Frame(main_frame)
        botones_frame.pack(fill=tk.X, pady=10)
        
        self.btn_ejecutar = ttk.Button(botones_frame, text="Ejecutar Optimización", 
                                      command=self.ejecutar_optimizacion, style='Success.TButton')
        self.btn_ejecutar.pack(side=tk.LEFT, padx=5)
        
        self.btn_cancelar = ttk.Button(botones_frame, text="Cancelar", 
                                      command=self.cancelar_optimizacion, state=tk.DISABLED, style='Danger.TButton')
        self.btn_cancelar.pack(side=tk.LEFT, padx=5)
    
    def ejecutar_optimizacion(self):
        """Ejecuta la optimización en un hilo separado"""
        if self.main_window.algoritmo_ejecutando:
            return
        
        # Validar antes de ejecutar
        try:
            self.main_window.tab_parametros.validar_parametros()
        except Exception as e:
            messagebox.showerror("Error", f"No se puede ejecutar la optimización:\n{e}")
            return
        
        # Preparar interfaz
        self.main_window.algoritmo_ejecutando = True
        self.btn_ejecutar.config(state=tk.DISABLED)
        self.btn_cancelar.config(state=tk.NORMAL)
        self.main_window.progreso_var.set(0)
        self.main_window.fitness_history.clear()
        self.main_window.generacion_history.clear()
        
        # Ejecutar en hilo separado
        thread = threading.Thread(target=self._ejecutar_algoritmo_thread)
        thread.daemon = True
        thread.start()
        
        # Iniciar monitoreo de progreso
        self.main_window.root.after(100, self.actualizar_progreso)
    
    def _ejecutar_algoritmo_thread(self):
        """Ejecuta el algoritmo en un hilo separado"""
        try:
            # Preparar configuración
            from ..utils import preparar_configuracion_algoritmo
            config = preparar_configuracion_algoritmo(self.main_window)
            
            # Simulación temporal para testing
            mejor_fitness_actual = float('inf')
            
            for i in range(1, config['num_generaciones'] + 1):
                if not self.main_window.algoritmo_ejecutando:
                    break
                
                # Simular mejora progresiva del fitness
                fitness_simulado = 100.0 * (1.0 - i / config['num_generaciones']) + random.random() * 10
                if fitness_simulado < mejor_fitness_actual:
                    mejor_fitness_actual = fitness_simulado
                
                self.main_window.progreso_queue.put(('progreso', {
                    'generacion': i,
                    'mejor_fitness': mejor_fitness_actual,
                    'poblacion': []
                }))
                
                time.sleep(0.05)
            
            # Generar resultados simulados
            resultados_simulados = generar_resultados_simulados(config)
            self.main_window.progreso_queue.put(('resultado', resultados_simulados))
            
        except Exception as e:
            self.main_window.progreso_queue.put(('error', str(e)))
    
    def actualizar_progreso(self):
        """Actualiza la interfaz con el progreso del algoritmo"""
        import queue
        
        try:
            while True:
                tipo, datos = self.main_window.progreso_queue.get_nowait()
                
                if tipo == 'progreso':
                    # Actualizar labels
                    gen = datos['generacion']
                    max_gen = self.main_window.generaciones_var.get()
                    progreso = (gen / max_gen) * 100
                    
                    self.main_window.progreso_var.set(progreso)
                    self.generacion_actual_label.config(text=f"Generación: {gen}/{max_gen}")
                    self.mejor_fitness_label.config(text=f"Mejor Fitness: {datos['mejor_fitness']:.4f}")
                    
                    # Actualizar gráfico
                    self.main_window.fitness_history.append(datos['mejor_fitness'])
                    self.main_window.generacion_history.append(gen)
                    
                    self.ax.clear()
                    self.ax.plot(self.main_window.generacion_history, self.main_window.fitness_history, 'b-')
                    self.ax.set_title("Evolución del Fitness")
                    self.ax.set_xlabel("Generación")
                    self.ax.set_ylabel("Fitness")
                    self.ax.grid(True)
                    self.canvas.draw()
                    
                elif tipo == 'resultado':
                    self.main_window.tab_resultados.mostrar_resultados(datos)
                    self.finalizar_optimizacion()
                    return
                    
                elif tipo == 'error':
                    messagebox.showerror("Error", f"Error durante la optimización:\n{datos}")
                    self.finalizar_optimizacion()
                    return
                    
        except queue.Empty:
            pass
        
        # Continuar monitoreando si el algoritmo sigue ejecutándose
        if self.main_window.algoritmo_ejecutando:
            self.main_window.root.after(100, self.actualizar_progreso)
    
    def finalizar_optimizacion(self):
        """Finaliza la optimización y restaura la interfaz"""
        self.main_window.algoritmo_ejecutando = False
        self.btn_ejecutar.config(state=tk.NORMAL)
        self.btn_cancelar.config(state=tk.DISABLED)
        self.main_window.progreso_var.set(100)
        self.main_window.status_bar.config(text="Optimización completada")
    
    def cancelar_optimizacion(self):
        """Cancela la optimización en curso"""
        if self.main_window.algoritmo_ejecutando:
            respuesta = messagebox.askyesno("Cancelar Optimización", 
                                          "¿Está seguro de que desea cancelar la optimización en curso?\n"
                                          "Se perderá el progreso actual.")
            if respuesta:
                self.main_window.algoritmo_ejecutando = False
                self.finalizar_optimizacion()
                self.main_window.status_bar.config(text="Optimización cancelada por el usuario")
                messagebox.showinfo("Cancelado", "Optimización cancelada exitosamente")
    
    def limpiar(self):
        """Limpia el gráfico y resetea el estado"""
        self.main_window.fitness_history.clear()
        self.main_window.generacion_history.clear()
        self.ax.clear()
        self.ax.set_title("Evolución del Fitness")
        self.ax.set_xlabel("Generación")
        self.ax.set_ylabel("Fitness")
        self.ax.grid(True)
        self.canvas.draw()
        self.main_window.progreso_var.set(0)
        self.generacion_actual_label.config(text="Generación: 0/0")
        self.mejor_fitness_label.config(text="Mejor Fitness: --")