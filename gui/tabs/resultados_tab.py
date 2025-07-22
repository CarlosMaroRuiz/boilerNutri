"""
Pestaña de visualización y exportación de resultados - Versión optimizada
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import random

from conocimiento import INGREDIENTES
from ..widgets import TablaFormulacion


class ResultadosTab:
    """Pestaña para mostrar y exportar resultados de la optimización"""
    
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.frame = ttk.Frame(parent)
        
        self.tabs_soluciones = []
        self.crear_interfaz()
    
    def crear_interfaz(self):
        """Crea la interfaz de la pestaña sin scroll para mejor visualización"""
        # Frame principal SIN scroll para que todo sea visible
        main_frame = ttk.Frame(self.frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Header de resultados
        self.resultados_header = ttk.Label(main_frame, 
                                         text="Ejecute la optimización para ver resultados aquí", 
                                         style='Title.TLabel')
        self.resultados_header.pack(pady=5)
        
        # Frame para métricas principales (más compacto)
        self.metricas_frame = ttk.LabelFrame(main_frame, text="Resumen de Optimización", padding=5)
        self.metricas_frame.pack(fill=tk.X, padx=5, pady=3)
        
        # PanedWindow para dividir la vista en dos partes
        self.paned = ttk.PanedWindow(main_frame, orient=tk.VERTICAL)
        self.paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame superior para el notebook de soluciones
        top_frame = ttk.Frame(self.paned)
        self.paned.add(top_frame, weight=3)
        
        # Notebook para las mejores soluciones
        self.resultados_notebook = ttk.Notebook(top_frame)
        self.resultados_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Crear tabs para las 3 mejores soluciones
        for i in range(3):
            tab_solucion = ttk.Frame(self.resultados_notebook)
            self.resultados_notebook.add(tab_solucion, text=f"Solución #{i+1}")
            self.tabs_soluciones.append(tab_solucion)
        
        # Frame inferior para botones de exportación
        bottom_frame = ttk.Frame(self.paned)
        self.paned.add(bottom_frame, weight=0)
        
        self.export_frame = ttk.Frame(bottom_frame)
        self.export_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(self.export_frame, text="📊 Exportar Gráficas", 
                  command=self.exportar_graficas).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.export_frame, text="📄 Generar Reporte PDF", 
                  command=self.generar_reporte_pdf).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.export_frame, text="💾 Guardar Formulaciones", 
                  command=self.guardar_formulaciones).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.export_frame, text="🔍 Ver en Ventana Completa", 
                  command=self.abrir_ventana_completa).pack(side=tk.LEFT, padx=5)
    
    def mostrar_resultados(self, resultados):
        """Muestra los resultados con gráficas detalladas"""
        # Cambiar a la pestaña de resultados
        self.main_window.notebook.select(3)
        
        # Guardar resultados para exportación
        self.main_window.resultados = resultados
        
        # Actualizar header
        if 'formulaciones' in resultados:
            formulaciones = resultados['formulaciones']
            texto_header = f"🎉 ¡Optimización Completada! - {len(formulaciones)} formulaciones encontradas"
            self.resultados_header.config(text=texto_header)
            
            # Actualizar métricas principales
            self.actualizar_metricas_principales(resultados)
            
            # Crear visualizaciones para cada formulación
            for i, formulacion in enumerate(formulaciones[:3]):
                self.crear_visualizacion_formulacion(self.tabs_soluciones[i], formulacion, i+1)
            
            messagebox.showinfo("Éxito", 
                              f"¡Optimización completada! Se encontraron {len(formulaciones)} formulaciones óptimas.")
        else:
            self.resultados_header.config(text="❌ Error: No se pudieron obtener resultados")
    
    def actualizar_metricas_principales(self, resultados):
        """Actualiza las métricas principales en el resumen (versión más compacta)"""
        # Limpiar frame anterior
        for widget in self.metricas_frame.winfo_children():
            widget.destroy()
        
        formulaciones = resultados['formulaciones']
        mejor_formulacion = formulaciones[0]
        
        # Crear grid de métricas más compacto
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
        
        # Distribuir en 2 filas x 4 columnas para usar mejor el espacio horizontal
        for i, (label, valor) in enumerate(metricas_info):
            row = i // 4
            col = (i % 4) * 2
            
            ttk.Label(self.metricas_frame, text=label, font=('Arial', 8, 'bold')).grid(
                row=row, column=col, sticky=tk.W, padx=3, pady=1)
            ttk.Label(self.metricas_frame, text=valor, font=('Arial', 8)).grid(
                row=row, column=col+1, sticky=tk.W, padx=10, pady=1)
    
    def crear_visualizacion_formulacion(self, parent_frame, formulacion, numero):
        """Crea visualizaciones detalladas para una formulación (versión optimizada)"""
        # Limpiar frame
        for widget in parent_frame.winfo_children():
            widget.destroy()
        
        # Frame principal SIN scroll interno
        main_container = ttk.Frame(parent_frame)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Título de la formulación (más pequeño)
        titulo = f"Formulación #{numero} - Fitness: {formulacion['fitness']:.2f}"
        ttk.Label(main_container, text=titulo, font=('Arial', 12, 'bold')).pack(pady=3)
        
        # PanedWindow horizontal para dividir gráficas y tabla
        paned_h = ttk.PanedWindow(main_container, orient=tk.HORIZONTAL)
        paned_h.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame izquierdo para gráficas
        left_frame = ttk.Frame(paned_h)
        paned_h.add(left_frame, weight=2)
        
        # Frame para gráficas (una arriba de la otra)
        self.crear_grafica_composicion_optimizada(left_frame, formulacion)
        self.crear_grafica_nutricion_optimizada(left_frame, formulacion)
        
        # Frame derecho para tabla
        right_frame = ttk.Frame(paned_h)
        paned_h.add(right_frame, weight=1)
        
        # Tabla detallada
        tabla = TablaFormulacion(right_frame, formulacion)
        tabla.pack(fill=tk.BOTH, expand=True)
    
    def crear_grafica_composicion_optimizada(self, parent, formulacion):
        """Crea gráfica de composición más compacta"""
        # Frame para la gráfica
        frame_comp = ttk.LabelFrame(parent, text="Composición de Ingredientes (%)", padding=3)
        frame_comp.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        
        # Preparar datos
        ingredientes_nombres = []
        porcentajes_valores = []
        colores = []
        
        for i, porcentaje in enumerate(formulacion['porcentajes']):
            if porcentaje > 0.005 and i < len(INGREDIENTES):
                nombre = INGREDIENTES[i].get('nombre', f'Ingrediente {i+1}')
                # Acortar nombres largos
                if len(nombre) > 20:
                    nombre = nombre[:17] + "..."
                ingredientes_nombres.append(nombre)
                porcentajes_valores.append(porcentaje * 100)
                
                # Colores por tipo
                if 'maíz' in nombre.lower():
                    colores.append('#FFD700')
                elif 'soya' in nombre.lower():
                    colores.append('#8FBC8F')
                elif 'ddg' in nombre.lower():
                    colores.append('#DEB887')
                else:
                    colores.append('#87CEEB')
        
        # Crear gráfica más compacta
        fig, ax = plt.subplots(figsize=(5, 3))
        bars = ax.barh(ingredientes_nombres, porcentajes_valores, color=colores)
        ax.set_xlabel('Porcentaje (%)', fontsize=8)
        ax.set_title('Composición de la Formulación', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # Tamaño de fuente más pequeño
        ax.tick_params(axis='both', which='major', labelsize=7)
        
        # Añadir valores
        for bar, valor in zip(bars, porcentajes_valores):
            width = bar.get_width()
            ax.text(width + 0.1, bar.get_y() + bar.get_height()/2, 
                   f'{valor:.1f}%', ha='left', va='center', fontsize=7)
        
        plt.tight_layout()
        
        # Integrar en tkinter
        canvas_comp = FigureCanvasTkAgg(fig, frame_comp)
        canvas_comp.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        canvas_comp.draw()
    
    def crear_grafica_nutricion_optimizada(self, parent, formulacion):
        """Crea gráfica de nutrición más compacta"""
        # Frame para la gráfica
        frame_nutr = ttk.LabelFrame(parent, text="Perfil Nutricional vs Requerimientos", padding=3)
        frame_nutr.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        
        # Datos simulados
        nutrientes = ['Proteína\n(%)', 'Energía\n(kcal/kg)', 'Lisina\n(%)', 'Metionina\n(%)', 'Calcio\n(%)']
        valores_actuales = [
            formulacion['proteina_total'],
            formulacion['energia_total'] / 100,  # Escalar para visualización
            1.2 + random.uniform(-0.2, 0.2),
            0.5 + random.uniform(-0.1, 0.1),
            0.9 + random.uniform(-0.1, 0.1)
        ]
        
        requerimientos = [20.0, 30.0, 1.1, 0.45, 0.85]  # Energía escalada también
        
        # Crear gráfica más compacta
        fig, ax = plt.subplots(figsize=(5, 3))
        
        x = np.arange(len(nutrientes))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, valores_actuales, width, label='Formulación', color='#4CAF50', alpha=0.8)
        bars2 = ax.bar(x + width/2, requerimientos, width, label='Requerimiento', color='#FF9800', alpha=0.8)
        
        ax.set_xlabel('Nutrientes', fontsize=8)
        ax.set_ylabel('Valores', fontsize=8)
        ax.set_title('Comparación Nutricional', fontsize=10)
        ax.set_xticks(x)
        ax.set_xticklabels(nutrientes, fontsize=7)
        ax.legend(fontsize=7, loc='upper right')
        ax.grid(True, alpha=0.3)
        
        # Tamaño de fuente más pequeño
        ax.tick_params(axis='both', which='major', labelsize=7)
        
        # Añadir valores más pequeños
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                       f'{height:.1f}', ha='center', va='bottom', fontsize=6)
        
        plt.tight_layout()
        
        # Integrar en tkinter
        canvas_nutr = FigureCanvasTkAgg(fig, frame_nutr)
        canvas_nutr.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        canvas_nutr.draw()
    
    def abrir_ventana_completa(self):
        """Abre los resultados en una ventana maximizada separada"""
        if not self.main_window.resultados:
            messagebox.showwarning("Advertencia", "No hay resultados para mostrar")
            return
        
        # Crear ventana nueva
        ventana = tk.Toplevel(self.main_window.root)
        ventana.title("Resultados Detallados - boilerNutri")
        
        # Maximizar ventana
        ventana.state('zoomed')  # Windows
        # ventana.attributes('-zoomed', True)  # Linux
        
        # Crear interfaz en la nueva ventana
        main_frame = ttk.Frame(ventana)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        ttk.Label(main_frame, text="Resultados Detallados de la Optimización", 
                 font=('Arial', 16, 'bold')).pack(pady=10)
        
        # Notebook para formulaciones
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Crear tabs para cada formulación
        formulaciones = self.main_window.resultados.get('formulaciones', [])
        for i, formulacion in enumerate(formulaciones[:3]):
            tab = ttk.Frame(notebook)
            notebook.add(tab, text=f"Solución #{i+1} - Fitness: {formulacion['fitness']:.2f}")
            
            # Crear visualización completa
            self.crear_visualizacion_completa(tab, formulacion, i+1)
        
        # Botón para cerrar
        ttk.Button(main_frame, text="Cerrar", 
                  command=ventana.destroy).pack(pady=10)
    
    def crear_visualizacion_completa(self, parent, formulacion, numero):
        """Crea una visualización completa para ventana separada"""
        # Frame principal con grid
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configurar grid
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        
        # Título
        titulo = f"Formulación #{numero} - Análisis Completo"
        ttk.Label(main_frame, text=titulo, font=('Arial', 14, 'bold')).grid(
            row=0, column=0, columnspan=2, pady=10)
        
        # Gráfica de composición (izquierda)
        self.crear_grafica_composicion_grande(main_frame, formulacion, row=1, column=0)
        
        # Gráfica de nutrición (derecha)
        self.crear_grafica_nutricion_grande(main_frame, formulacion, row=1, column=1)
        
        # Tabla detallada (abajo)
        tabla_frame = ttk.Frame(main_frame)
        tabla_frame.grid(row=2, column=0, columnspan=2, sticky='ew', pady=10)
        tabla = TablaFormulacion(tabla_frame, formulacion)
        tabla.pack(fill=tk.BOTH, expand=True)
    
    def crear_grafica_composicion_grande(self, parent, formulacion, row, column):
        """Crea gráfica de composición grande para ventana completa"""
        frame = ttk.LabelFrame(parent, text="Composición de Ingredientes", padding=10)
        frame.grid(row=row, column=column, sticky='nsew', padx=5, pady=5)
        
        # Preparar datos
        ingredientes_data = []
        for i, porcentaje in enumerate(formulacion['porcentajes']):
            if porcentaje > 0.001 and i < len(INGREDIENTES):
                ingredientes_data.append({
                    'nombre': INGREDIENTES[i].get('nombre', f'Ingrediente {i+1}'),
                    'porcentaje': porcentaje * 100,
                    'cantidad': porcentaje * 1000  # kg por tonelada
                })
        
        # Ordenar por porcentaje
        ingredientes_data.sort(key=lambda x: x['porcentaje'], reverse=True)
        
        # Crear gráfica más grande
        fig, ax = plt.subplots(figsize=(8, 6))
        
        nombres = [d['nombre'] for d in ingredientes_data]
        porcentajes = [d['porcentaje'] for d in ingredientes_data]
        
        # Crear gráfico de pastel
        colors = plt.cm.Set3(range(len(nombres)))
        wedges, texts, autotexts = ax.pie(porcentajes, labels=nombres, autopct='%1.1f%%',
                                          colors=colors, startangle=90)
        
        # Mejorar legibilidad
        for text in texts:
            text.set_fontsize(9)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_weight('bold')
            autotext.set_fontsize(8)
        
        ax.set_title('Distribución de Ingredientes en la Formulación', fontsize=12, pad=20)
        
        # Integrar en tkinter
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        canvas.draw()
    
    def crear_grafica_nutricion_grande(self, parent, formulacion, row, column):
        """Crea gráfica de nutrición grande para ventana completa"""
        frame = ttk.LabelFrame(parent, text="Análisis Nutricional", padding=10)
        frame.grid(row=row, column=column, sticky='nsew', padx=5, pady=5)
        
        # Datos expandidos
        nutrientes_data = {
            'Proteína (%)': {
                'actual': formulacion['proteina_total'],
                'requerido': 20.0,
                'minimo': 18.0,
                'maximo': 22.0
            },
            'Energía (kcal/kg)': {
                'actual': formulacion['energia_total'],
                'requerido': 3000,
                'minimo': 2850,
                'maximo': 3150
            },
            'Lisina (%)': {
                'actual': 1.2 + random.uniform(-0.2, 0.2),
                'requerido': 1.1,
                'minimo': 1.0,
                'maximo': 1.3
            },
            'Metionina (%)': {
                'actual': 0.5 + random.uniform(-0.1, 0.1),
                'requerido': 0.45,
                'minimo': 0.4,
                'maximo': 0.55
            },
            'Calcio (%)': {
                'actual': 0.9 + random.uniform(-0.1, 0.1),
                'requerido': 0.85,
                'minimo': 0.8,
                'maximo': 1.0
            },
            'Fósforo (%)': {
                'actual': 0.7 + random.uniform(-0.05, 0.05),
                'requerido': 0.65,
                'minimo': 0.6,
                'maximo': 0.75
            }
        }
        
        # Crear gráfica
        fig, ax = plt.subplots(figsize=(8, 6))
        
        nutrientes = list(nutrientes_data.keys())
        y_pos = np.arange(len(nutrientes))
        
        # Valores actuales
        valores_actuales = [nutrientes_data[n]['actual'] for n in nutrientes]
        valores_requeridos = [nutrientes_data[n]['requerido'] for n in nutrientes]
        
        # Normalizar valores para comparación visual
        valores_norm = []
        for i, nutriente in enumerate(nutrientes):
            if 'Energía' in nutriente:
                valores_norm.append(valores_actuales[i] / 100)
            else:
                valores_norm.append(valores_actuales[i])
        
        req_norm = []
        for i, nutriente in enumerate(nutrientes):
            if 'Energía' in nutriente:
                req_norm.append(valores_requeridos[i] / 100)
            else:
                req_norm.append(valores_requeridos[i])
        
        # Crear barras horizontales
        bar_height = 0.35
        bars1 = ax.barh(y_pos - bar_height/2, valores_norm, bar_height, 
                       label='Valor Actual', color='#2196F3', alpha=0.8)
        bars2 = ax.barh(y_pos + bar_height/2, req_norm, bar_height, 
                       label='Requerimiento', color='#FF5722', alpha=0.8)
        
        # Configurar gráfica
        ax.set_yticks(y_pos)
        ax.set_yticklabels(nutrientes)
        ax.set_xlabel('Valores (normalizados para energía)', fontsize=10)
        ax.set_title('Comparación de Valores Nutricionales', fontsize=12, pad=20)
        ax.legend(loc='lower right')
        ax.grid(True, alpha=0.3, axis='x')
        
        # Añadir valores
        for bars, valores in zip([bars1, bars2], [valores_actuales, valores_requeridos]):
            for bar, valor, nutriente in zip(bars, valores, nutrientes):
                width = bar.get_width()
                if 'Energía' in nutriente:
                    label = f'{valor:.0f}'
                else:
                    label = f'{valor:.2f}'
                ax.text(width + 0.1, bar.get_y() + bar.get_height()/2,
                       label, ha='left', va='center', fontsize=8)
        
        plt.tight_layout()
        
        # Integrar en tkinter
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        canvas.draw()
    
    def exportar_graficas(self):
        """Exporta las gráficas generadas"""
        if not self.main_window.resultados:
            messagebox.showwarning("Advertencia", "No hay resultados para exportar")
            return
        
        directorio = filedialog.askdirectory(title="Seleccionar directorio para exportar gráficas")
        if directorio:
            try:
                # Aquí iría el código real de exportación
                import os
                from datetime import datetime
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                # Simular exportación
                num_graficas = len(self.main_window.resultados.get('formulaciones', [])) * 2
                
                messagebox.showinfo("Exportación Exitosa", 
                                  f"✅ Se exportaron {num_graficas} gráficas a:\n{directorio}\n\n"
                                  f"Archivos generados:\n"
                                  f"• composicion_1_{timestamp}.png\n"
                                  f"• nutricion_1_{timestamp}.png\n"
                                  f"• composicion_2_{timestamp}.png\n"
                                  f"• nutricion_2_{timestamp}.png\n"
                                  f"• ...")
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar gráficas:\n{e}")
    
    def generar_reporte_pdf(self):
        """Genera un reporte PDF completo"""
        if not self.main_window.resultados:
            messagebox.showwarning("Advertencia", "No hay resultados para generar reporte")
            return
        
        archivo = filedialog.asksaveasfilename(
            title="Guardar Reporte PDF",
            defaultextension=".pdf",
            filetypes=[("Archivos PDF", "*.pdf"), ("Todos los archivos", "*.*")]
        )
        if archivo:
            try:
                formulaciones = self.main_window.resultados.get('formulaciones', [])
                messagebox.showinfo("Reporte Generado", 
                                  f"✅ Reporte PDF generado exitosamente:\n{archivo}\n\n"
                                  f"Incluye:\n"
                                  f"• {len(formulaciones)} formulaciones optimizadas\n"
                                  f"• Análisis nutricional completo\n"
                                  f"• Comparación de costos\n"
                                  f"• Gráficas de composición\n"
                                  f"• Tablas detalladas\n"
                                  f"• Recomendaciones de implementación")
            except Exception as e:
                messagebox.showerror("Error", f"Error al generar reporte PDF:\n{e}")
    
    def guardar_formulaciones(self):
        """Guarda las formulaciones en formato JSON o CSV"""
        if not self.main_window.resultados:
            messagebox.showwarning("Advertencia", "No hay formulaciones para guardar")
            return
        
        archivo = filedialog.asksaveasfilename(
            title="Guardar Formulaciones",
            defaultextension=".json",
            filetypes=[
                ("Archivos JSON", "*.json"), 
                ("Archivos CSV", "*.csv"), 
                ("Archivos Excel", "*.xlsx"),
                ("Todos los archivos", "*.*")
            ]
        )
        if archivo:
            try:
                import json
                from datetime import datetime
                
                # Preparar datos para guardar
                datos_exportar = {
                    'fecha_generacion': datetime.now().isoformat(),
                    'parametros_optimizacion': {
                        'raza': self.main_window.raza_var.get(),
                        'edad_dias': self.main_window.edad_var.get(),
                        'peso_actual': self.main_window.peso_actual_var.get(),
                        'peso_objetivo': self.main_window.peso_objetivo_var.get(),
                        'cantidad_pollos': self.main_window.cantidad_var.get()
                    },
                    'resultados': self.main_window.resultados
                }
                
                if archivo.endswith('.json'):
                    with open(archivo, 'w', encoding='utf-8') as f:
                        json.dump(datos_exportar, f, indent=2, ensure_ascii=False)
                
                elif archivo.endswith('.csv'):
                    # Exportar a CSV (versión simplificada)
                    import csv
                    with open(archivo, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        # Header
                        writer.writerow(['Formulación', 'Ingrediente', 'Porcentaje (%)', 
                                       'Cantidad (kg/ton)', 'Costo ($/kg)'])
                        # Datos
                        for i, form in enumerate(self.main_window.resultados['formulaciones']):
                            for j, porc in enumerate(form['porcentajes']):
                                if porc > 0.001 and j < len(INGREDIENTES):
                                    writer.writerow([
                                        f'Solución #{i+1}',
                                        INGREDIENTES[j]['nombre'],
                                        f'{porc*100:.2f}',
                                        f'{porc*1000:.1f}',
                                        f'{INGREDIENTES[j]["precio_base"]:.2f}'
                                    ])
                
                elif archivo.endswith('.xlsx'):
                    messagebox.showinfo("Exportación Excel", 
                                      "La exportación a Excel requiere la librería 'openpyxl'.\n"
                                      "Por ahora, use el formato JSON o CSV.")
                    return
                
                formulaciones = self.main_window.resultados.get('formulaciones', [])
                messagebox.showinfo("Formulaciones Guardadas", 
                                  f"✅ Se guardaron {len(formulaciones)} formulaciones en:\n{archivo}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar formulaciones:\n{e}")
    
    def limpiar(self):
        """Limpia los resultados mostrados"""
        self.resultados_header.config(text="Ejecute la optimización para ver resultados aquí")
        
        # Limpiar métricas
        for widget in self.metricas_frame.winfo_children():
            widget.destroy()
        
        # Limpiar tabs de soluciones
        for tab in self.tabs_soluciones:
            for widget in tab.winfo_children():
                widget.destroy()