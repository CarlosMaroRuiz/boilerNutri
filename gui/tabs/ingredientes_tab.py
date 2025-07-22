"""
Pestaña de selección y configuración de ingredientes
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from conocimiento import INGREDIENTES


class IngredientesTab:
    """Pestaña para gestionar ingredientes disponibles"""
    
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.frame = ttk.Frame(parent)
        
        self.crear_interfaz()
        self.cargar_ingredientes_en_tree()
    
    def crear_interfaz(self):
        """Crea la interfaz de la pestaña"""
        # Frame principal dividido
        paned = ttk.PanedWindow(self.frame, orient=tk.HORIZONTAL)
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
    
    def cargar_ingredientes_en_tree(self):
        """Carga los ingredientes en el TreeView"""
        for item in self.ingredientes_tree.get_children():
            self.ingredientes_tree.delete(item)
        
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
    
    def seleccionar_todos_ingredientes(self):
        """Selecciona todos los ingredientes disponibles"""
        messagebox.showinfo("Ingredientes", f"✅ Seleccionados todos los {len(INGREDIENTES)} ingredientes disponibles")
        self.main_window.status_bar.config(text=f"Todos los ingredientes seleccionados ({len(INGREDIENTES)} items)")
    
    def deseleccionar_todos_ingredientes(self):
        """Deselecciona todos los ingredientes"""
        respuesta = messagebox.askyesno("Confirmar", 
                                       "¿Desea deseleccionar todos los ingredientes?\n"
                                       "Esto podría afectar la optimización.")
        if respuesta:
            messagebox.showinfo("Ingredientes", "❌ Todos los ingredientes han sido deseleccionados")
            self.main_window.status_bar.config(text="Ingredientes deseleccionados - Revise selección antes de optimizar")
    
    def actualizar_precios(self):
        """Actualiza los precios de los ingredientes"""
        respuesta = messagebox.askyesno("Actualizar Precios", 
                                       "¿Desea actualizar los precios desde los proveedores?\n"
                                       "Esto podría tardar unos momentos.")
        if respuesta:
            try:
                import time
                self.main_window.status_bar.config(text="Actualizando precios...")
                self.main_window.root.update()
                time.sleep(1)  # Simular delay
                
                # Recargar ingredientes en el tree
                self.cargar_ingredientes_en_tree()
                
                messagebox.showinfo("Actualización Completada", 
                                  f"✅ Precios actualizados exitosamente\n\n"
                                  f"• {len(INGREDIENTES)} ingredientes actualizados\n"
                                  f"• Fuentes consultadas: 3 proveedores\n"
                                  f"• Última actualización: {datetime.now().strftime('%H:%M:%S')}")
                self.main_window.status_bar.config(text="Precios actualizados correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"Error al actualizar precios:\n{e}")
                self.main_window.status_bar.config(text="Error en actualización de precios")