"""
Widgets personalizados reutilizables para boilerNutri
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
        tabla_frame = ttk.LabelFrame(self, text="Detalle de la Formulación", padding=3)
        tabla_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=3)
        
        # Frame para búsqueda/filtrado
        search_frame = ttk.Frame(tabla_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(search_frame, text="Buscar:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind('<KeyRelease>', self.filtrar_tabla)
        
        # Mostrar total de ingredientes
        self.total_label = ttk.Label(search_frame, text="")
        self.total_label.pack(side=tk.RIGHT, padx=5)
        
        # Crear Treeview con altura ajustable
        columns = ('Ingrediente', '(%)', 'kg/ton', '$/kg', 'Total $')
        self.tree = ttk.Treeview(tabla_frame, columns=columns, show='headings', height=12)
        
        # Configurar columnas más estrechas
        self.tree.heading('Ingrediente', text='Ingrediente', command=lambda: self.ordenar_columna('Ingrediente'))
        self.tree.column('Ingrediente', width=180, anchor=tk.W)
        
        self.tree.heading('(%)', text='%', command=lambda: self.ordenar_columna('(%)'))
        self.tree.column('(%)', width=60, anchor=tk.CENTER)
        
        self.tree.heading('kg/ton', text='kg/ton', command=lambda: self.ordenar_columna('kg/ton'))
        self.tree.column('kg/ton', width=70, anchor=tk.CENTER)
        
        self.tree.heading('$/kg', text='$/kg', command=lambda: self.ordenar_columna('$/kg'))
        self.tree.column('$/kg', width=60, anchor=tk.CENTER)
        
        self.tree.heading('Total $', text='Total $', command=lambda: self.ordenar_columna('Total $'))
        self.tree.column('Total $', width=70, anchor=tk.CENTER)
        
        # Estilo de fuente más pequeño
        style = ttk.Style()
        style.configure("Treeview", font=('Arial', 8))
        style.configure("Treeview.Heading", font=('Arial', 8, 'bold'))
        
        # Scrollbar para la tabla
        scrollbar_tabla = ttk.Scrollbar(tabla_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar_tabla.set)
        
        # Grid
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_tabla.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind para selección
        self.tree.bind('<Double-Button-1>', self.on_double_click)
        
        # Frame de resumen - CREAR ANTES de cargar_datos()
        resumen_frame = ttk.Frame(tabla_frame)
        resumen_frame.pack(fill=tk.X, pady=5)
        
        self.resumen_label = ttk.Label(resumen_frame, font=('Arial', 9, 'bold'))
        self.resumen_label.pack()
        
        # AHORA cargar datos
        self.cargar_datos()
    
    def cargar_datos(self):
        """Carga los datos en la tabla"""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Variables para totales
        total_costo = 0
        total_proteina = 0
        total_energia = 0
        num_ingredientes = 0
        
        # Datos para la tabla
        self.datos_tabla = []
        
        for i, porcentaje in enumerate(self.formulacion['porcentajes']):
            if porcentaje > 0.001 and i < len(INGREDIENTES):
                ingrediente = INGREDIENTES[i]
                nombre = ingrediente.get('nombre', f'Ingrediente {i+1}')
                porcentaje_pct = porcentaje * 100
                cantidad_kg = porcentaje * 1000  # Por tonelada
                precio_kg = ingrediente.get('precio_base', 0)
                costo_total = cantidad_kg * precio_kg / 1000
                total_costo += costo_total
                
                # Calcular contribución nutricional
                nutrientes = ingrediente.get('nutrientes', {})
                proteina_contrib = porcentaje * nutrientes.get('proteina', 0) * 100
                energia_contrib = porcentaje * nutrientes.get('energia', 0)
                
                total_proteina += proteina_contrib
                total_energia += energia_contrib
                num_ingredientes += 1
                
                # Guardar datos
                self.datos_tabla.append({
                    'nombre': nombre,
                    'porcentaje': porcentaje_pct,
                    'cantidad': cantidad_kg,
                    'precio': precio_kg,
                    'costo': costo_total,
                    'proteina': proteina_contrib,
                    'energia': energia_contrib
                })
                
                # Insertar en tree
                self.tree.insert('', tk.END, values=(
                    nombre,
                    f'{porcentaje_pct:.2f}%',
                    f'{cantidad_kg:.1f}',
                    f'${precio_kg:.2f}',
                    f'${costo_total:.3f}'
                ))
        
        # Añadir fila de total
        self.tree.insert('', tk.END, values=(
            'TOTAL',
            '100.00%',
            '1000.0',
            '',
            f'${total_costo:.3f}'
        ), tags=('total',))
        
        # Configurar estilo para total
        self.tree.tag_configure('total', background='#E3F2FD', font=('Arial', 9, 'bold'))
        
        # Actualizar labels
        self.total_label.config(text=f"Total: {num_ingredientes} ingredientes")
        self.resumen_label.config(
            text=f"Costo Total: ${total_costo:.3f}/kg | "
            f"Proteína Total: {total_proteina:.1f}% | "
            f"Energía Total: {total_energia:.0f} kcal/kg"
        )
    
    def filtrar_tabla(self, event=None):
        """Filtra la tabla según el texto de búsqueda"""
        busqueda = self.search_var.get().lower()
        
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Recargar con filtro
        total_costo_filtrado = 0
        num_mostrados = 0
        
        for datos in self.datos_tabla:
            if busqueda in datos['nombre'].lower() or not busqueda:
                self.tree.insert('', tk.END, values=(
                    datos['nombre'],
                    f"{datos['porcentaje']:.2f}%",
                    f"{datos['cantidad']:.1f}",
                    f"${datos['precio']:.2f}",
                    f"${datos['costo']:.3f}"
                ))
                total_costo_filtrado += datos['costo']
                num_mostrados += 1
        
        # Añadir total filtrado si hay búsqueda
        if busqueda and num_mostrados > 0:
            self.tree.insert('', tk.END, values=(
                f'SUBTOTAL ({num_mostrados} items)',
                '',
                '',
                '',
                f'${total_costo_filtrado:.3f}'
            ), tags=('total',))
        elif not busqueda:
            # Total general
            self.tree.insert('', tk.END, values=(
                'TOTAL',
                '100.00%',
                '1000.0',
                '',
                f'${sum(d["costo"] for d in self.datos_tabla):.3f}'
            ), tags=('total',))
    
    def ordenar_columna(self, col):
        """Ordena la tabla por la columna seleccionada"""
        # Obtener datos actuales
        datos = []
        for child in self.tree.get_children()[:-1]:  # Excluir la fila TOTAL
            datos.append(self.tree.item(child)['values'])
        
        # Determinar índice de columna
        col_indices = {'Ingrediente': 0, '(%)': 1, 'kg/ton': 2, '$/kg': 3, 'Total $': 4}
        col_idx = col_indices.get(col, 0)
        
        # Función de ordenamiento
        def sort_key(item):
            value = item[col_idx]
            if col_idx == 0:  # Nombre
                return value
            else:  # Valores numéricos
                # Extraer número de strings como "12.5%" o "$10.50"
                import re
                match = re.search(r'[\d.]+', str(value))
                return float(match.group()) if match else 0
        
        # Verificar si el atributo existe, si no, crearlo
        sort_attr = f'_sort_reverse_{col}'
        if not hasattr(self, sort_attr):
            setattr(self, sort_attr, False)
        
        # Ordenar
        datos.sort(key=sort_key, reverse=getattr(self, sort_attr))
        
        # Alternar orden para próximo click
        setattr(self, sort_attr, not getattr(self, sort_attr))
        
        # Recargar tabla ordenada
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for valores in datos:
            self.tree.insert('', tk.END, values=valores)
        
        # Re-añadir fila total
        total_costo = sum(d['costo'] for d in self.datos_tabla)
        self.tree.insert('', tk.END, values=(
            'TOTAL',
            '100.00%',
            '1000.0',
            '',
            f'${total_costo:.3f}'
        ), tags=('total',))
    
    def on_double_click(self, event):
        """Maneja doble click en un ingrediente"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            valores = item['values']
            if valores[0] != 'TOTAL' and not str(valores[0]).startswith('SUBTOTAL'):
                # Mostrar información detallada del ingrediente
                self.mostrar_detalle_ingrediente(valores[0])
    
    def mostrar_detalle_ingrediente(self, nombre_ingrediente):
        """Muestra información detallada de un ingrediente"""
        # Buscar el ingrediente
        ingrediente_info = None
        for ing in INGREDIENTES:
            if ing['nombre'] == nombre_ingrediente:
                ingrediente_info = ing
                break
        
        if not ingrediente_info:
            return
        
        # Crear ventana de detalle
        detalle_window = tk.Toplevel(self)
        detalle_window.title(f"Detalle: {nombre_ingrediente}")
        detalle_window.geometry("400x500")
        
        # Frame principal
        main_frame = ttk.Frame(detalle_window, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(main_frame, text=nombre_ingrediente, 
                 font=('Arial', 12, 'bold')).pack(pady=5)
        
        # Información general
        info_frame = ttk.LabelFrame(main_frame, text="Información General", padding=10)
        info_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(info_frame, text=f"Precio Base: ${ingrediente_info.get('precio_base', 0):.2f}/kg").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Categoría: {ingrediente_info.get('categoria', 'N/A')}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Disponibilidad: {'Sí' if ingrediente_info.get('disponible', True) else 'No'}").pack(anchor=tk.W)
        
        # Información nutricional
        nutri_frame = ttk.LabelFrame(main_frame, text="Información Nutricional", padding=10)
        nutri_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Crear texto con información nutricional
        nutri_text = tk.Text(nutri_frame, height=15, width=45, wrap=tk.WORD)
        nutri_text.pack(fill=tk.BOTH, expand=True)
        
        # Llenar información nutricional
        nutrientes = ingrediente_info.get('nutrientes', {})
        texto = "Composición Nutricional:\n" + "="*40 + "\n\n"
        
        # Nutrientes principales
        texto += f"Proteína: {nutrientes.get('proteina', 0)*100:.2f}%\n"
        texto += f"Energía: {nutrientes.get('energia', 0):.0f} kcal/kg\n"
        texto += f"Fibra: {nutrientes.get('fibra', 0)*100:.2f}%\n"
        texto += f"Grasa: {nutrientes.get('grasa', 0)*100:.2f}%\n\n"
        
        # Aminoácidos
        texto += "Aminoácidos:\n" + "-"*20 + "\n"
        texto += f"Lisina: {nutrientes.get('lisina', 0)*100:.3f}%\n"
        texto += f"Metionina: {nutrientes.get('metionina', 0)*100:.3f}%\n"
        texto += f"Treonina: {nutrientes.get('treonina', 0)*100:.3f}%\n"
        texto += f"Triptófano: {nutrientes.get('triptofano', 0)*100:.3f}%\n\n"
        
        # Minerales
        texto += "Minerales:\n" + "-"*20 + "\n"
        texto += f"Calcio: {nutrientes.get('calcio', 0)*100:.3f}%\n"
        texto += f"Fósforo: {nutrientes.get('fosforo', 0)*100:.3f}%\n"
        texto += f"Sodio: {nutrientes.get('sodio', 0)*100:.3f}%\n"
        
        nutri_text.insert(1.0, texto)
        nutri_text.config(state=tk.DISABLED)
        
        # Botón cerrar
        ttk.Button(main_frame, text="Cerrar", 
                  command=detalle_window.destroy).pack(pady=10)
        
        # Centrar ventana
        detalle_window.transient(self.winfo_toplevel())
        detalle_window.grab_set()


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
        
        # Botón cancelar
        self.cancel_button = ttk.Button(self, text="Cancelar", command=self.cancelar)
        self.cancel_button.pack(pady=5)
        
        self.cancelado = False
        
        # Centrar en pantalla
        self.update_idletasks()
        x = (self.winfo_screenwidth() - self.winfo_width()) // 2
        y = (self.winfo_screenheight() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
    
    def update_progress(self, value, status_text=""):
        """Actualiza el progreso"""
        self.progress_var.set(value)
        if status_text:
            self.status_label.config(text=status_text)
        self.update()
    
    def cancelar(self):
        """Marca como cancelado y cierra"""
        self.cancelado = True
        self.destroy()


class IngredienteSelector(tk.Toplevel):
    """Diálogo para seleccionar ingredientes disponibles"""
    
    def __init__(self, parent, ingredientes_actuales=None):
        super().__init__(parent)
        self.title("Seleccionar Ingredientes Disponibles")
        self.geometry("600x500")
        
        self.ingredientes_seleccionados = ingredientes_actuales or []
        self.resultado = None
        
        self.crear_interfaz()
        
        # Centrar ventana
        self.transient(parent)
        self.grab_set()
    
    def crear_interfaz(self):
        """Crea la interfaz del selector"""
        # Frame principal
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Instrucciones
        ttk.Label(main_frame, text="Seleccione los ingredientes disponibles para la optimización:",
                 font=('Arial', 10)).pack(pady=5)
        
        # Frame con scroll para checkboxes
        canvas = tk.Canvas(main_frame, height=350)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Checkboxes para cada ingrediente
        self.check_vars = {}
        
        # Agrupar por categoría
        categorias = {}
        for ing in INGREDIENTES:
            cat = ing.get('categoria', 'Otros')
            if cat not in categorias:
                categorias[cat] = []
            categorias[cat].append(ing)
        
        # Crear checkboxes por categoría
        for categoria, ingredientes in sorted(categorias.items()):
            # Frame de categoría
            cat_frame = ttk.LabelFrame(scrollable_frame, text=categoria, padding=5)
            cat_frame.pack(fill=tk.X, padx=5, pady=5)
            
            for ing in sorted(ingredientes, key=lambda x: x['nombre']):
                var = tk.BooleanVar(value=ing['nombre'] in self.ingredientes_seleccionados)
                self.check_vars[ing['nombre']] = var
                
                # Checkbox con información
                check_frame = ttk.Frame(cat_frame)
                check_frame.pack(fill=tk.X, pady=1)
                
                check = ttk.Checkbutton(check_frame, text=ing['nombre'], variable=var)
                check.pack(side=tk.LEFT)
                
                # Info adicional
                info_text = f"(${ing['precio_base']:.2f}/kg, "
                info_text += f"{ing['nutrientes']['proteina']*100:.1f}% prot)"
                ttk.Label(check_frame, text=info_text, font=('Arial', 8),
                         foreground='gray').pack(side=tk.LEFT, padx=10)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Botones de acción rápida
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(action_frame, text="Seleccionar Todos", 
                  command=self.seleccionar_todos).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Deseleccionar Todos", 
                  command=self.deseleccionar_todos).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Invertir Selección", 
                  command=self.invertir_seleccion).pack(side=tk.LEFT, padx=5)
        
        # Label contador
        self.contador_label = ttk.Label(action_frame, text="")
        self.contador_label.pack(side=tk.RIGHT, padx=5)
        self.actualizar_contador()
        
        # Bind para actualizar contador
        for var in self.check_vars.values():
            var.trace('w', lambda *args: self.actualizar_contador())
        
        # Botones OK/Cancelar
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Aceptar", command=self.aceptar).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancelar", command=self.cancelar).pack(side=tk.RIGHT, padx=5)
    
    def seleccionar_todos(self):
        """Selecciona todos los ingredientes"""
        for var in self.check_vars.values():
            var.set(True)
    
    def deseleccionar_todos(self):
        """Deselecciona todos los ingredientes"""
        for var in self.check_vars.values():
            var.set(False)
    
    def invertir_seleccion(self):
        """Invierte la selección actual"""
        for var in self.check_vars.values():
            var.set(not var.get())
    
    def actualizar_contador(self):
        """Actualiza el contador de ingredientes seleccionados"""
        seleccionados = sum(1 for var in self.check_vars.values() if var.get())
        total = len(self.check_vars)
        self.contador_label.config(text=f"Seleccionados: {seleccionados}/{total}")
    
    def aceptar(self):
        """Guarda la selección y cierra"""
        self.resultado = [nombre for nombre, var in self.check_vars.items() if var.get()]
        self.destroy()
    
    def cancelar(self):
        """Cierra sin guardar cambios"""
        self.resultado = None
        self.destroy()