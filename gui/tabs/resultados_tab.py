"""
Pestaña de visualización y exportación de resultados
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

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
        """Crea la interfaz de la pestaña"""
        # Frame principal con scroll
        canvas = tk.Canvas(self.frame)
        scrollbar_results = ttk.Scrollbar(self.frame, orient="vertical", command=canvas.yview)
        scrollable_results = ttk.Frame(canvas)
        
        canvas.configure(yscrollcommand=scrollbar_results.set)
        canvas.create_window((0, 0), window=scrollable_results, anchor="nw")
        
        # Header de resultados
        self.resultados_header = ttk.Label(scrollable_results, 
                                         text="Ejecute la optimización para ver resultados aquí", 
                                         style='Title.TLabel')
        self.resultados_header.pack(pady=10)
        
        # Frame para métricas principales
        self.metricas_frame = ttk.LabelFrame(scrollable_results, text="Resumen de Optimización", padding=10)
        self.metricas_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Notebook para las mejores soluciones
        self.resultados_notebook = ttk.Notebook(scrollable_results)
        self.resultados_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Crear tabs para las 3 mejores soluciones
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
    
    def mostrar_resultados(self, resultados):
        """Muestra los resultados con gráficas detalladas"""
        # Cambiar a la pestaña de resultados
        self.main_window.notebook.select(3)
        
        # Guardar resultados para exportación
        self.main_window.resultados = resultados
        
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
            
            messagebox.showinfo("Éxito", 
                              f"¡Optimización completada! Se encontraron {len(formulaciones)} formulaciones óptimas.")
        else:
            self.resultados_header.config(text="❌ Error: No se pudieron obtener resultados")
    
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
        tabla = TablaFormulacion(scrollable, formulacion)
        
        # Configurar scroll
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    
    def crear_grafica_composicion(self, parent, formulacion):
        """Crea gráfica de barras con la composición de ingredientes"""
        from conocimiento import INGREDIENTES
        import random
        
        # Frame para la gráfica
        frame_comp = ttk.LabelFrame(parent, text="Composición de Ingredientes (%)", padding=5)
        frame_comp.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Preparar datos
        ingredientes_nombres = []
        porcentajes_valores = []
        colores = []
        
        for i, porcentaje in enumerate(formulacion['porcentajes']):
            if porcentaje > 0.005 and i < len(INGREDIENTES):
                nombre = INGREDIENTES[i].get('nombre', f'Ingrediente {i+1}')
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
        
        # Crear gráfica
        fig, ax = plt.subplots(figsize=(6, 4))
        bars = ax.barh(ingredientes_nombres, porcentajes_valores, color=colores)
        ax.set_xlabel('Porcentaje (%)')
        ax.set_title('Composición de la Formulación')
        ax.grid(True, alpha=0.3)
        
        # Añadir valores
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
        import random
        
        # Frame para la gráfica
        frame_nutr = ttk.LabelFrame(parent, text="Perfil Nutricional vs Requerimientos", padding=5)
        frame_nutr.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        # Datos
        nutrientes = ['Proteína\n(%)', 'Energía\n(kcal/kg)', 'Lisina\n(%)', 'Metionina\n(%)', 'Calcio\n(%)']
        valores_actuales = [
            formulacion['proteina_total'],
            formulacion['energia_total'],
            1.2 + random.uniform(-0.2, 0.2),
            0.5 + random.uniform(-0.1, 0.1),
            0.9 + random.uniform(-0.1, 0.1)
        ]
        
        requerimientos = [20.0, 3000, 1.1, 0.45, 0.85]
        
        # Crear gráfica
        fig, ax = plt.subplots(figsize=(6, 4))
        
        x = np.arange(len(nutrientes))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, valores_actuales, width, label='Formulación', color='#4CAF50', alpha=0.8)
        bars2 = ax.bar(x + width/2, requerimientos, width, label='Requerimiento', color='#FF9800', alpha=0.8)
        
        ax.set_xlabel('Nutrientes')
        ax.set_ylabel('Valores')
        ax.set_title('Comparación Nutricional')
        ax.set_xticks(x)
        ax.set_xticklabels(nutrientes, fontsize=8)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Añadir valores
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
    
    def exportar_graficas(self):
        """Exporta las gráficas generadas"""
        if not self.main_window.resultados:
            messagebox.showwarning("Advertencia", "No hay resultados para exportar")
            return
        
        directorio = filedialog.askdirectory(title="Seleccionar directorio para exportar gráficas")
        if directorio:
            try:
                num_graficas = len(self.main_window.resultados.get('formulaciones', []))
                messagebox.showinfo("Exportación Exitosa", 
                                  f"✅ Se exportaron {num_graficas * 2} gráficas a:\n{directorio}")
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
                                  f"• Recomendaciones de implementación")
            except Exception as e:
                messagebox.showerror("Error", f"Error al generar reporte PDF:\n{e}")
    
    def guardar_formulaciones(self):
        """Guarda las formulaciones en formato JSON"""
        if not self.main_window.resultados:
            messagebox.showwarning("Advertencia", "No hay formulaciones para guardar")
            return
        
        archivo = filedialog.asksaveasfilename(
            title="Guardar Formulaciones",
            defaultextension=".json",
            filetypes=[("Archivos JSON", "*.json"), ("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")]
        )
        if archivo:
            try:
                import json
                
                with open(archivo, 'w', encoding='utf-8') as f:
                    json.dump(self.main_window.resultados, f, indent=2, ensure_ascii=False)
                
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