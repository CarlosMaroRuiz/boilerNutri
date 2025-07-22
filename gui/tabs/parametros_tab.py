"""
Pestaña de configuración de parámetros de producción
"""

import tkinter as tk
from tkinter import ttk, messagebox
from conocimiento import RAZAS_POLLOS


class ParametrosTab:
    """Pestaña para configurar los parámetros de producción"""
    
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.frame = ttk.Frame(parent)
        
        self.crear_interfaz()
    
    def crear_interfaz(self):
        """Crea la interfaz de la pestaña"""
        # Scroll frame para contenido largo
        canvas = tk.Canvas(self.frame)
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Sección: Información de Pollos
        pollos_frame = ttk.LabelFrame(scrollable_frame, text="Información de Pollos", padding=10)
        pollos_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Raza
        ttk.Label(pollos_frame, text="Raza de Pollos:").grid(row=0, column=0, sticky=tk.W, pady=2)
        nombres_razas = [raza["nombre"] for raza in RAZAS_POLLOS]
        raza_combo = ttk.Combobox(pollos_frame, textvariable=self.main_window.raza_var, 
                                 values=nombres_razas, state="readonly", width=30)
        raza_combo.grid(row=0, column=1, padx=10, pady=2, sticky=tk.W)
        raza_combo.bind('<<ComboboxSelected>>', self.on_raza_selected)
        
        # Edad actual
        ttk.Label(pollos_frame, text="Edad Actual (días):").grid(row=1, column=0, sticky=tk.W, pady=2)
        edad_spin = ttk.Spinbox(pollos_frame, from_=1, to=60, 
                               textvariable=self.main_window.edad_var, width=30)
        edad_spin.grid(row=1, column=1, padx=10, pady=2, sticky=tk.W)
        
        # Peso actual
        ttk.Label(pollos_frame, text="Peso Actual (gramos):").grid(row=2, column=0, sticky=tk.W, pady=2)
        peso_actual_entry = ttk.Entry(pollos_frame, 
                                     textvariable=self.main_window.peso_actual_var, width=30)
        peso_actual_entry.grid(row=2, column=1, padx=10, pady=2, sticky=tk.W)
        
        # Peso objetivo
        ttk.Label(pollos_frame, text="Peso Objetivo (gramos):").grid(row=3, column=0, sticky=tk.W, pady=2)
        peso_objetivo_entry = ttk.Entry(pollos_frame, 
                                       textvariable=self.main_window.peso_objetivo_var, width=30)
        peso_objetivo_entry.grid(row=3, column=1, padx=10, pady=2, sticky=tk.W)
        
        # Cantidad de pollos
        ttk.Label(pollos_frame, text="Cantidad de Pollos:").grid(row=4, column=0, sticky=tk.W, pady=2)
        cantidad_entry = ttk.Entry(pollos_frame, 
                                  textvariable=self.main_window.cantidad_var, width=30)
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
    
    def on_raza_selected(self, event=None):
        """Maneja la selección de raza"""
        nombre_raza = self.main_window.raza_var.get()
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
            if not self.main_window.raza_var.get():
                raise ValueError("Debe seleccionar una raza")
            
            if self.main_window.edad_var.get() < 1:
                raise ValueError("La edad debe ser al menos 1 día")
            
            if self.main_window.peso_actual_var.get() <= 0:
                raise ValueError("El peso actual debe ser mayor a 0")
            
            if self.main_window.peso_objetivo_var.get() <= self.main_window.peso_actual_var.get():
                raise ValueError("El peso objetivo debe ser mayor al peso actual")
            
            if self.main_window.cantidad_var.get() <= 0:
                raise ValueError("La cantidad de pollos debe ser mayor a 0")
            
            messagebox.showinfo("Validación", "✅ Todos los parámetros son válidos")
            self.main_window.status_bar.config(text="Parámetros validados correctamente")
            
        except Exception as e:
            messagebox.showerror("Error de Validación", f"❌ {str(e)}")
            self.main_window.status_bar.config(text="Error en validación de parámetros")
    
    def cargar_ejemplo(self):
        """Carga parámetros de ejemplo"""
        if RAZAS_POLLOS:
            self.main_window.raza_var.set(RAZAS_POLLOS[0].get('nombre', ''))
        self.main_window.edad_var.set(21)
        self.main_window.peso_actual_var.set(925.0)
        self.main_window.peso_objetivo_var.set(2500.0)
        self.main_window.cantidad_var.set(5000)
        
        # Actualizar información de la raza
        self.on_raza_selected()
        
        messagebox.showinfo("Ejemplo Cargado", 
                          "✅ Se cargaron parámetros de ejemplo:\n\n"
                          f"• Raza: {self.main_window.raza_var.get()}\n"
                          f"• Edad: {self.main_window.edad_var.get()} días\n"
                          f"• Peso actual: {self.main_window.peso_actual_var.get()} g\n"
                          f"• Peso objetivo: {self.main_window.peso_objetivo_var.get()} g\n"
                          f"• Cantidad: {self.main_window.cantidad_var.get()} pollos")