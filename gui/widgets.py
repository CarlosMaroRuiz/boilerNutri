"""
Widgets personalizados reutilizables
"""

import tkinter as tk
from tkinter import ttk
from conocimiento import INGREDIENTES


class TablaFormulacion(ttk.Frame):
    """Widget de tabla para mostrar el detalle de una formulación"""
    
    def __init__(self, parent, formulacion):
        super().__init__(parent)
        self.formulacion = formulacion
        
        self.crear_tabla()
    
    def crear_tabla(self):
        """Crea la tabla con el detalle de la formulación"""
        # Frame para la tabla
        tabla_frame = ttk.LabelFrame(self, text="Detalle de la Formulación", padding=5)
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
        for i, porcentaje in enumerate(self.formulacion['porcentajes']):
            if porcentaje > 0.001 and i < len(INGREDIENTES):
                ingrediente = INGREDIENTES[i]
                nombre = ingrediente.get('nombre', f'Ingrediente {i+1}')
                porcentaje_pct = porcentaje * 100
                cantidad_kg = porcentaje * 1000  # Por tonelada
                precio_kg = ingrediente.get('precio_base', 0)
                costo_total = cantidad_kg * precio_kg / 1000
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


class ProgressDialog(tk.Toplevel):
    """Diálogo de progreso para operaciones largas"""
    
    def __init__(self, parent, title="Procesando...", message="Por favor espere..."):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x150")
        self.resizable(False, False)
        
        # Centrar ventana
        self.transient(parent)
        self.grab_set()
        
        # Contenido
        ttk.Label(self, text=message, font=('Arial', 10)).pack(pady=20)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self, variable=self.progress_var, 
                                           maximum=100, length=350)
        self.progress_bar.pack(pady=10)
        
        self.status_label = ttk.Label(self, text="Iniciando...")
        self.status_label.pack(pady=5)
    
    def update_progress(self, value, status_text=""):
        """Actualiza el progreso"""
        self.progress_var.set(value)
        if status_text:
            self.status_label.config(text=status_text)
        self.update()