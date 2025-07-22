"""
Ventana principal de la aplicación boilerNutri
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import queue
from datetime import datetime

# Importaciones del sistema boilerNutri
from config import SISTEMA_INFO, ALGORITMO_CONFIG
from conocimiento import INGREDIENTES, REQUERIMIENTOS_NUTRICIONALES, RAZAS_POLLOS
from utils import validar_parametros_produccion

# Importaciones de la GUI
from .tabs import (
    ParametrosTab, 
    IngredientesTab, 
    OptimizacionTab, 
    ResultadosTab
)
from .dialogs import ManualDialog, BaseConocimientoDialog
from .utils import preparar_configuracion_algoritmo


class BoilerNutriGUI:
    """Interfaz gráfica principal para boilerNutri"""
    
    def __init__(self):
        self.root = tk.Tk()
        
        # Título de la ventana
        try:
            titulo = f"{SISTEMA_INFO['nombre']} v{SISTEMA_INFO['version']} - Optimización de Alimentos para Pollos"
        except:
            titulo = "boilerNutri - Optimización de Alimentos para Pollos"
        
        self.root.title(titulo)
        self.root.geometry("1400x900")
        self.root.minsize(1000, 700)

        self.root.state('zoomed')
        
        # Variables del sistema
        self.algoritmo_ejecutando = False
        self.progreso_queue = queue.Queue()
        self.configuracion_actual = {}
        self.resultados = None
        
        # Variables de configuración
        self.init_variables()
        
        # Configurar estilo
        self.configurar_estilos()
        
        # Crear interfaz
        self.crear_menu()
        self.crear_interfaz_principal()
        self.crear_barra_estado()
        
        # Configurar eventos
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Inicializar tabs
        self.init_tabs()
        
        # Mostrar información inicial
        self.mostrar_informacion_sistema()
    
    def init_variables(self):
        """Inicializa las variables de la interfaz"""
        # Variables de configuración de pollos
        self.raza_var = tk.StringVar()
        self.edad_var = tk.IntVar(value=1)
        self.peso_actual_var = tk.DoubleVar(value=50.0)
        self.peso_objetivo_var = tk.DoubleVar(value=2500.0)
        self.cantidad_var = tk.IntVar(value=1000)
        
        # Variables del algoritmo
        self.poblacion_var = tk.IntVar(value=ALGORITMO_CONFIG['tamano_poblacion'])
        self.generaciones_var = tk.IntVar(value=ALGORITMO_CONFIG['num_generaciones'])
        self.progreso_var = tk.DoubleVar()
        
        # Historial para gráficas
        self.fitness_history = []
        self.generacion_history = []
    
    def configurar_estilos(self):
        """Configura los estilos de la interfaz"""
        style = ttk.Style()
        
        try:
            style.theme_use('clam')
        except:
            style.theme_use('default')
        
        # Personalizar estilos
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
    
    def init_tabs(self):
        """Inicializa las pestañas"""
        # Pestaña 1: Configuración de Parámetros
        self.tab_parametros = ParametrosTab(self.notebook, self)
        self.notebook.add(self.tab_parametros.frame, text="Configuración de Producción")
        
        # Pestaña 2: Selección de Ingredientes
        self.tab_ingredientes = IngredientesTab(self.notebook, self)
        self.notebook.add(self.tab_ingredientes.frame, text="Ingredientes Disponibles")
        
        # Pestaña 3: Optimización
        self.tab_optimizacion = OptimizacionTab(self.notebook, self)
        self.notebook.add(self.tab_optimizacion.frame, text="Optimización")
        
        # Pestaña 4: Resultados
        self.tab_resultados = ResultadosTab(self.notebook, self)
        self.notebook.add(self.tab_resultados.frame, text="Resultados")
    
    def crear_barra_estado(self):
        """Crea la barra de estado"""
        self.status_bar = ttk.Label(self.root, text="Listo", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def mostrar_informacion_sistema(self):
        """Muestra información inicial del sistema"""
        try:
            version = SISTEMA_INFO.get('version', '1.0.0')
            nombre = SISTEMA_INFO.get('nombre', 'boilerNutri')
            self.status_bar.config(text=f"{nombre} v{version} - Sistema iniciado correctamente")
        except:
            self.status_bar.config(text="Sistema iniciado - Verificando configuración...")
    
    # Métodos de menú
    def nuevo_proyecto(self):
        """Inicia un nuevo proyecto"""
        respuesta = messagebox.askyesno("Nuevo Proyecto", 
                                       "¿Desea iniciar un nuevo proyecto?\n"
                                       "Se perderán los datos actuales no guardados.")
        if respuesta:
            # Limpiar variables
            self.raza_var.set("")
            self.edad_var.set(1)
            self.peso_actual_var.set(50.0)
            self.peso_objetivo_var.set(2500.0)
            self.cantidad_var.set(1000)
            self.resultados = None
            
            # Limpiar tabs
            self.tab_optimizacion.limpiar()
            self.tab_resultados.limpiar()
            
            # Volver a la primera pestaña
            self.notebook.select(0)
            
            self.status_bar.config(text="Nuevo proyecto iniciado")
    
    def abrir_configuracion(self):
        """Abre una configuración guardada"""
        from tkinter import filedialog
        import json
        
        archivo = filedialog.askopenfilename(
            title="Abrir Configuración",
            filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")]
        )
        if archivo:
            try:
                with open(archivo, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Cargar configuración
                self.raza_var.set(config.get('raza', ''))
                self.edad_var.set(config.get('edad_dias', 1))
                self.peso_actual_var.set(config.get('peso_actual', 50))
                self.peso_objetivo_var.set(config.get('peso_objetivo', 2500))
                self.cantidad_var.set(config.get('cantidad_pollos', 1000))
                self.poblacion_var.set(config.get('tamano_poblacion', ALGORITMO_CONFIG['tamano_poblacion']))
                self.generaciones_var.set(config.get('num_generaciones', ALGORITMO_CONFIG['num_generaciones']))
                
                messagebox.showinfo("Configuración Cargada", 
                                  f"✅ Configuración cargada desde:\n{archivo}")
                self.status_bar.config(text=f"Configuración cargada: {archivo}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar configuración:\n{e}")
    
    def guardar_configuracion(self):
        """Guarda la configuración actual"""
        from tkinter import filedialog
        import json
        
        archivo = filedialog.asksaveasfilename(
            title="Guardar Configuración",
            defaultextension=".json",
            filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")]
        )
        if archivo:
            try:
                config = {
                    'raza': self.raza_var.get(),
                    'edad_dias': self.edad_var.get(),
                    'peso_actual': self.peso_actual_var.get(),
                    'peso_objetivo': self.peso_objetivo_var.get(),
                    'cantidad_pollos': self.cantidad_var.get(),
                    'tamano_poblacion': self.poblacion_var.get(),
                    'num_generaciones': self.generaciones_var.get(),
                    'timestamp': datetime.now().isoformat()
                }
                
                with open(archivo, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo("Configuración Guardada", 
                                  f"✅ Configuración guardada en:\n{archivo}")
                self.status_bar.config(text=f"Configuración guardada: {archivo}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar configuración:\n{e}")
    
    def exportar_resultados(self):
        """Exporta los resultados"""
        if self.resultados:
            self.tab_resultados.generar_reporte_pdf()
        else:
            messagebox.showwarning("Advertencia", "No hay resultados para exportar")
    
    def validar_configuracion_completa(self):
        """Valida toda la configuración antes de ejecutar"""
        try:
            self.tab_parametros.validar_parametros()
            messagebox.showinfo("Validación", "✅ Configuración validada correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"Error en la configuración:\n{e}")
    
    def actualizar_precios(self):
        """Actualiza los precios de los ingredientes"""
        self.tab_ingredientes.actualizar_precios()
    
    def ver_base_conocimiento(self):
        """Muestra información de la base de conocimiento"""
        dialog = BaseConocimientoDialog(self.root)
    
    def mostrar_manual(self):
        """Muestra el manual de usuario"""
        dialog = ManualDialog(self.root)
    
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
- Algoritmos genéticos multiobjetivo
- Optimización por fases adaptativas  
- Interfaz gráfica moderna con tkinter
- Visualizaciones con matplotlib

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
    
    def ejecutar(self):
        """Ejecuta la aplicación"""
        self.root.mainloop()