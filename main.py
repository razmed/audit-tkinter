#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Application Portail Document - SNTP
Application desktop de gestion de documents avec Drag & Drop

Auteur: Portail Document Team
Version: 2.0.0
"""

import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# IMPORTANT: Importer TkinterDnD AVANT tk
try:
    from tkinterdnd2 import TkinterDnD
    DRAG_DROP_AVAILABLE = True
    print("✅ Module tkinterdnd2 chargé - Drag & Drop activé")
except ImportError:
    import tkinter as tk
    DRAG_DROP_AVAILABLE = False
    print("⚠️ Module tkinterdnd2 non trouvé - Drag & Drop désactivé")
    print("   Pour activer le Drag & Drop, installez: pip install tkinterdnd2")

from tkinter import messagebox
from database import Database
from utils.file_handler import FileHandler
from ui.main_window import MainWindow


class PortalApplication:
    """Application principale du Portail Document"""
    
    def __init__(self):
        # Créer la fenêtre principale avec support Drag & Drop si disponible
        if DRAG_DROP_AVAILABLE:
            self.root = TkinterDnD.Tk()
            print("✅ Fenêtre TkinterDnD créée")
        else:
            import tkinter as tk
            self.root = tk.Tk()
            print("⚠️ Fenêtre Tk standard créée (pas de Drag & Drop)")
        
        self.db = None
        self.file_handler = None
        
        # Initialiser la base de données
        self.init_database()
        
        # Initialiser le gestionnaire de fichiers
        self.init_file_handler()
        
        # Afficher directement la fenêtre principale (PAS DE LOGIN)
        self.show_main_window()
    
    def init_database(self):
        """Initialiser la connexion à la base de données"""
        try:
            self.db = Database("portal.db")
            print("✅ Base de données initialisée")
        except Exception as e:
            messagebox.showerror(
                "Erreur Critique",
                f"Impossible d'initialiser la base de données:\n\n{e}"
            )
            sys.exit(1)
    
    def init_file_handler(self):
        """Initialiser le gestionnaire de fichiers"""
        try:
            self.file_handler = FileHandler("uploads")
            print("✅ Gestionnaire de fichiers initialisé")
        except Exception as e:
            messagebox.showerror(
                "Erreur Critique",
                f"Impossible d'initialiser le gestionnaire de fichiers:\n\n{e}"
            )
            sys.exit(1)
    
    def show_main_window(self):
        """Afficher la fenêtre principale"""
        MainWindow(self.root, self.db, self.file_handler)
        self.root.mainloop()
    
    def run(self):
        """Démarrer l'application"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\n⚠️ Interruption par l'utilisateur")
            self.cleanup()
        except Exception as e:
            print(f"❌ Erreur fatale: {e}")
            messagebox.showerror("Erreur Fatale", str(e))
            self.cleanup()
    
    def cleanup(self):
        """Nettoyer les ressources avant de quitter"""
        if self.db:
            self.db.close()
        print("👋 Application fermée")


def main():
    """Point d'entrée principal de l'application"""
    print("=" * 60)
    print("  PORTAIL DOCUMENT - SNTP")
    print("  Application Desktop de Gestion de Documents")
    print("  Version 2.0 - Avec Drag & Drop")
    print("=" * 60)
    print()
    
    try:
        app = PortalApplication()
        app.run()
    except Exception as e:
        print(f"❌ Erreur lors du démarrage de l'application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
