"""
Pestaña de optimización con gráfica de evolución de fitness simplificada
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time

from config import ALGORITMO_CONFIG
from ..utils import generar_resultados_simulados
from utils.fitness_evolution import crear_grafica_fitness, crear_generador_datos


class OptimizacionTab:
    """Pestaña para ejecutar y monitorear la optimización"""
    
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.frame = ttk.Frame(parent)
        
        # Variables de control
        self.algoritmo_thread = None
        self.simulacion_activa = False
        self.fitness_chart = None
        self.data_generator = None
        
        self.crear_interfaz()
    
    def crear_interfaz(self):
        """Crea la interfaz de la pestaña"""
        # Frame principal
        main_frame = ttk.Frame(self.frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Configuración del algoritmo
        config_frame = ttk.LabelFrame(main_frame, text="Configuración del Algoritmo Genético", padding=10)
        config_frame.pack(fill=tk.X, pady=5)
        
        # Parámetros en dos filas
        # Primera fila
        fila1 = ttk.Frame(config_frame)
        fila1.pack(fill=tk.X, pady=2)
        
        ttk.Label(fila1, text="Población:").pack(side=tk.LEFT)
        ttk.Entry(fila1, textvariable=self.main_window.poblacion_var, width=10).pack(side=tk.LEFT, padx=(5,20))
        
        ttk.Label(fila1, text="Generaciones:").pack(side=tk.LEFT)
        ttk.Entry(fila1, textvariable=self.main_window.generaciones_var, width=10).pack(side=tk.LEFT, padx=(5,20))
        
        # Botones de control
        self.btn_iniciar = ttk.Button(fila1, text="🚀 Iniciar", command=self.iniciar_optimizacion)
        self.btn_iniciar.pack(side=tk.RIGHT, padx=5)
        
        self.btn_detener = ttk.Button(fila1, text="⏹️ Detener", command=self.detener_optimizacion, state=tk.DISABLED)
        self.btn_detener.pack(side=tk.RIGHT, padx=5)
        
        # Segunda fila - información
        fila2 = ttk.Frame(config_frame)
        fila2.pack(fill=tk.X, pady=(10,2))
        
        self.info_generacion = ttk.Label(fila2, text="Generación: 0/0")
        self.info_generacion.pack(side=tk.LEFT)
        
        self.info_fitness = ttk.Label(fila2, text="Mejor Fitness: --")
        self.info_fitness.pack(side=tk.LEFT, padx=(20,0))
        
        self.info_tiempo = ttk.Label(fila2, text="Tiempo: 00:00")
        self.info_tiempo.pack(side=tk.RIGHT)
        
        # Barra de progreso
        self.progreso_bar = ttk.Progressbar(config_frame, variable=self.main_window.progreso_var, maximum=100)
        self.progreso_bar.pack(fill=tk.X, pady=(10,0))
        
        # Frame para la gráfica de fitness
        grafica_frame = ttk.LabelFrame(main_frame, text="Evolución del Fitness", padding=5)
        grafica_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Crear gráfica de fitness
        try:
            self.fitness_chart = crear_grafica_fitness(grafica_frame, max_puntos=100)
            self.grafica_disponible = True
            print("✅ Gráfica de fitness creada exitosamente")
        except Exception as e:
            print(f"❌ Error creando gráfica: {e}")
            error_label = ttk.Label(grafica_frame, text="⚠️ Gráfica no disponible\nVerifique que matplotlib esté instalado")
            error_label.pack(expand=True)
            self.grafica_disponible = False
        
        # Botones de la gráfica
        botones_frame = ttk.Frame(grafica_frame)
        botones_frame.pack(fill=tk.X, pady=5)
        
        self.btn_exportar = ttk.Button(botones_frame, text="💾 Exportar Gráfica", command=self.exportar_grafica)
        self.btn_exportar.pack(side=tk.LEFT, padx=5)
        
        self.btn_limpiar = ttk.Button(botones_frame, text="🧹 Limpiar", command=self.limpiar_grafica)
        self.btn_limpiar.pack(side=tk.LEFT, padx=5)
        
        self.btn_metricas = ttk.Button(botones_frame, text="📊 Métricas", command=self.mostrar_metricas)
        self.btn_metricas.pack(side=tk.LEFT, padx=5)
        
        # Deshabilitar botones si no hay gráfica
        if not self.grafica_disponible:
            self.btn_exportar.config(state=tk.DISABLED)
            self.btn_limpiar.config(state=tk.DISABLED)
            self.btn_metricas.config(state=tk.DISABLED)
    
    def iniciar_optimizacion(self):
        """Inicia el proceso de optimización"""
        # Validar configuración
        if not self._validar_parametros():
            return
        
        # Preparar interfaz
        self.simulacion_activa = True
        self.btn_iniciar.config(state=tk.DISABLED)
        self.btn_detener.config(state=tk.NORMAL)
        
        # Limpiar gráfica anterior
        if self.grafica_disponible and self.fitness_chart:
            self.fitness_chart.limpiar()
        
        # Crear generador de datos
        self.data_generator = crear_generador_datos(fitness_inicial=0.2, fitness_objetivo=0.95)
        
        # Inicializar tiempo
        self.tiempo_inicio = time.time()
        
        # Ejecutar optimización en thread separado
        self.algoritmo_thread = threading.Thread(target=self._ejecutar_optimizacion, daemon=True)
        self.algoritmo_thread.start()
        
        self.main_window.status_bar.config(text="🔄 Optimización en progreso...")
        print("🚀 Optimización iniciada")
    
    def detener_optimizacion(self):
        """Detiene la optimización"""
        self.simulacion_activa = False
        self.btn_iniciar.config(state=tk.NORMAL)
        self.btn_detener.config(state=tk.DISABLED)
        
        self.main_window.status_bar.config(text="⏹️ Optimización detenida")
        messagebox.showinfo("Detenido", "Optimización detenida por el usuario")
    
    def _validar_parametros(self):
        """Valida que los parámetros estén correctos"""
        if not self.main_window.raza_var.get():
            messagebox.showerror("Error", "Seleccione una raza de pollos")
            return False
        
        if self.main_window.peso_actual_var.get() >= self.main_window.peso_objetivo_var.get():
            messagebox.showerror("Error", "El peso objetivo debe ser mayor al peso actual")
            return False
        
        poblacion = self.main_window.poblacion_var.get()
        generaciones = self.main_window.generaciones_var.get()
        
        if poblacion < 10 or poblacion > 1000:
            messagebox.showerror("Error", "La población debe estar entre 10 y 1000")
            return False
        
        if generaciones < 5 or generaciones > 500:
            messagebox.showerror("Error", "Las generaciones deben estar entre 5 y 500")
            return False
        
        return True
    
    def _ejecutar_optimizacion(self):
        """Ejecuta la simulación del algoritmo genético"""
        tamano_poblacion = self.main_window.poblacion_var.get()
        max_generaciones = self.main_window.generaciones_var.get()
        
        try:
            print(f"🧬 Ejecutando {max_generaciones} generaciones con población de {tamano_poblacion}")
            
            for generacion in range(max_generaciones):
                if not self.simulacion_activa:
                    print("⏹️ Optimización detenida por usuario")
                    break
                
                # Generar datos de la generación
                mejor, promedio, peor = self.data_generator.generar_poblacion(tamano_poblacion, max_generaciones)
                
                # Actualizar gráfica si está disponible
                if self.grafica_disponible and self.fitness_chart:
                    self.fitness_chart.agregar_punto(generacion, mejor, promedio, peor)
                
                # Actualizar interfaz en el hilo principal
                self.main_window.root.after(0, self._actualizar_interfaz, 
                                          generacion, max_generaciones, mejor, promedio, peor)
                
                # Pausa para simular procesamiento
                time.sleep(0.05)  # 50ms por generación
            
            # Completar optimización si no fue detenida
            if self.simulacion_activa:
                self.main_window.root.after(0, self._completar_optimizacion)
                
        except Exception as e:
            print(f"❌ Error en optimización: {e}")
            self.main_window.root.after(0, lambda: messagebox.showerror("Error", f"Error en optimización: {e}"))
    
    def _actualizar_interfaz(self, generacion, max_generaciones, mejor, promedio, peor):
        """Actualiza la interfaz con datos de la generación actual"""
        try:
            # Progreso
            progreso = (generacion + 1) / max_generaciones * 100
            self.main_window.progreso_var.set(progreso)
            
            # Información de generación
            self.info_generacion.config(text=f"Generación: {generacion + 1}/{max_generaciones}")
            self.info_fitness.config(text=f"Mejor Fitness: {mejor:.4f}")
            
            # Tiempo transcurrido
            tiempo_transcurrido = time.time() - self.tiempo_inicio
            minutos = int(tiempo_transcurrido // 60)
            segundos = int(tiempo_transcurrido % 60)
            self.info_tiempo.config(text=f"Tiempo: {minutos:02d}:{segundos:02d}")
            
        except Exception as e:
            print(f"Error actualizando interfaz: {e}")
    
    def _completar_optimizacion(self):
        """Completa el proceso de optimización"""
        self.simulacion_activa = False
        self.btn_iniciar.config(state=tk.NORMAL)
        self.btn_detener.config(state=tk.DISABLED)
        
        # Generar resultados simulados
        config = self._preparar_configuracion()
        self.main_window.resultados = generar_resultados_simulados(config)
        
        # Mostrar resultados
        self.main_window.tab_resultados.mostrar_resultados(self.main_window.resultados)
        self.main_window.notebook.select(3)  # Cambiar a pestaña de resultados
        
        # Mostrar métricas finales
        if self.grafica_disponible and self.fitness_chart:
            metricas = self.fitness_chart.obtener_metricas()
            if metricas:
                mensaje = (f"✅ Optimización completada\n\n"
                          f"📊 Resultados:\n"
                          f"• Generaciones: {metricas['total_generaciones']}\n"
                          f"• Mejor Fitness: {metricas['mejor_fitness_actual']:.4f}\n"
                          f"• Mejora Total: {metricas['mejora_total']:.4f}\n"
                          f"• Estado: {metricas['tendencia']}")
                messagebox.showinfo("Optimización Completada", mensaje)
        else:
            messagebox.showinfo("Optimización Completada", "✅ Optimización completada exitosamente")
        
        self.main_window.status_bar.config(text="✅ Optimización completada")
        print("✅ Optimización completada exitosamente")
    
    def _preparar_configuracion(self):
        """Prepara configuración para generar resultados"""
        from ..utils import preparar_configuracion_algoritmo
        return preparar_configuracion_algoritmo(self.main_window)
    
    def exportar_grafica(self):
        """Exporta la gráfica a un archivo"""
        if not self.grafica_disponible or not self.fitness_chart:
            messagebox.showwarning("Advertencia", "Gráfica no disponible")
            return
        
        from tkinter import filedialog
        
        archivo = filedialog.asksaveasfilename(
            title="Exportar Gráfica de Evolución",
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("PDF files", "*.pdf"),
                ("SVG files", "*.svg")
            ]
        )
        
        if archivo:
            if self.fitness_chart.exportar_grafica(archivo):
                messagebox.showinfo("Éxito", f"Gráfica exportada exitosamente a:\n{archivo}")
            else:
                messagebox.showerror("Error", "No se pudo exportar la gráfica")
    
    def limpiar_grafica(self):
        """Limpia la gráfica de evolución"""
        if self.grafica_disponible and self.fitness_chart:
            self.fitness_chart.limpiar()
            print("🧹 Gráfica limpiada")
        
        # Resetear información
        self.info_generacion.config(text="Generación: 0/0")
        self.info_fitness.config(text="Mejor Fitness: --")
        self.info_tiempo.config(text="Tiempo: 00:00")
        self.main_window.progreso_var.set(0)
    
    def mostrar_metricas(self):
        """Muestra las métricas actuales de la optimización"""
        if not self.grafica_disponible or not self.fitness_chart:
            messagebox.showwarning("Advertencia", "Gráfica no disponible")
            return
        
        metricas = self.fitness_chart.obtener_metricas()
        
        if not metricas:
            messagebox.showinfo("Métricas", "No hay datos disponibles\nEjecute una optimización primero")
            return
        
        # Crear ventana de métricas
        ventana = tk.Toplevel(self.main_window.root)
        ventana.title("Métricas de Evolución")
        ventana.geometry("400x300")
        ventana.resizable(False, False)
        
        # Contenido
        frame = ttk.Frame(ventana, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="📊 Métricas de Evolución", font=('Arial', 14, 'bold')).pack(pady=(0,20))
        
        info_text = f"""
        Generaciones Ejecutadas: {metricas.get('total_generaciones', 0)}
        
        Fitness Inicial: {metricas.get('mejor_fitness_inicial', 0):.4f}
        Fitness Actual: {metricas.get('mejor_fitness_actual', 0):.4f}
        Mejora Total: {metricas.get('mejora_total', 0):.4f}
        
        Promedio Actual: {metricas.get('promedio_actual', 0):.4f}
        Tendencia: {metricas.get('tendencia', 'N/A').title()}
        """
        
        ttk.Label(frame, text=info_text, justify=tk.LEFT, font=('Courier', 10)).pack(pady=10)
        
        ttk.Button(frame, text="Cerrar", command=ventana.destroy).pack(pady=20)
    
    def limpiar(self):
        """Limpia toda la pestaña (llamado desde ventana principal)"""
        if self.simulacion_activa:
            self.detener_optimizacion()
        
        self.limpiar_grafica()
        self.main_window.resultados = None
        
        if self.data_generator:
            self.data_generator.reset()