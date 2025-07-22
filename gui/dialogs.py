"""
Diálogos y ventanas emergentes de la aplicación
"""

import tkinter as tk
from tkinter import ttk
from config import SISTEMA_INFO, ALGORITMO_CONFIG
from conocimiento import INGREDIENTES, RAZAS_POLLOS


class ManualDialog:
    """Diálogo del manual de usuario"""
    
    def __init__(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Manual de Usuario - boilerNutri")
        self.dialog.geometry("600x500")
        
        # Texto del manual
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
- Use "Validar Parámetros" antes de optimizar
- Guarde configuraciones frecuentemente
- Exporte resultados importantes como PDF
"""
        
        # Texto del manual
        text_widget = tk.Text(self.dialog, wrap=tk.WORD, padx=10, pady=10)
        text_widget.insert(1.0, manual_texto)
        text_widget.config(state=tk.DISABLED)
        
        # Scrollbar
        scrollbar_manual = ttk.Scrollbar(self.dialog, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar_manual.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_manual.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Centrar ventana
        self.dialog.transient(parent)
        self.dialog.grab_set()


class BaseConocimientoDialog:
    """Diálogo para mostrar información de la base de conocimiento"""
    
    def __init__(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Base de Conocimiento - boilerNutri")
        self.dialog.geometry("500x400")
        
        # Preparar información
        info_texto = self._generar_info_texto()
        
        # Mostrar información
        text_widget = tk.Text(self.dialog, wrap=tk.WORD, padx=10, pady=10)
        text_widget.insert(1.0, info_texto)
        text_widget.config(state=tk.DISABLED)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.dialog, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Centrar ventana
        self.dialog.transient(parent)
        self.dialog.grab_set()
    
    def _generar_info_texto(self):
        """Genera el texto con la información de la base de conocimiento"""
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
        
        info_texto += f"\nConfiguración del algoritmo:\n"
        info_texto += f"   • Población: {ALGORITMO_CONFIG.get('tamano_poblacion', 'N/A')}\n"
        info_texto += f"   • Generaciones: {ALGORITMO_CONFIG.get('num_generaciones', 'N/A')}\n"
        info_texto += f"   • Probabilidad cruza: {ALGORITMO_CONFIG.get('prob_cruza', 'N/A')}\n"
        info_texto += f"   • Probabilidad mutación: {ALGORITMO_CONFIG.get('prob_mutacion', 'N/A')}\n"
        
        return info_texto