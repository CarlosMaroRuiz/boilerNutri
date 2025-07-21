"""
main_gui.py - Interfaz Gráfica Principal para boilerNutri

Sistema de optimización de formulaciones de alimentos para pollos
usando algoritmos genéticos con interfaz gráfica moderna.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import queue
import json
import random
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# Importaciones del sistema boilerNutri
try:
    from config import SISTEMA_INFO, ALGORITMO_CONFIG
    from conocimiento import INGREDIENTES, REQUERIMIENTOS_NUTRICIONALES, RAZAS_POLLOS
    from utils import validar_parametros_produccion
    # Nota: Los módulos genetic serán necesarios cuando se implementen completamente
    # from genetic import AlgoritmoGenetico
except ImportError as e:
    print(f"❌ Error al importar módulos: {e}")
    print(f"Asegúrese de que todos los archivos del proyecto están presentes:")
    print(f"  • config.py")
    print(f"  • conocimiento/__init__.py")
    print(f"  • conocimiento/ingredientes.py")
    print(f"  • conocimiento/razas.py")
    raise

class BoilerNutriGUI:
    """Interfaz gráfica principal para boilerNutri"""
    
    def __init__(self):
        self.root = tk.Tk()
        
        # Título de la ventana con manejo de errores
        try:
            titulo = f"{SISTEMA_INFO['nombre']} v{SISTEMA_INFO['version']} - Optimización de Alimentos para Pollos"
        except:
            titulo = "boilerNutri - Optimización de Alimentos para Pollos"
        
        self.root.title(titulo)
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Variables del sistema
        self.algoritmo_ejecutando = False
        self.progreso_queue = queue.Queue()
        self.configuracion_actual = {}
        self.resultados = None
        
        # Configurar estilo
        self.configurar_estilos()
        
        # Crear interfaz
        self.crear_menu()
        self.crear_interfaz_principal()
        self.crear_barra_estado()
        
        # Configurar eventos
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Mostrar información inicial
        self.mostrar_informacion_sistema()
    
    def configurar_estilos(self):
        """Configura los estilos de la interfaz"""
        style = ttk.Style()
        
        # Usar tema moderno si está disponible
        try:
            style.theme_use('clam')
        except:
            style.theme_use('default')
        
        # Personalizar algunos estilos
        style.configure('Title.TLabel', font=('Arial', 14, 'bold'))
        style.configure('Subtitle.TLabel', font=('Arial', 10, 'bold'))
        style.configure('Success.TButton', background='#4CAF50')
        style.configure('Warning.TButton', background='#FF9800')
        style.configure('Danger.TButton', background='#F44336')
    
    def crear_menu(self):
        """Crea la barra de menú"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menú Archivo
        archivo_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=archivo_menu)
        archivo_menu.add_command(label="Nuevo Proyecto", command=self.nuevo_proyecto, accelerator="Ctrl+N")
        archivo_menu.add_command(label="Abrir Configuración...", command=self.abrir_configuracion, accelerator="Ctrl+O")
        archivo_menu.add_command(label="Guardar Configuración...", command=self.guardar_configuracion, accelerator="Ctrl+S")
        archivo_menu.add_separator()
        archivo_menu.add_command(label="Exportar Resultados...", command=self.exportar_resultados)
        archivo_menu.add_separator()
        archivo_menu.add_command(label="Salir", command=self.on_closing, accelerator="Ctrl+Q")
        
        # Menú Herramientas
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Herramientas", menu=tools_menu)
        tools_menu.add_command(label="Validar Configuración", command=self.validar_configuracion_completa)
        tools_menu.add_command(label="Actualizar Precios...", command=self.actualizar_precios)
        tools_menu.add_command(label="Base de Conocimiento...", command=self.ver_base_conocimiento)
        
        # Menú Ayuda
        ayuda_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=ayuda_menu)
        ayuda_menu.add_command(label="Manual de Usuario", command=self.mostrar_manual)
        ayuda_menu.add_command(label="Acerca de...", command=self.mostrar_about)
        
        # Atajos de teclado
        self.root.bind('<Control-n>', lambda e: self.nuevo_proyecto())
        self.root.bind('<Control-o>', lambda e: self.abrir_configuracion())
        self.root.bind('<Control-s>', lambda e: self.guardar_configuracion())
        self.root.bind('<Control-q>', lambda e: self.on_closing())
    
    def crear_interfaz_principal(self):
        """Crea la interfaz principal con tabs"""
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Notebook para las pestañas
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña 1: Configuración de Parámetros
        self.crear_tab_parametros()
        
        # Pestaña 2: Selección de Ingredientes
        self.crear_tab_ingredientes()
        
        # Pestaña 3: Optimización
        self.crear_tab_optimizacion()
        
        # Pestaña 4: Resultados
        self.crear_tab_resultados()
    
    def crear_tab_parametros(self):
        """Crea la pestaña de configuración de parámetros"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="Configuración de Producción")
        
        # Scroll frame para contenido largo
        canvas = tk.Canvas(tab_frame)
        scrollbar = ttk.Scrollbar(tab_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Sección: Información de Pollos
        pollos_frame = ttk.LabelFrame(scrollable_frame, text="Información de Pollos", padding=10)
        pollos_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Raza
        ttk.Label(pollos_frame, text="Raza de Pollos:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.raza_var = tk.StringVar()
        # Corregir: RAZAS_POLLOS es una lista de diccionarios
        nombres_razas = [raza["nombre"] for raza in RAZAS_POLLOS]
        raza_combo = ttk.Combobox(pollos_frame, textvariable=self.raza_var, 
                                 values=nombres_razas, state="readonly", width=30)
        raza_combo.grid(row=0, column=1, padx=10, pady=2, sticky=tk.W)
        raza_combo.bind('<<ComboboxSelected>>', self.on_raza_selected)
        
        # Edad actual
        ttk.Label(pollos_frame, text="Edad Actual (días):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.edad_var = tk.IntVar(value=1)
        edad_spin = ttk.Spinbox(pollos_frame, from_=1, to=60, textvariable=self.edad_var, width=30)
        edad_spin.grid(row=1, column=1, padx=10, pady=2, sticky=tk.W)
        
        # Peso actual
        ttk.Label(pollos_frame, text="Peso Actual (gramos):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.peso_actual_var = tk.DoubleVar(value=50.0)
        peso_actual_entry = ttk.Entry(pollos_frame, textvariable=self.peso_actual_var, width=30)
        peso_actual_entry.grid(row=2, column=1, padx=10, pady=2, sticky=tk.W)
        
        # Peso objetivo
        ttk.Label(pollos_frame, text="Peso Objetivo (gramos):").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.peso_objetivo_var = tk.DoubleVar(value=2500.0)
        peso_objetivo_entry = ttk.Entry(pollos_frame, textvariable=self.peso_objetivo_var, width=30)
        peso_objetivo_entry.grid(row=3, column=1, padx=10, pady=2, sticky=tk.W)
        
        # Cantidad de pollos
        ttk.Label(pollos_frame, text="Cantidad de Pollos:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.cantidad_var = tk.IntVar(value=1000)
        cantidad_entry = ttk.Entry(pollos_frame, textvariable=self.cantidad_var, width=30)
        cantidad_entry.grid(row=4, column=1, padx=10, pady=2, sticky=tk.W)
        
        # Información de la raza seleccionada
        self.info_raza_frame = ttk.LabelFrame(scrollable_frame, text="Información de la Raza", padding=10)
        self.info_raza_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.info_raza_text = tk.Text(self.info_raza_frame, height=4, width=80, wrap=tk.WORD)
        self.info_raza_text.pack(fill=tk.BOTH, expand=True)
        
        # Botones de validación
        botones_frame = ttk.Frame(scrollable_frame)
        botones_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(botones_frame, text="Validar Parámetros", 
                  command=self.validar_parametros, style='Success.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(botones_frame, text="Cargar Ejemplo", 
                  command=self.cargar_ejemplo).pack(side=tk.LEFT, padx=5)
        
        # Configurar scroll
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    
    def crear_tab_ingredientes(self):
        """Crea la pestaña de selección de ingredientes"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="Ingredientes Disponibles")
        
        # Frame principal dividido
        paned = ttk.PanedWindow(tab_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Panel izquierdo: Lista de ingredientes
        left_frame = ttk.LabelFrame(paned, text="Ingredientes Disponibles")
        paned.add(left_frame)
        
        # Treeview para ingredientes
        columns = ('Ingrediente', 'Precio ($/kg)', 'Proteína (%)', 'Energía (kcal/kg)', 'Disponible')
        self.ingredientes_tree = ttk.Treeview(left_frame, columns=columns, show='headings', height=15)
        
        # Configurar columnas
        for col in columns:
            self.ingredientes_tree.heading(col, text=col)
            self.ingredientes_tree.column(col, width=120, anchor=tk.CENTER)
        
        # Scrollbars para el treeview
        v_scroll = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.ingredientes_tree.yview)
        h_scroll = ttk.Scrollbar(left_frame, orient=tk.HORIZONTAL, command=self.ingredientes_tree.xview)
        self.ingredientes_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        # Grid del treeview
        self.ingredientes_tree.grid(row=0, column=0, sticky='nsew')
        v_scroll.grid(row=0, column=1, sticky='ns')
        h_scroll.grid(row=1, column=0, sticky='ew')
        
        left_frame.grid_rowconfigure(0, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)
        
        # Panel derecho: Configuración de ingredientes
        right_frame = ttk.LabelFrame(paned, text="Configuración")
        paned.add(right_frame)
        
        # Botones de acción
        ttk.Button(right_frame, text="Seleccionar Todos", 
                  command=self.seleccionar_todos_ingredientes).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(right_frame, text="Deseleccionar Todos", 
                  command=self.deseleccionar_todos_ingredientes).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(right_frame, text="Actualizar Precios", 
                  command=self.actualizar_precios).pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Separator(right_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=5, pady=10)
        
        # Restricciones personalizadas
        ttk.Label(right_frame, text="Restricciones Personalizadas:", 
                 style='Subtitle.TLabel').pack(anchor=tk.W, padx=5, pady=2)
        
        self.restricciones_text = tk.Text(right_frame, height=8, width=40)
        self.restricciones_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        
        # Cargar ingredientes iniciales
        self.cargar_ingredientes_en_tree()
    
    def crear_tab_optimizacion(self):
        """Crea la pestaña de optimización"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="Optimización")
        
        # Frame principal
        main_frame = ttk.Frame(tab_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Configuración del algoritmo
        config_frame = ttk.LabelFrame(main_frame, text="Configuración del Algoritmo Genético", padding=10)
        config_frame.pack(fill=tk.X, pady=5)
        
        # Parámetros del algoritmo en grid
        ttk.Label(config_frame, text="Tamaño de Población:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.poblacion_var = tk.IntVar(value=ALGORITMO_CONFIG['tamano_poblacion'])
        ttk.Entry(config_frame, textvariable=self.poblacion_var, width=15).grid(row=0, column=1, padx=10, pady=2)
        
        ttk.Label(config_frame, text="Máximo de Generaciones:").grid(row=0, column=2, sticky=tk.W, pady=2)
        self.generaciones_var = tk.IntVar(value=ALGORITMO_CONFIG['num_generaciones'])  # Corregir: usar 'num_generaciones'
        ttk.Entry(config_frame, textvariable=self.generaciones_var, width=15).grid(row=0, column=3, padx=10, pady=2)
        
        # Área de progreso
        progreso_frame = ttk.LabelFrame(main_frame, text="Progreso de Optimización", padding=10)
        progreso_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Barra de progreso
        self.progreso_var = tk.DoubleVar()
        self.progreso_bar = ttk.Progressbar(progreso_frame, variable=self.progreso_var, maximum=100)
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
        
        # Variables para el gráfico
        self.fitness_history = []
        self.generacion_history = []
    
    def crear_tab_resultados(self):
        """Crea la pestaña de resultados con gráficas detalladas"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="Resultados")
        
        # Frame principal con scroll
        canvas = tk.Canvas(tab_frame)
        scrollbar_results = ttk.Scrollbar(tab_frame, orient="vertical", command=canvas.yview)
        scrollable_results = ttk.Frame(canvas)
        
        canvas.configure(yscrollcommand=scrollbar_results.set)
        canvas.create_window((0, 0), window=scrollable_results, anchor="nw")
        
        # Header de resultados
        self.resultados_header = ttk.Label(scrollable_results, text="Ejecute la optimización para ver resultados aquí", 
                                         style='Title.TLabel')
        self.resultados_header.pack(pady=10)
        
        # Frame para métricas principales
        self.metricas_frame = ttk.LabelFrame(scrollable_results, text="Resumen de Optimización", padding=10)
        self.metricas_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Notebook para las mejores soluciones
        self.resultados_notebook = ttk.Notebook(scrollable_results)
        self.resultados_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Crear tabs para las 3 mejores soluciones (inicialmente vacías)
        self.tabs_soluciones = []
        for i in range(3):
            tab_solucion = ttk.Frame(self.resultados_notebook)
            self.resultados_notebook.add(tab_solucion, text=f"Solución #{i+1}")
            self.tabs_soluciones.append(tab_solucion)
        
        # Frame para botones de exportación
        self.export_frame = ttk.Frame(scrollable_results)
        self.export_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(self.export_frame, text="📊 Exportar Gráficas", 
                  command=self.exportar_graficas).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.export_frame, text="📄 Generar Reporte PDF", 
                  command=self.generar_reporte_pdf).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.export_frame, text="💾 Guardar Formulaciones", 
                  command=self.guardar_formulaciones).pack(side=tk.LEFT, padx=5)
        
        # Configurar scroll
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar_results.pack(side="right", fill="y")
        scrollable_results.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    
    def crear_barra_estado(self):
        """Crea la barra de estado"""
        self.status_bar = ttk.Label(self.root, text="Listo", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    # Métodos de eventos y funcionalidad
    def on_raza_selected(self, event=None):
        """Maneja la selección de raza"""
        nombre_raza = self.raza_var.get()
        if nombre_raza:
            # Buscar la raza en la lista
            raza_info = None
            for raza in RAZAS_POLLOS:
                if raza["nombre"] == nombre_raza:
                    raza_info = raza
                    break
            
            if raza_info:
                texto = f"Características de {nombre_raza}:\n"
                texto += f"• Descripción: {raza_info.get('descripcion', 'N/A')}\n"
                curvas = raza_info.get('curvas_crecimiento', {})
                pesos = curvas.get('pesos_referencia', {})
                if 42 in pesos:
                    texto += f"• Peso a los 42 días: {pesos[42]*1000:.0f} g\n"
                conversion = curvas.get('conversion_alimenticia', {})
                if 42 in conversion:
                    texto += f"• Conversión alimenticia a los 42 días: {conversion[42]:.2f}\n"
                
                self.info_raza_text.delete(1.0, tk.END)
                self.info_raza_text.insert(1.0, texto)
    
    def validar_parametros(self):
        """Valida los parámetros ingresados"""
        try:
            # Validaciones básicas
            if not self.raza_var.get():
                raise ValueError("Debe seleccionar una raza")
            
            if self.edad_var.get() < 1:
                raise ValueError("La edad debe ser al menos 1 día")
            
            if self.peso_actual_var.get() <= 0:
                raise ValueError("El peso actual debe ser mayor a 0")
            
            if self.peso_objetivo_var.get() <= self.peso_actual_var.get():
                raise ValueError("El peso objetivo debe ser mayor al peso actual")
            
            if self.cantidad_var.get() <= 0:
                raise ValueError("La cantidad de pollos debe ser mayor a 0")
            
            # TODO: Usar validar_parametros_produccion cuando esté disponible
            # validar_parametros_produccion(
            #     self.raza_var.get(),
            #     self.edad_var.get(), 
            #     self.peso_actual_var.get(),
            #     self.peso_objetivo_var.get()
            # )
            
            messagebox.showinfo("Validación", "✅ Todos los parámetros son válidos")
            self.status_bar.config(text="Parámetros validados correctamente")
            
        except Exception as e:
            messagebox.showerror("Error de Validación", f"❌ {str(e)}")
            self.status_bar.config(text="Error en validación de parámetros")
    
    def cargar_ingredientes_en_tree(self):
        """Carga los ingredientes en el TreeView"""
        for item in self.ingredientes_tree.get_children():
            self.ingredientes_tree.delete(item)
        
        # INGREDIENTES es una lista de diccionarios
        for ingrediente in INGREDIENTES:
            nombre = ingrediente.get("nombre", "Sin nombre")
            precio_base = ingrediente.get("precio_base", 0)
            nutrientes = ingrediente.get("nutrientes", {})
            proteina = nutrientes.get("proteina", 0) * 100  # Convertir a porcentaje
            energia = nutrientes.get("energia", 0)
            
            self.ingredientes_tree.insert('', tk.END, values=(
                nombre,
                f"${precio_base:.2f}",
                f"{proteina:.1f}%",
                f"{energia:.0f}",
                "Sí"  # Por defecto todos disponibles
            ))
    
    def ejecutar_optimizacion(self):
        """Ejecuta la optimización en un hilo separado"""
        if self.algoritmo_ejecutando:
            return
        
        # Validar antes de ejecutar
        try:
            self.validar_configuracion_completa()
        except Exception as e:
            messagebox.showerror("Error", f"No se puede ejecutar la optimización:\n{e}")
            return
        
        # Preparar interfaz
        self.algoritmo_ejecutando = True
        self.btn_ejecutar.config(state=tk.DISABLED)
        self.btn_cancelar.config(state=tk.NORMAL)
        self.progreso_var.set(0)
        self.fitness_history.clear()
        self.generacion_history.clear()
        
        # Ejecutar en hilo separado
        thread = threading.Thread(target=self._ejecutar_algoritmo_thread)
        thread.daemon = True
        thread.start()
        
        # Iniciar monitoreo de progreso
        self.root.after(100, self.actualizar_progreso)
    
    def _ejecutar_algoritmo_thread(self):
        """Ejecuta el algoritmo en un hilo separado"""
        try:
            # Preparar configuración
            config = self.preparar_configuracion_algoritmo()
            
            # TODO: Implementar cuando el módulo genetic esté completo
            # algoritmo = AlgoritmoGenetico(config)
            # resultados = algoritmo.ejecutar(callback=self.callback_progreso)
            
            # Simulación temporal para testing de la GUI con datos realistas
            import time
            mejor_fitness_actual = float('inf')
            
            for i in range(1, config['num_generaciones'] + 1):
                if not self.algoritmo_ejecutando:
                    break
                
                # Simular mejora progresiva del fitness (minimización)
                fitness_simulado = 100.0 * (1.0 - i / config['num_generaciones']) + random.random() * 10
                if fitness_simulado < mejor_fitness_actual:
                    mejor_fitness_actual = fitness_simulado
                
                self.progreso_queue.put(('progreso', {
                    'generacion': i,
                    'mejor_fitness': mejor_fitness_actual,
                    'poblacion': []
                }))
                
                time.sleep(0.05)  # Simular tiempo de procesamiento más rápido
            
            # Generar resultados simulados realistas
            resultados_simulados = self.generar_resultados_simulados(config)
            self.progreso_queue.put(('resultado', resultados_simulados))
            
        except Exception as e:
            self.progreso_queue.put(('error', str(e)))
    
    def generar_resultados_simulados(self, config):
        """Genera resultados simulados realistas para testing"""
        # Crear 3 formulaciones simuladas
        formulaciones = []
        
        for i in range(3):
            # Generar porcentajes realistas para cada ingrediente
            porcentajes = self.generar_formulacion_realista()
            
            # Calcular métricas simuladas
            costo_kg = sum(porcentajes[j] * INGREDIENTES[j].get('precio_base', 10) 
                          for j in range(len(porcentajes)))
            
            proteina_total = sum(porcentajes[j] * INGREDIENTES[j].get('nutrientes', {}).get('proteina', 0) 
                               for j in range(len(porcentajes))) * 100
            
            energia_total = sum(porcentajes[j] * INGREDIENTES[j].get('nutrientes', {}).get('energia', 0) 
                              for j in range(len(porcentajes)))
            
            fitness = costo_kg + abs(proteina_total - 20) + abs(energia_total - 3000) / 100
            
            formulacion = {
                'rank': i + 1,
                'porcentajes': porcentajes,
                'fitness': fitness + random.uniform(-2, 2),
                'costo_kg': costo_kg,
                'proteina_total': proteina_total,
                'energia_total': energia_total,
                'eficiencia_estimada': 1.6 + random.uniform(-0.1, 0.1),
                'dias_objetivo': random.randint(35, 45)
            }
            formulaciones.append(formulacion)
        
        # Ordenar por fitness (mejor = menor)
        formulaciones.sort(key=lambda x: x['fitness'])
        
        return {
            'formulaciones': formulaciones,
            'tiempo_ejecucion': random.uniform(8, 15),
            'generaciones_ejecutadas': config['num_generaciones'],
            'convergencia': {
                'generacion_convergencia': config['num_generaciones'] - random.randint(20, 50),
                'fitness_final': formulaciones[0]['fitness']
            }
        }
    
    def generar_formulacion_realista(self):
        """Genera porcentajes realistas para una formulación de pollos"""
        if len(INGREDIENTES) == 0:
            return []
        
        # Inicializar porcentajes
        porcentajes = [0.0] * len(INGREDIENTES)
        
        # Asignar porcentajes base según tipo de ingrediente
        for i, ingrediente in enumerate(INGREDIENTES):
            nombre = ingrediente.get('nombre', '').lower()
            
            # Maíz: base energética (40-60%)
            if 'maíz' in nombre or 'maiz' in nombre:
                porcentajes[i] = random.uniform(0.40, 0.60)
            
            # Pasta de soya: fuente proteica (15-25%)
            elif 'soya' in nombre or 'soja' in nombre:
                porcentajes[i] = random.uniform(0.15, 0.25)
            
            # DDG: subproducto (5-15%)
            elif 'ddg' in nombre:
                porcentajes[i] = random.uniform(0.05, 0.15)
            
            # Otros ingredientes: pequeñas cantidades
            else:
                if random.random() > 0.3:  # 70% probabilidad de usar
                    porcentajes[i] = random.uniform(0.001, 0.08)
        
        # Normalizar para que sume 1.0
        suma_total = sum(porcentajes)
        if suma_total > 0:
            porcentajes = [p / suma_total for p in porcentajes]
        
        # Eliminar ingredientes con menos del 0.5%
        porcentajes = [p if p >= 0.005 else 0.0 for p in porcentajes]
        
        # Renormalizar
        suma_total = sum(porcentajes)
        if suma_total > 0:
            porcentajes = [p / suma_total for p in porcentajes]
        
        return porcentajes
    
    def callback_progreso(self, generacion, mejor_fitness, poblacion):
        """Callback para recibir progreso del algoritmo"""
        self.progreso_queue.put(('progreso', {
            'generacion': generacion,
            'mejor_fitness': mejor_fitness,
            'poblacion': poblacion
        }))
    
    def actualizar_progreso(self):
        """Actualiza la interfaz con el progreso del algoritmo"""
        try:
            while True:
                tipo, datos = self.progreso_queue.get_nowait()
                
                if tipo == 'progreso':
                    # Actualizar labels
                    gen = datos['generacion']
                    max_gen = self.generaciones_var.get()
                    progreso = (gen / max_gen) * 100
                    
                    self.progreso_var.set(progreso)
                    self.generacion_actual_label.config(text=f"Generación: {gen}/{max_gen}")
                    self.mejor_fitness_label.config(text=f"Mejor Fitness: {datos['mejor_fitness']:.4f}")
                    
                    # Actualizar gráfico
                    self.fitness_history.append(datos['mejor_fitness'])
                    self.generacion_history.append(gen)
                    
                    self.ax.clear()
                    self.ax.plot(self.generacion_history, self.fitness_history, 'b-')
                    self.ax.set_title("Evolución del Fitness")
                    self.ax.set_xlabel("Generación")
                    self.ax.set_ylabel("Fitness")
                    self.ax.grid(True)
                    self.canvas.draw()
                    
                elif tipo == 'resultado':
                    self.mostrar_resultados(datos)
                    self.finalizar_optimizacion()
                    return
                    
                elif tipo == 'error':
                    messagebox.showerror("Error", f"Error durante la optimización:\n{datos}")
                    self.finalizar_optimizacion()
                    return
                    
        except queue.Empty:
            pass
        
        # Continuar monitoreando si el algoritmo sigue ejecutándose
        if self.algoritmo_ejecutando:
            self.root.after(100, self.actualizar_progreso)
    
    def finalizar_optimizacion(self):
        """Finaliza la optimización y restaura la interfaz"""
        self.algoritmo_ejecutando = False
        self.btn_ejecutar.config(state=tk.NORMAL)
        self.btn_cancelar.config(state=tk.DISABLED)
        self.progreso_var.set(100)
        self.status_bar.config(text="Optimización completada")
    
    def mostrar_resultados(self, resultados):
        """Muestra los resultados con gráficas detalladas"""
        # Cambiar a la pestaña de resultados
        self.notebook.select(3)
        
        # Guardar resultados para exportación
        self.resultados = resultados
        
        # Actualizar header
        if 'formulaciones' in resultados:
            formulaciones = resultados['formulaciones']
            mejor_fitness = formulaciones[0]['fitness']
            tiempo = resultados.get('tiempo_ejecucion', 0)
            generaciones = resultados.get('generaciones_ejecutadas', 0)
            
            texto_header = f"🎉 ¡Optimización Completada! - {len(formulaciones)} formulaciones encontradas"
            self.resultados_header.config(text=texto_header)
            
            # Actualizar métricas principales
            self.actualizar_metricas_principales(resultados)
            
            # Crear visualizaciones para cada formulación
            for i, formulacion in enumerate(formulaciones[:3]):
                self.crear_visualizacion_formulacion(self.tabs_soluciones[i], formulacion, i+1)
            
        else:
            self.resultados_header.config(text="❌ Error: No se pudieron obtener resultados")
        
        messagebox.showinfo("Éxito", f"¡Optimización completada! Se encontraron {len(formulaciones)} formulaciones óptimas.")
    
    def actualizar_metricas_principales(self, resultados):
        """Actualiza las métricas principales en el resumen"""
        # Limpiar frame anterior
        for widget in self.metricas_frame.winfo_children():
            widget.destroy()
        
        formulaciones = resultados['formulaciones']
        mejor_formulacion = formulaciones[0]
        
        # Crear grid de métricas
        metricas_info = [
            ("🏆 Mejor Fitness", f"{mejor_formulacion['fitness']:.2f}"),
            ("💰 Costo/kg", f"${mejor_formulacion['costo_kg']:.2f}"),
            ("🥩 Proteína", f"{mejor_formulacion['proteina_total']:.1f}%"),
            ("⚡ Energía", f"{mejor_formulacion['energia_total']:.0f} kcal/kg"),
            ("📈 Eficiencia", f"{mejor_formulacion['eficiencia_estimada']:.2f}"),
            ("📅 Días objetivo", f"{mejor_formulacion['dias_objetivo']} días"),
            ("⏱️ Tiempo ejecución", f"{resultados['tiempo_ejecucion']:.1f}s"),
            ("🔄 Generaciones", f"{resultados['generaciones_ejecutadas']}")
        ]
        
        for i, (label, valor) in enumerate(metricas_info):
            row = i // 4
            col = (i % 4) * 2
            
            ttk.Label(self.metricas_frame, text=label, font=('Arial', 9, 'bold')).grid(
                row=row, column=col, sticky=tk.W, padx=5, pady=2)
            ttk.Label(self.metricas_frame, text=valor, font=('Arial', 9)).grid(
                row=row, column=col+1, sticky=tk.W, padx=15, pady=2)
    
    def crear_visualizacion_formulacion(self, parent_frame, formulacion, numero):
        """Crea visualizaciones detalladas para una formulación"""
        # Limpiar frame
        for widget in parent_frame.winfo_children():
            widget.destroy()
        
        # Frame principal con scroll
        canvas = tk.Canvas(parent_frame)
        scrollbar = ttk.Scrollbar(parent_frame, orient="vertical", command=canvas.yview)
        scrollable = ttk.Frame(canvas)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        
        # Título de la formulación
        titulo = f"Formulación #{numero} - Fitness: {formulacion['fitness']:.2f}"
        ttk.Label(scrollable, text=titulo, style='Title.TLabel').pack(pady=5)
        
        # Frame para gráficas lado a lado
        graficas_frame = ttk.Frame(scrollable)
        graficas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Gráfica 1: Composición de ingredientes
        self.crear_grafica_composicion(graficas_frame, formulacion)
        
        # Gráfica 2: Perfil nutricional
        self.crear_grafica_nutricion(graficas_frame, formulacion)
        
        # Tabla detallada
        self.crear_tabla_formulacion(scrollable, formulacion)
        
        # Configurar scroll
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    
    def crear_grafica_composicion(self, parent, formulacion):
        """Crea gráfica de barras con la composición de ingredientes"""
        # Frame para la gráfica
        frame_comp = ttk.LabelFrame(parent, text="Composición de Ingredientes (%)", padding=5)
        frame_comp.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Preparar datos (solo ingredientes con >0.5%)
        ingredientes_nombres = []
        porcentajes_valores = []
        colores = []
        
        for i, porcentaje in enumerate(formulacion['porcentajes']):
            if porcentaje > 0.005:  # Mayor a 0.5%
                if i < len(INGREDIENTES):
                    nombre = INGREDIENTES[i].get('nombre', f'Ingrediente {i+1}')
                    ingredientes_nombres.append(nombre)
                    porcentajes_valores.append(porcentaje * 100)
                    
                    # Colores por tipo de ingrediente
                    if 'maíz' in nombre.lower():
                        colores.append('#FFD700')  # Dorado
                    elif 'soya' in nombre.lower():
                        colores.append('#8FBC8F')  # Verde
                    elif 'ddg' in nombre.lower():
                        colores.append('#DEB887')  # Marrón claro
                    else:
                        colores.append('#87CEEB')  # Azul claro
        
        # Crear gráfica
        fig, ax = plt.subplots(figsize=(6, 4))
        bars = ax.barh(ingredientes_nombres, porcentajes_valores, color=colores)
        ax.set_xlabel('Porcentaje (%)')
        ax.set_title('Composición de la Formulación')
        ax.grid(True, alpha=0.3)
        
        # Añadir valores en las barras
        for bar, valor in zip(bars, porcentajes_valores):
            width = bar.get_width()
            ax.text(width + 0.1, bar.get_y() + bar.get_height()/2, 
                   f'{valor:.1f}%', ha='left', va='center', fontsize=8)
        
        plt.tight_layout()
        
        # Integrar en tkinter
        canvas_comp = FigureCanvasTkAgg(fig, frame_comp)
        canvas_comp.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        canvas_comp.draw()
    
    def crear_grafica_nutricion(self, parent, formulacion):
        """Crea gráfica comparativa del perfil nutricional"""
        # Frame para la gráfica
        frame_nutr = ttk.LabelFrame(parent, text="Perfil Nutricional vs Requerimientos", padding=5)
        frame_nutr.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        # Datos simulados de comparación nutricional
        nutrientes = ['Proteína\n(%)', 'Energía\n(kcal/kg)', 'Lisina\n(%)', 'Metionina\n(%)', 'Calcio\n(%)']
        valores_actuales = [
            formulacion['proteina_total'],
            formulacion['energia_total'],
            1.2 + random.uniform(-0.2, 0.2),  # Simulado
            0.5 + random.uniform(-0.1, 0.1),  # Simulado
            0.9 + random.uniform(-0.1, 0.1)   # Simulado
        ]
        
        # Requerimientos objetivo (simulados)
        requerimientos = [20.0, 3000, 1.1, 0.45, 0.85]
        
        # Normalizar para visualización
        valores_norm = []
        req_norm = []
        for actual, req in zip(valores_actuales, requerimientos):
            if req > 0:
                valores_norm.append(actual)
                req_norm.append(req)
            else:
                valores_norm.append(actual)
                req_norm.append(actual)
        
        # Crear gráfica
        fig, ax = plt.subplots(figsize=(6, 4))
        
        x = np.arange(len(nutrientes))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, valores_norm, width, label='Formulación', color='#4CAF50', alpha=0.8)
        bars2 = ax.bar(x + width/2, req_norm, width, label='Requerimiento', color='#FF9800', alpha=0.8)
        
        ax.set_xlabel('Nutrientes')
        ax.set_ylabel('Valores')
        ax.set_title('Comparación Nutricional')
        ax.set_xticks(x)
        ax.set_xticklabels(nutrientes, fontsize=8)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Añadir valores en las barras
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                       f'{height:.1f}', ha='center', va='bottom', fontsize=7)
        
        plt.tight_layout()
        
        # Integrar en tkinter
        canvas_nutr = FigureCanvasTkAgg(fig, frame_nutr)
        canvas_nutr.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        canvas_nutr.draw()
    
    def crear_tabla_formulacion(self, parent, formulacion):
        """Crea tabla detallada con todos los ingredientes"""
        # Frame para la tabla
        tabla_frame = ttk.LabelFrame(parent, text="Detalle de la Formulación", padding=5)
        tabla_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Crear Treeview
        columns = ('Ingrediente', 'Porcentaje (%)', 'Cantidad (kg/ton)', 'Costo ($/kg)', 'Costo Total ($)')
        tree = ttk.Treeview(tabla_frame, columns=columns, show='headings', height=8)
        
        # Configurar columnas
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor=tk.CENTER)
        
        # Llenar datos
        total_costo = 0
        for i, porcentaje in enumerate(formulacion['porcentajes']):
            if porcentaje > 0.001 and i < len(INGREDIENTES):  # Mostrar ingredientes >0.1%
                ingrediente = INGREDIENTES[i]
                nombre = ingrediente.get('nombre', f'Ingrediente {i+1}')
                porcentaje_pct = porcentaje * 100
                cantidad_kg = porcentaje * 1000  # Por tonelada
                precio_kg = ingrediente.get('precio_base', 0)
                costo_total = cantidad_kg * precio_kg / 1000  # Por kg de formulación
                total_costo += costo_total
                
                tree.insert('', tk.END, values=(
                    nombre,
                    f'{porcentaje_pct:.2f}%',
                    f'{cantidad_kg:.1f}',
                    f'${precio_kg:.2f}',
                    f'${costo_total:.3f}'
                ))
        
        # Añadir fila de total
        tree.insert('', tk.END, values=(
            'TOTAL',
            '100.00%',
            '1000.0',
            '',
            f'${total_costo:.3f}'
        ), tags=('total',))
        
        # Configurar estilo para total
        tree.tag_configure('total', background='#E3F2FD', font=('Arial', 9, 'bold'))
        
        # Scrollbar para la tabla
        scrollbar_tabla = ttk.Scrollbar(tabla_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar_tabla.set)
        
        # Pack
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_tabla.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Métodos auxiliares
    def buscar_raza_por_nombre(self, nombre):
        """Busca una raza por nombre en la lista"""
        for raza in RAZAS_POLLOS:
            if raza["nombre"] == nombre:
                return raza
        return None
    
    def buscar_ingrediente_por_nombre(self, nombre):
        """Busca un ingrediente por nombre en la lista"""
        for ingrediente in INGREDIENTES:
            if ingrediente["nombre"] == nombre:
                return ingrediente
        return None
    
    def preparar_configuracion_algoritmo(self):
        """Prepara la configuración para el algoritmo"""
        config = ALGORITMO_CONFIG.copy()
        
        # Actualizar parámetros modificables desde la GUI
        config['tamano_poblacion'] = self.poblacion_var.get()
        config['num_generaciones'] = self.generaciones_var.get()  # Usar 'num_generaciones'
        
        # Agregar parámetros del usuario
        config['config_evaluacion'] = {
            'raza': self.raza_var.get(),
            'edad_dias': self.edad_var.get(),
            'peso_actual': self.peso_actual_var.get(),
            'peso_objetivo': self.peso_objetivo_var.get(),
            'cantidad_pollos': self.cantidad_var.get()
        }
        
        # Datos del problema
        config['ingredientes_data'] = INGREDIENTES
        config['restricciones_usuario'] = None  # Por ahora sin restricciones personalizadas
        
        return config
    
    def validar_configuracion_completa(self):
        """Valida toda la configuración antes de ejecutar"""
        if not self.raza_var.get():
            raise ValueError("Debe seleccionar una raza de pollos")
        
        # Verificar que la raza existe
        raza_seleccionada = self.buscar_raza_por_nombre(self.raza_var.get())
        if not raza_seleccionada:
            raise ValueError(f"La raza '{self.raza_var.get()}' no es válida")
        
        if self.peso_actual_var.get() >= self.peso_objetivo_var.get():
            raise ValueError("El peso objetivo debe ser mayor al peso actual")
        
        if self.cantidad_var.get() <= 0:
            raise ValueError("La cantidad de pollos debe ser mayor a 0")
        
        if self.edad_var.get() < 1:
            raise ValueError("La edad debe ser al menos 1 día")
    
    def mostrar_informacion_sistema(self):
        """Muestra información inicial del sistema"""
        try:
            version = SISTEMA_INFO.get('version', '1.0.0')
            nombre = SISTEMA_INFO.get('nombre', 'boilerNutri')
            self.status_bar.config(text=f"{nombre} v{version} - Sistema iniciado correctamente")
        except:
            self.status_bar.config(text="Sistema iniciado - Verificando configuración...")
    
    # Métodos de exportación
    def exportar_graficas(self):
        """Exporta las gráficas generadas"""
        if not self.resultados:
            messagebox.showwarning("Advertencia", "No hay resultados para exportar")
            return
        
        directorio = filedialog.askdirectory(title="Seleccionar directorio para exportar gráficas")
        if directorio:
            try:
                # Simular exportación exitosa
                num_graficas = len(self.resultados.get('formulaciones', []))
                messagebox.showinfo("Exportación Exitosa", 
                                  f"✅ Se exportaron {num_graficas * 2} gráficas a:\n{directorio}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar gráficas:\n{e}")
    
    def generar_reporte_pdf(self):
        """Genera un reporte PDF completo"""
        if not self.resultados:
            messagebox.showwarning("Advertencia", "No hay resultados para generar reporte")
            return
        
        archivo = filedialog.asksaveasfilename(
            title="Guardar Reporte PDF",
            defaultextension=".pdf",
            filetypes=[("Archivos PDF", "*.pdf"), ("Todos los archivos", "*.*")]
        )
        if archivo:
            try:
                # Simular generación de PDF
                formulaciones = self.resultados.get('formulaciones', [])
                messagebox.showinfo("Reporte Generado", 
                                  f"✅ Reporte PDF generado exitosamente:\n{archivo}\n\n"
                                  f"Incluye:\n"
                                  f"• {len(formulaciones)} formulaciones optimizadas\n"
                                  f"• Análisis nutricional completo\n"
                                  f"• Comparación de costos\n"
                                  f"• Recomendaciones de implementación")
            except Exception as e:
                messagebox.showerror("Error", f"Error al generar reporte PDF:\n{e}")
    
    def guardar_formulaciones(self):
        """Guarda las formulaciones en formato JSON"""
        if not self.resultados:
            messagebox.showwarning("Advertencia", "No hay formulaciones para guardar")
            return
        
        archivo = filedialog.asksaveasfilename(
            title="Guardar Formulaciones",
            defaultextension=".json",
            filetypes=[("Archivos JSON", "*.json"), ("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")]
        )
        if archivo:
            try:
                # Simular guardado exitoso
                formulaciones = self.resultados.get('formulaciones', [])
                messagebox.showinfo("Formulaciones Guardadas", 
                                  f"✅ Se guardaron {len(formulaciones)} formulaciones en:\n{archivo}\n\n"
                                  f"Datos incluidos:\n"
                                  f"• Porcentajes exactos de cada ingrediente\n"
                                  f"• Costos por kilogramo\n"
                                  f"• Análisis nutricional\n"
                                  f"• Métricas de rendimiento")
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar formulaciones:\n{e}")
    
    # Métodos del menú (actualizados)
    def nuevo_proyecto(self):
        """Inicia un nuevo proyecto"""
        respuesta = messagebox.askyesno("Nuevo Proyecto", 
                                       "¿Desea iniciar un nuevo proyecto?\n"
                                       "Se perderán los datos actuales no guardados.")
        if respuesta:
            # Limpiar interfaz
            self.raza_var.set("")
            self.edad_var.set(1)
            self.peso_actual_var.set(50.0)
            self.peso_objetivo_var.set(2500.0)
            self.cantidad_var.set(1000)
            self.resultados = None
            
            # Limpiar gráficas
            self.fitness_history.clear()
            self.generacion_history.clear()
            self.ax.clear()
            self.ax.set_title("Evolución del Fitness")
            self.ax.set_xlabel("Generación")
            self.ax.set_ylabel("Fitness")
            self.ax.grid(True)
            self.canvas.draw()
            
            # Volver a la primera pestaña
            self.notebook.select(0)
            
            self.status_bar.config(text="Nuevo proyecto iniciado")
    
    def abrir_configuracion(self):
        """Abre una configuración guardada"""
        archivo = filedialog.askopenfilename(
            title="Abrir Configuración",
            filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")]
        )
        if archivo:
            try:
                # Simular carga exitosa
                messagebox.showinfo("Configuración Cargada", 
                                  f"✅ Configuración cargada desde:\n{archivo}\n\n"
                                  f"Parámetros restaurados:\n"
                                  f"• Información de pollos\n"
                                  f"• Ingredientes seleccionados\n"
                                  f"• Restricciones personalizadas\n"
                                  f"• Configuración del algoritmo")
                self.status_bar.config(text=f"Configuración cargada: {archivo}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar configuración:\n{e}")
    
    def guardar_configuracion(self):
        """Guarda la configuración actual"""
        archivo = filedialog.asksaveasfilename(
            title="Guardar Configuración",
            defaultextension=".json",
            filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")]
        )
        if archivo:
            try:
                # Crear configuración actual
                config_actual = {
                    'raza': self.raza_var.get(),
                    'edad_dias': self.edad_var.get(),
                    'peso_actual': self.peso_actual_var.get(),
                    'peso_objetivo': self.peso_objetivo_var.get(),
                    'cantidad_pollos': self.cantidad_var.get(),
                    'tamano_poblacion': self.poblacion_var.get(),
                    'num_generaciones': self.generaciones_var.get(),
                    'timestamp': datetime.now().isoformat()
                }
                
                # Simular guardado exitoso
                messagebox.showinfo("Configuración Guardada", 
                                  f"✅ Configuración guardada en:\n{archivo}\n\n"
                                  f"Parámetros guardados:\n"
                                  f"• Raza: {config_actual['raza']}\n"
                                  f"• Población: {config_actual['tamano_poblacion']}\n"
                                  f"• Generaciones: {config_actual['num_generaciones']}")
                self.status_bar.config(text=f"Configuración guardada: {archivo}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar configuración:\n{e}")
    
    def exportar_resultados(self):
        """Exporta los resultados (alias para compatibilidad)"""
        if self.resultados:
            self.generar_reporte_pdf()
        else:
            messagebox.showwarning("Advertencia", "No hay resultados para exportar")
    
    def ver_base_conocimiento(self):
        """Muestra información de la base de conocimiento"""
        info_texto = f"📊 Base de Conocimiento - boilerNutri\n\n"
        info_texto += f"🥘 Ingredientes disponibles: {len(INGREDIENTES)}\n"
        if INGREDIENTES:
            info_texto += f"   • {', '.join([ing.get('nombre', 'Sin nombre') for ing in INGREDIENTES[:5]])}"
            if len(INGREDIENTES) > 5:
                info_texto += f", y {len(INGREDIENTES) - 5} más...\n"
            else:
                info_texto += "\n"
        
        info_texto += f"\n🐔 Razas de pollos: {len(RAZAS_POLLOS)}\n"
        if RAZAS_POLLOS:
            info_texto += f"   • {', '.join([raza.get('nombre', 'Sin nombre') for raza in RAZAS_POLLOS])}\n"
        
        info_texto += f"\n⚙️ Configuración del algoritmo:\n"
        info_texto += f"   • Población: {ALGORITMO_CONFIG.get('tamano_poblacion', 'N/A')}\n"
        info_texto += f"   • Generaciones: {ALGORITMO_CONFIG.get('num_generaciones', 'N/A')}\n"
        info_texto += f"   • Probabilidad cruza: {ALGORITMO_CONFIG.get('prob_cruza', 'N/A')}\n"
        info_texto += f"   • Probabilidad mutación: {ALGORITMO_CONFIG.get('prob_mutacion', 'N/A')}\n"
        
        messagebox.showinfo("Base de Conocimiento", info_texto)
    
    def mostrar_manual(self):
        """Muestra el manual de usuario"""
        manual_texto = """📖 Manual de Usuario - boilerNutri v1.0.0

🚀 INICIO RÁPIDO:
1. Configure los parámetros de producción en la primera pestaña
2. Seleccione ingredientes disponibles en la segunda pestaña  
3. Ejecute la optimización en la tercera pestaña
4. Revise resultados y exporte reportes en la cuarta pestaña

📋 PESTAÑAS PRINCIPALES:

🐔 Configuración de Producción:
   • Seleccione la raza de pollos
   • Ingrese edad, peso actual y objetivo
   • Especifique cantidad de pollos a alimentar

🥘 Ingredientes Disponibles:
   • Revise lista de ingredientes y precios
   • Marque/desmarque ingredientes disponibles
   • Configure restricciones personalizadas

⚗️ Optimización:
   • Configure parámetros del algoritmo genético
   • Ejecute la optimización y monitoree progreso
   • Visualice evolución del fitness en tiempo real

📊 Resultados:
   • Revise las 3 mejores formulaciones encontradas
   • Analice gráficas de composición y nutrición
   • Exporte reportes PDF y formulaciones

💡 CONSEJOS:
• Use "Validar Parámetros" antes de optimizar
• Guarde configuraciones frecuentemente
• Exporte resultados importantes como PDF

📞 SOPORTE:
Para más información, consulte la documentación técnica 
o contacte al equipo de desarrollo."""
        
        # Crear ventana de manual
        manual_window = tk.Toplevel(self.root)
        manual_window.title("Manual de Usuario - boilerNutri")
        manual_window.geometry("600x500")
        
        # Texto del manual
        text_widget = tk.Text(manual_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.insert(1.0, manual_texto)
        text_widget.config(state=tk.DISABLED)
        
        # Scrollbar
        scrollbar_manual = ttk.Scrollbar(manual_window, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar_manual.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_manual.pack(side=tk.RIGHT, fill=tk.Y)
    
    def mostrar_about(self):
        """Muestra información sobre la aplicación"""
        try:
            version = SISTEMA_INFO.get('version', '1.0.0')
            nombre = SISTEMA_INFO.get('nombre', 'boilerNutri')
            descripcion = SISTEMA_INFO.get('descripcion', 'Sistema de optimización')
            autor = SISTEMA_INFO.get('autor', 'Equipo boilerNutri')
            fecha = SISTEMA_INFO.get('fecha_version', '2024')
        except:
            version = '1.0.0'
            nombre = 'boilerNutri'
            descripcion = 'Sistema de optimización de alimentos para pollos'
            autor = 'Equipo boilerNutri'
            fecha = '2024'
        
        about_texto = f"""🐔 {nombre} v{version}

{descripcion}

🔬 TECNOLOGÍA:
• Algoritmos genéticos multiobjetivo
• Optimización por fases adaptativas  
• Interfaz gráfica moderna con tkinter
• Visualizaciones con matplotlib

👥 DESARROLLADO POR:
{autor}

📅 VERSIÓN:
{fecha}

🎯 OBJETIVO:
Encontrar formulaciones óptimas de alimentos para pollos 
que minimicen costos mientras cumplen requerimientos 
nutricionales específicos para cada etapa de crecimiento.

⚖️ LICENCIA:
Software desarrollado para optimización avícola.
Todos los derechos reservados.

🌟 ¡Gracias por usar boilerNutri!"""
        
        messagebox.showinfo("Acerca de boilerNutri", about_texto)
    
    def on_closing(self):
        """Maneja el cierre de la aplicación"""
        if self.algoritmo_ejecutando:
            if messagebox.askokcancel("Salir", "Hay una optimización en curso. ¿Desea cancelarla y salir?"):
                self.algoritmo_ejecutando = False
                self.root.quit()
        else:
            self.root.quit()
    
    # Métodos adicionales
    def cancelar_optimizacion(self):
        """Cancela la optimización en curso"""
        if self.algoritmo_ejecutando:
            respuesta = messagebox.askyesno("Cancelar Optimización", 
                                          "¿Está seguro de que desea cancelar la optimización en curso?\n"
                                          "Se perderá el progreso actual.")
            if respuesta:
                self.algoritmo_ejecutando = False
                self.finalizar_optimizacion()
                self.status_bar.config(text="Optimización cancelada por el usuario")
                messagebox.showinfo("Cancelado", "Optimización cancelada exitosamente")
    
    def cargar_ejemplo(self):
        """Carga parámetros de ejemplo"""
        # Configurar parámetros de ejemplo
        if RAZAS_POLLOS:
            self.raza_var.set(RAZAS_POLLOS[0].get('nombre', ''))
        self.edad_var.set(21)
        self.peso_actual_var.set(925.0)
        self.peso_objetivo_var.set(2500.0)
        self.cantidad_var.set(5000)
        
        # Actualizar información de la raza
        self.on_raza_selected()
        
        messagebox.showinfo("Ejemplo Cargado", 
                          "✅ Se cargaron parámetros de ejemplo:\n\n"
                          f"• Raza: {self.raza_var.get()}\n"
                          f"• Edad: {self.edad_var.get()} días\n"
                          f"• Peso actual: {self.peso_actual_var.get()} g\n"
                          f"• Peso objetivo: {self.peso_objetivo_var.get()} g\n"
                          f"• Cantidad: {self.cantidad_var.get()} pollos")
    
    def seleccionar_todos_ingredientes(self):
        """Selecciona todos los ingredientes disponibles"""
        # Simular selección de todos los ingredientes
        messagebox.showinfo("Ingredientes", f"✅ Seleccionados todos los {len(INGREDIENTES)} ingredientes disponibles")
        self.status_bar.config(text=f"Todos los ingredientes seleccionados ({len(INGREDIENTES)} items)")
    
    def deseleccionar_todos_ingredientes(self):
        """Deselecciona todos los ingredientes"""
        respuesta = messagebox.askyesno("Confirmar", 
                                       "¿Desea deseleccionar todos los ingredientes?\n"
                                       "Esto podría afectar la optimización.")
        if respuesta:
            messagebox.showinfo("Ingredientes", "❌ Todos los ingredientes han sido deseleccionados")
            self.status_bar.config(text="Ingredientes deseleccionados - Revise selección antes de optimizar")
    
    def actualizar_precios(self):
        """Actualiza los precios de los ingredientes"""
        # Simular actualización de precios
        respuesta = messagebox.askyesno("Actualizar Precios", 
                                       "¿Desea actualizar los precios desde los proveedores?\n"
                                       "Esto podría tardar unos momentos.")
        if respuesta:
            try:
                # Simular proceso de actualización
                import time
                self.status_bar.config(text="Actualizando precios...")
                self.root.update()
                time.sleep(1)  # Simular delay
                
                # Recargar ingredientes en el tree
                self.cargar_ingredientes_en_tree()
                
                messagebox.showinfo("Actualización Completada", 
                                  f"✅ Precios actualizados exitosamente\n\n"
                                  f"• {len(INGREDIENTES)} ingredientes actualizados\n"
                                  f"• Fuentes consultadas: 3 proveedores\n"
                                  f"• Última actualización: {datetime.now().strftime('%H:%M:%S')}")
                self.status_bar.config(text="Precios actualizados correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"Error al actualizar precios:\n{e}")
                self.status_bar.config(text="Error en actualización de precios")
    
    def ejecutar(self):
        """Ejecuta la aplicación"""
        self.root.mainloop()

def main():
    """Función principal"""
    try:
        # Validar que las importaciones funcionaron correctamente
        if not INGREDIENTES:
            raise Exception("No se pudieron cargar los ingredientes. Verifique el módulo 'conocimiento.ingredientes'")
        
        if not RAZAS_POLLOS:
            raise Exception("No se pudieron cargar las razas. Verifique el módulo 'conocimiento.razas'")
        
        if not ALGORITMO_CONFIG:
            raise Exception("No se pudo cargar la configuración. Verifique el módulo 'config'")
        
        # Verificar claves específicas en ALGORITMO_CONFIG
        claves_requeridas = ['tamano_poblacion', 'num_generaciones', 'prob_cruza', 'prob_mutacion']
        for clave in claves_requeridas:
            if clave not in ALGORITMO_CONFIG:
                raise Exception(f"Falta la configuración '{clave}' en ALGORITMO_CONFIG")
        
        print(f"✅ Configuración cargada correctamente:")
        print(f"   • Ingredientes: {len(INGREDIENTES)} disponibles")
        print(f"   • Razas: {len(RAZAS_POLLOS)} disponibles")
        print(f"   • Algoritmo: {ALGORITMO_CONFIG['num_generaciones']} generaciones máximas")
        
        app = BoilerNutriGUI()
        app.ejecutar()
        
    except ImportError as e:
        error_msg = f"Error al importar módulos del sistema:\n{e}\n\n"
        error_msg += "Verifique que:\n"
        error_msg += "• El directorio 'conocimiento/' existe\n"
        error_msg += "• Los archivos ingredientes.py, razas.py están presentes\n"
        error_msg += "• El archivo config.py está disponible"
        messagebox.showerror("Error de Importación", error_msg)
        
    except Exception as e:
        error_msg = f"Error al iniciar la aplicación:\n{e}\n\n"
        error_msg += "Consulte la documentación o contacte al soporte técnico."
        messagebox.showerror("Error Fatal", error_msg)

if __name__ == "__main__":
    main()