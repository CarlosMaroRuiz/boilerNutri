"""
Widget de tabla para mostrar formulaciones de alimentos
"""

import tkinter as tk
from tkinter import ttk, messagebox
import re
from conocimiento import INGREDIENTES


class TablaFormulacion(ttk.Frame):
    """Widget de tabla para mostrar el detalle de una formulación CON PROVEEDOR"""
    
    def __init__(self, parent, formulacion):
        super().__init__(parent)
        self.formulacion = formulacion
        
        self.crear_tabla()
    
    def crear_tabla(self):
        """Crea la tabla con el detalle de la formulación INCLUYENDO PROVEEDOR"""
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
        
        # ✅ COLUMNAS CON PROVEEDOR Y CLARIDAD MEJORADA
        columns = ('Ingrediente', '(%)', 'kg/ton', 'Precio', 'Proveedor', 'Costo/Ton')
        self.tree = ttk.Treeview(tabla_frame, columns=columns, show='headings', height=12)
        
        # Configurar columnas
        self.tree.heading('Ingrediente', text='Ingrediente', command=lambda: self.ordenar_columna('Ingrediente'))
        self.tree.column('Ingrediente', width=160, anchor=tk.W)
        
        self.tree.heading('(%)', text='%', command=lambda: self.ordenar_columna('(%)'))
        self.tree.column('(%)', width=50, anchor=tk.CENTER)
        
        self.tree.heading('kg/ton', text='kg/ton', command=lambda: self.ordenar_columna('kg/ton'))
        self.tree.column('kg/ton', width=60, anchor=tk.CENTER)
        
        self.tree.heading('Precio', text='Precio $/kg', command=lambda: self.ordenar_columna('Precio'))
        self.tree.column('Precio', width=80, anchor=tk.CENTER)
        
        # ✅ COLUMNA DE PROVEEDOR
        self.tree.heading('Proveedor', text='Proveedor', command=lambda: self.ordenar_columna('Proveedor'))
        self.tree.column('Proveedor', width=140, anchor=tk.W)
        
        self.tree.heading('Costo/Ton', text='Costo Total', command=lambda: self.ordenar_columna('Costo/Ton'))
        self.tree.column('Costo/Ton', width=90, anchor=tk.CENTER)
        
        # Estilo de fuente más pequeño
        style = ttk.Style()
        style.configure("Treeview", font=('Arial', 8))
        style.configure("Treeview.Heading", font=('Arial', 8, 'bold'))
        
        # Frame para tabla con scrollbars usando pack
        tree_frame = ttk.Frame(tabla_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Scrollbars usando pack
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack para tabla y scrollbars
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Configurar eventos
        self.tree.bind('<Double-1>', self.on_double_click)
        self.tree.bind('<Button-3>', self.mostrar_menu_contextual)  # Click derecho
        
        # Frame de resumen usando pack
        resumen_frame = ttk.Frame(tabla_frame)
        resumen_frame.pack(fill=tk.X, pady=5)
        
        self.resumen_label = ttk.Label(resumen_frame, font=('Arial', 9, 'bold'))
        self.resumen_label.pack()
        
        # Cargar datos
        self.cargar_datos()
    
    def cargar_datos(self):
        """Carga los datos en la tabla CON PROVEEDOR"""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # ✅ OBTENER DATOS CON PROVEEDOR
        datos_ingredientes = self.procesar_datos_formulacion()
        
        # Variables para totales
        total_costo = 0
        total_proteina = 0
        total_energia = 0
        num_ingredientes = 0
        
        # Insertar datos
        self.datos_tabla = []
        for datos in datos_ingredientes:
            if datos['porcentaje'] > 0.1:  # Solo mostrar ingredientes > 0.1%
                costo_total = datos['costo_total']
                total_costo += costo_total
                
                # Calcular contribución nutricional
                try:
                    ingrediente_idx = next(i for i, ing in enumerate(INGREDIENTES) 
                                         if ing['nombre'] == datos['ingrediente'])
                    nutrientes = INGREDIENTES[ingrediente_idx].get('nutrientes', {})
                    porcentaje_decimal = datos['porcentaje'] / 100
                    
                    proteina_contrib = porcentaje_decimal * nutrientes.get('proteina', 0) * 100
                    energia_contrib = porcentaje_decimal * nutrientes.get('energia', 0)
                    
                    total_proteina += proteina_contrib
                    total_energia += energia_contrib
                except StopIteration:
                    pass  # Ingrediente no encontrado
                
                num_ingredientes += 1
                
                # Formatear valores con más claridad
                porcentaje_str = f"{datos['porcentaje']:.2f}%"
                kg_ton_str = f"{datos['kg_ton']:.1f}"
                precio_str = f"${datos['precio']:.2f}"
                costo_ton_str = f"${costo_total:.0f}"
                
                # ✅ INCLUIR PROVEEDOR EN LOS DATOS
                self.tree.insert('', 'end', values=(
                    datos['ingrediente'],
                    porcentaje_str,
                    kg_ton_str,
                    precio_str,
                    datos['proveedor'],  # 🔥 COLUMNA DE PROVEEDOR
                    costo_ton_str       # Costo en pesos totales para esa cantidad
                ))
                
                # Guardar para filtrado y ordenamiento
                self.datos_tabla.append(datos)
        
        # Calcular costo por kg y por tonelada
        costo_por_kg = total_costo / 1000 if total_costo > 0 else 0
        costo_por_tonelada = total_costo
        
        # Fila de totales con información clara
        self.tree.insert('', 'end', values=(
            'TOTAL',
            '100.00%',
            '1000.0',
            f'${costo_por_kg:.2f}/kg',
            'TODOS LOS PROVEEDORES',
            f'${costo_por_tonelada:.0f}/ton'
        ), tags=('total',))
        
        # Configurar estilo para fila total
        self.tree.tag_configure('total', background='#E3F2FD', font=('Arial', 9, 'bold'))
        
        # Actualizar labels con información más completa
        self.total_label.config(text=f"Total: {num_ingredientes} ingredientes activos")
        
        # Calcular estimación por pollo (asumiendo 3.5 kg promedio)
        costo_por_pollo = costo_por_kg * 3.5
        
        self.resumen_label.config(
            text=f"💰 COSTO: ${costo_por_kg:.2f}/kg • ${costo_por_tonelada:,.0f}/tonelada • ${costo_por_pollo:.0f}/pollo(3.5kg) | "
            f"🥩 PROTEÍNA: {total_proteina:.1f}% | "
            f"⚡ ENERGÍA: {total_energia:.0f} kcal/kg"
        )
    
    def procesar_datos_formulacion(self):
        """✅ PROCESA LOS DATOS INCLUYENDO PROVEEDOR RECOMENDADO"""
        datos = []
        porcentajes = self.formulacion.get('porcentajes', [])
        
        # Obtener proveedores recomendados si existen
        proveedores_rec = self.formulacion.get('proveedor_recomendado', {})
        
        for i, porcentaje in enumerate(porcentajes):
            if i < len(INGREDIENTES):
                ingrediente = INGREDIENTES[i]
                
                # Determinar proveedor y precio
                if str(i) in proveedores_rec:
                    # Usar proveedor recomendado por el algoritmo
                    proveedor_info = proveedores_rec[str(i)]
                    proveedor_clave = proveedor_info['proveedor']
                    precio = proveedor_info['precio']
                    proveedor_nombre = self.obtener_nombre_proveedor(proveedor_clave)
                elif i in proveedores_rec:
                    # Probar con índice numérico
                    proveedor_info = proveedores_rec[i]
                    proveedor_clave = proveedor_info['proveedor']
                    precio = proveedor_info['precio']
                    proveedor_nombre = self.obtener_nombre_proveedor(proveedor_clave)
                else:
                    # Buscar el mejor precio manualmente
                    precios = ingrediente.get('precios', {})
                    if precios:
                        proveedor_clave = min(precios, key=precios.get)
                        precio = precios[proveedor_clave]
                        proveedor_nombre = self.obtener_nombre_proveedor(proveedor_clave)
                    else:
                        precio = ingrediente.get('precio_base', 0)
                        proveedor_nombre = "No especificado"
                
                datos.append({
                    'ingrediente': ingrediente.get('nombre', f'Ingrediente {i+1}'),
                    'porcentaje': porcentaje * 100,  # Convertir a porcentaje
                    'kg_ton': porcentaje * 1000,     # kg por tonelada
                    'precio': precio,
                    'proveedor': proveedor_nombre,   # 🔥 INFORMACIÓN DE PROVEEDOR
                    'costo_total': porcentaje * 1000 * precio
                })
        
        return datos
    
    def obtener_nombre_proveedor(self, clave_proveedor):
        """✅ OBTIENE EL NOMBRE LEGIBLE DEL PROVEEDOR"""
        nombres_proveedores = {
            'veterinaria_buenavista': 'Vet. Buenavista',
            'veterinaria_don_paco': 'Vet. Don Paco', 
            'veterinaria_don_edilberto': 'Vet. Don Edilberto'
        }
        return nombres_proveedores.get(clave_proveedor, clave_proveedor)
    
    def mostrar_menu_contextual(self, event):
        """✅ MUESTRA MENÚ CONTEXTUAL PARA CAMBIAR PROVEEDOR"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        valores = self.tree.item(item, 'values')
        if valores[0] == 'TOTAL':
            return
        
        # Crear menú contextual
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Ver precios por veterinaria", 
                        command=lambda: self.mostrar_comparacion_precios(item))
        menu.add_separator()
        menu.add_command(label="Cambiar a Vet. Don Paco", 
                        command=lambda: self.cambiar_proveedor(item, 'veterinaria_don_paco'))
        menu.add_command(label="Cambiar a Vet. Don Edilberto", 
                        command=lambda: self.cambiar_proveedor(item, 'veterinaria_don_edilberto'))
        menu.add_command(label="Cambiar a Vet. Buenavista", 
                        command=lambda: self.cambiar_proveedor(item, 'veterinaria_buenavista'))
        
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def mostrar_comparacion_precios(self, item):
        """✅ MUESTRA COMPARACIÓN DE PRECIOS POR VETERINARIA"""
        valores = self.tree.item(item, 'values')
        ingrediente_nombre = valores[0]
        
        # Buscar el ingrediente
        ingrediente_data = None
        for ing in INGREDIENTES:
            if ing['nombre'] == ingrediente_nombre:
                ingrediente_data = ing
                break
        
        if not ingrediente_data:
            return
        
        # Crear ventana de comparación
        ventana = tk.Toplevel(self)
        ventana.title(f"Precios de {ingrediente_nombre}")
        ventana.geometry("450x250")
        ventana.resizable(False, False)
        
        # Frame principal
        main_frame = ttk.Frame(ventana, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(main_frame, text=f"Comparación de Precios", 
                 font=('Arial', 12, 'bold')).pack(pady=5)
        ttk.Label(main_frame, text=ingrediente_nombre, 
                 font=('Arial', 10)).pack(pady=5)
        
        # Tabla de precios
        precio_frame = ttk.LabelFrame(main_frame, text="Precios por Veterinaria", padding=10)
        precio_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        precios = ingrediente_data.get('precios', {})
        precio_minimo = min(precios.values()) if precios else 0
        
        for i, (clave, precio) in enumerate(precios.items()):
            nombre = self.obtener_nombre_proveedor(clave)
            
            # Frame para cada precio
            row_frame = ttk.Frame(precio_frame)
            row_frame.pack(fill=tk.X, pady=2)
            
            # Nombre de la veterinaria
            ttk.Label(row_frame, text=f"{nombre}:", 
                     font=('Arial', 10)).pack(side=tk.LEFT)
            
            # Precio
            precio_text = f"${precio:.2f}/kg"
            color = 'green' if precio == precio_minimo else 'black'
            peso = 'bold' if precio == precio_minimo else 'normal'
            
            ttk.Label(row_frame, text=precio_text, 
                     font=('Arial', 10, peso),
                     foreground=color).pack(side=tk.RIGHT)
            
            # Indicador de mejor precio
            if precio == precio_minimo:
                ttk.Label(row_frame, text="← MEJOR PRECIO", 
                         font=('Arial', 8),
                         foreground='green').pack(side=tk.RIGHT, padx=10)
        
        # Botón cerrar
        ttk.Button(main_frame, text="Cerrar", 
                  command=ventana.destroy).pack(pady=10)
        
        # Centrar ventana
        ventana.transient(self.winfo_toplevel())
        ventana.grab_set()
    
    def cambiar_proveedor(self, item, nuevo_proveedor):
        """✅ CAMBIA EL PROVEEDOR DE UN INGREDIENTE"""
        nuevo_nombre = self.obtener_nombre_proveedor(nuevo_proveedor)
        messagebox.showinfo("Cambio de Proveedor", 
                          f"Proveedor cambiado a: {nuevo_nombre}\n\n"
                          f"Nota: Esta funcionalidad recalculará la formulación\n"
                          f"en una futura versión.")
    
    def filtrar_tabla(self, event=None):
        """Filtra la tabla según el texto de búsqueda"""
        busqueda = self.search_var.get().lower()
        
        # Si no hay búsqueda, recargar todo
        if not busqueda:
            self.cargar_datos()
            return
        
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Filtrar datos
        datos_ingredientes = self.procesar_datos_formulacion()
        total_costo_filtrado = 0
        num_mostrados = 0
        
        for datos in datos_ingredientes:
            if (busqueda in datos['ingrediente'].lower() or 
                busqueda in datos['proveedor'].lower()):
                
                if datos['porcentaje'] > 0.1:
                    costo_total = datos['costo_total']
                    total_costo_filtrado += costo_total
                    num_mostrados += 1
                    
                    porcentaje_str = f"{datos['porcentaje']:.2f}%"
                    kg_ton_str = f"{datos['kg_ton']:.1f}"
                    precio_str = f"${datos['precio']:.2f}"
                    costo_ton_str = f"${costo_total:.0f}"
                    
                    self.tree.insert('', 'end', values=(
                        datos['ingrediente'],
                        porcentaje_str,
                        kg_ton_str,
                        precio_str,
                        datos['proveedor'],
                        costo_ton_str
                    ))
        
        # Añadir total filtrado
        if num_mostrados > 0:
            costo_kg_filtrado = total_costo_filtrado / 1000
            costo_ton_filtrado = total_costo_filtrado
            
            self.tree.insert('', 'end', values=(
                f'SUBTOTAL ({num_mostrados} items)',
                '',
                '',
                f'${costo_kg_filtrado:.2f}/kg',
                '',
                f'${costo_ton_filtrado:.0f}/ton'
            ), tags=('total',))
        
        # Actualizar contador
        self.total_label.config(text=f"Mostrando: {num_mostrados} ingredientes")
    
    def ordenar_columna(self, col):
        """Ordena la tabla por la columna seleccionada"""
        # Obtener datos actuales (sin la fila TOTAL)
        datos = []
        for child in self.tree.get_children()[:-1]:
            datos.append(self.tree.item(child)['values'])
        
        # Determinar índice de columna
        col_indices = {
            'Ingrediente': 0, '(%)': 1, 'kg/ton': 2, 
            'Precio': 3, 'Proveedor': 4, 'Costo/Ton': 5
        }
        col_idx = col_indices.get(col, 0)
        
        # Función de ordenamiento
        def sort_key(item):
            value = item[col_idx]
            if col_idx in [0, 4]:  # Nombre e ingrediente, proveedor
                return value
            else:  # Valores numéricos
                match = re.search(r'[\d.]+', str(value))
                return float(match.group()) if match else 0
        
        # Verificar orden
        sort_attr = f'_sort_reverse_{col}'
        if not hasattr(self, sort_attr):
            setattr(self, sort_attr, False)
        
        # Ordenar
        datos.sort(key=sort_key, reverse=getattr(self, sort_attr))
        setattr(self, sort_attr, not getattr(self, sort_attr))
        
        # Recargar tabla ordenada
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for valores in datos:
            self.tree.insert('', tk.END, values=valores)
        
        # Re-añadir fila total con información clara
        total_costo_sum = 0
        for valores in datos:
            try:
                # Extraer número de la columna de costo total
                costo_str = str(valores[5]).replace('$', '').replace(',', '')
                total_costo_sum += float(costo_str)
            except (ValueError, IndexError):
                continue
        
        costo_por_kg = total_costo_sum / 1000
        costo_por_tonelada = total_costo_sum
        
        self.tree.insert('', tk.END, values=(
            'TOTAL',
            '100.00%',
            '1000.0',
            f'${costo_por_kg:.2f}/kg',
            'TODOS LOS PROVEEDORES',
            f'${costo_por_tonelada:.0f}/ton'
        ), tags=('total',))
    
    def on_double_click(self, event):
        """Maneja doble click en la tabla"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            self.mostrar_comparacion_precios(item)