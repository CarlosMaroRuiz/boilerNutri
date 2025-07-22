#!/usr/bin/env python3
"""
main.py - Archivo principal para ejecutar boilerNutri

Sistema de optimización de formulaciones de alimentos para pollos
usando algoritmos genéticos con interfaz gráfica moderna.
"""

import tkinter as tk
from tkinter import messagebox

# Importaciones del sistema
try:
    from config import SISTEMA_INFO, ALGORITMO_CONFIG
    from conocimiento import INGREDIENTES, RAZAS_POLLOS
    from gui import BoilerNutriGUI
except ImportError as e:
    print(f"❌ Error al importar módulos: {e}")
    print(f"Asegúrese de que todos los archivos del proyecto están presentes:")
    print(f"  • config.py")
    print(f"  • conocimiento/__init__.py")
    print(f"  • gui/__init__.py")
    raise


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
        
        # Iniciar aplicación
        app = BoilerNutriGUI()
        app.ejecutar()
        
    except ImportError as e:
        error_msg = f"Error al importar módulos del sistema:\n{e}\n\n"
        error_msg += "Verifique que:\n"
        error_msg += "• El directorio 'conocimiento/' existe\n"
        error_msg += "• Los archivos ingredientes.py, razas.py están presentes\n"
        error_msg += "• El archivo config.py está disponible\n"
        error_msg += "• El directorio 'gui/' existe con todos sus archivos"
        messagebox.showerror("Error de Importación", error_msg)
        
    except Exception as e:
        error_msg = f"Error al iniciar la aplicación:\n{e}\n\n"
        error_msg += "Consulte la documentación o contacte al soporte técnico."
        messagebox.showerror("Error Fatal", error_msg)


if __name__ == "__main__":
    main()