import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Optional
from .folder_view import FolderView

class MainWindow:
    """Fenêtre principale de l'application"""
    
    def __init__(self, root: tk.Tk, db, file_handler):
        self.root = root
        self.db = db
        self.file_handler = file_handler
        self.current_folder_id = None
        self.folder_history = []  # Historique de navigation
        self.is_admin_authenticated = False  # État d'authentification admin
        
        self.root.title("Portail Document - SNTP")
        self.root.geometry("1200x700")
        
        # Centrer la fenêtre
        self.center_window()
        
        # Créer l'interface
        self.create_widgets()
        
        # Charger le contenu initial
        self.load_folder(None)
    
    def center_window(self):
        """Centrer la fenêtre sur l'écran"""
        self.root.update_idletasks()
        width = 1200
        height = 700
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Créer les widgets de l'interface"""
        # Barre de navigation supérieure
        navbar = tk.Frame(self.root, bg='#000', height=60)
        navbar.pack(fill=tk.X, side=tk.TOP)
        navbar.pack_propagate(False)
        
        # Logo et titre
        logo_frame = tk.Frame(navbar, bg='#000')
        logo_frame.pack(side=tk.LEFT, padx=20)
        
        logo_label = tk.Label(
            logo_frame,
            text="📁",
            font=('Arial', 24),
            bg='#000',
            fg='white'
        )
        logo_label.pack(side=tk.LEFT, padx=(0, 10))
        
        title_label = tk.Label(
            logo_frame,
            text="Portail Document",
            font=('Segoe UI', 16, 'bold'),
            bg='#000',
            fg='white'
        )
        title_label.pack(side=tk.LEFT)
        
        subtitle_label = tk.Label(
            logo_frame,
            text="Société Nationale des Travaux Publics",
            font=('Segoe UI', 9),
            bg='#000',
            fg='#adb5bd'
        )
        subtitle_label.pack(side=tk.LEFT, padx=(15, 0))
        
        # Boutons de navigation
        nav_buttons_frame = tk.Frame(navbar, bg='#000')
        nav_buttons_frame.pack(side=tk.RIGHT, padx=20)
        
        # Bouton retour
        self.back_button = tk.Button(
            nav_buttons_frame,
            text="⬅️ Retour",
            font=('Segoe UI', 10),
            bg='#495057',
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=self.go_back,
            state=tk.DISABLED
        )
        self.back_button.pack(side=tk.LEFT, padx=5)
        
        # Bouton accueil
        home_button = tk.Button(
            nav_buttons_frame,
            text="🏠 Accueil",
            font=('Segoe UI', 10),
            bg='#495057',
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=lambda: self.load_folder(None, clear_history=True)
        )
        home_button.pack(side=tk.LEFT, padx=5)
        
        # Bouton admin (avec authentification et déconnexion)
        self.admin_button = tk.Button(
            nav_buttons_frame,
            text="⚙️ Admin",
            font=('Segoe UI', 10),
            bg='#ff4d4d',
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=self.toggle_admin
        )
        self.admin_button.pack(side=tk.LEFT, padx=5)
        
        # Container pour le contenu
        self.content_frame = tk.Frame(self.root, bg='#f8f9fa')
        self.content_frame.pack(fill=tk.BOTH, expand=True)
    
    def toggle_admin(self):
        """Basculer entre connexion et déconnexion admin"""
        if self.is_admin_authenticated:
            # Déjà connecté -> proposer de se déconnecter ou d'ouvrir le panel
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="📊 Ouvrir Panel Admin", command=self.open_admin)
            menu.add_separator()
            menu.add_command(label="🚪 Se Déconnecter", command=self.logout_admin)
            
            # Afficher le menu à la position du bouton
            x = self.admin_button.winfo_rootx()
            y = self.admin_button.winfo_rooty() + self.admin_button.winfo_height()
            menu.post(x, y)
        else:
            # Pas connecté -> ouvrir la fenêtre de connexion
            self.open_admin_with_auth()
    
    def logout_admin(self):
        """Déconnecter l'administrateur"""
        response = messagebox.askyesno(
            "Déconnexion",
            "Voulez-vous vous déconnecter du mode administrateur ?",
            icon='question'
        )
        
        if response:
            self.is_admin_authenticated = False
            self.admin_button.config(text="⚙️ Admin", bg='#ff4d4d')
            messagebox.showinfo("Déconnexion", "Vous êtes maintenant déconnecté")
    
    def load_folder(self, folder_id: Optional[int], clear_history: bool = False):
        """Charger le contenu d'un dossier"""
        # Gérer l'historique
        if clear_history:
            self.folder_history = []
        elif self.current_folder_id is not None:
            self.folder_history.append(self.current_folder_id)
        
        self.current_folder_id = folder_id
        
        # Activer/désactiver le bouton retour
        self.back_button.config(
            state=tk.NORMAL if self.folder_history else tk.DISABLED
        )
        
        # Nettoyer le contenu précédent
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Créer la vue du dossier
        folder_view = FolderView(
            self.content_frame,
            self.db,
            self.file_handler,
            folder_id
        )
        folder_view.pack(fill=tk.BOTH, expand=True)
        
        # Écouter l'événement d'ouverture de dossier
        folder_view.bind('<<FolderOpen>>', self.on_folder_open)
    
    def on_folder_open(self, event):
        """Gérer l'ouverture d'un dossier"""
        # Récupérer l'ID du dossier depuis l'attribut temporaire
        folder_id = getattr(event.widget, '_folder_id', None)
        if folder_id:
            self.load_folder(folder_id)
    
    def go_back(self):
        """Retourner au dossier précédent"""
        if self.folder_history:
            previous_folder_id = self.folder_history.pop()
            
            # Charger le dossier précédent sans ajouter à l'historique
            self.current_folder_id = previous_folder_id
            self.back_button.config(
                state=tk.NORMAL if self.folder_history else tk.DISABLED
            )
            
            # Nettoyer et recharger
            for widget in self.content_frame.winfo_children():
                widget.destroy()
            
            folder_view = FolderView(
                self.content_frame,
                self.db,
                self.file_handler,
                previous_folder_id
            )
            folder_view.pack(fill=tk.BOTH, expand=True)
            folder_view.bind('<<FolderOpen>>', self.on_folder_open)
    
    def open_admin_with_auth(self):
        """Ouvrir le panneau admin avec authentification"""
        # Demander les identifiants
        auth_dialog = tk.Toplevel(self.root)
        auth_dialog.title("Authentification Administrateur")
        auth_dialog.geometry("400x250")
        auth_dialog.transient(self.root)
        auth_dialog.grab_set()
        auth_dialog.resizable(False, False)
        
        # Centrer
        auth_dialog.update_idletasks()
        x = (auth_dialog.winfo_screenwidth() // 2) - 200
        y = (auth_dialog.winfo_screenheight() // 2) - 125
        auth_dialog.geometry(f'400x250+{x}+{y}')
        
        # Contenu
        tk.Label(
            auth_dialog,
            text="🔒 Authentification Requise",
            font=('Segoe UI', 14, 'bold'),
            fg='#ff4d4d'
        ).pack(pady=(20, 10))
        
        tk.Label(
            auth_dialog,
            text="Veuillez entrer vos identifiants administrateur",
            font=('Segoe UI', 9),
            fg='#6c757d'
        ).pack(pady=(0, 20))
        
        # Username
        tk.Label(
            auth_dialog,
            text="Nom d'utilisateur:",
            font=('Segoe UI', 10)
        ).pack(anchor=tk.W, padx=30)
        
        username_entry = tk.Entry(
            auth_dialog,
            font=('Segoe UI', 11),
            relief=tk.SOLID,
            bd=1
        )
        username_entry.pack(fill=tk.X, padx=30, pady=(5, 10))
        username_entry.insert(0, "admin")
        username_entry.focus()
        
        # Password
        tk.Label(
            auth_dialog,
            text="Mot de passe:",
            font=('Segoe UI', 10)
        ).pack(anchor=tk.W, padx=30)
        
        password_entry = tk.Entry(
            auth_dialog,
            font=('Segoe UI', 11),
            relief=tk.SOLID,
            bd=1,
            show='●'
        )
        password_entry.pack(fill=tk.X, padx=30, pady=(5, 15))
        password_entry.insert(0, "admin")
        
        # Boutons
        button_frame = tk.Frame(auth_dialog)
        button_frame.pack(pady=10)
        
        def on_login():
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            
            if self.db.authenticate_admin(username, password):
                self.is_admin_authenticated = True
                self.admin_button.config(text="⚙️ Admin ✓", bg='#28a745')
                auth_dialog.destroy()
                self.open_admin()
            else:
                messagebox.showerror(
                    "Erreur",
                    "Identifiants incorrects",
                    parent=auth_dialog
                )
                password_entry.delete(0, tk.END)
                username_entry.focus()
        
        tk.Button(
            button_frame,
            text="Se connecter",
            font=('Segoe UI', 10, 'bold'),
            bg='#ff4d4d',
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=on_login
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Annuler",
            font=('Segoe UI', 10),
            bg='#6c757d',
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=auth_dialog.destroy
        ).pack(side=tk.LEFT, padx=5)
        
        # Enter pour valider
        auth_dialog.bind('<Return>', lambda e: on_login())
    
    def open_admin(self):
        """Ouvrir le panneau d'administration"""
        from .admin_window import AdminWindow
        admin_window = tk.Toplevel(self.root)
        AdminWindow(admin_window, self.db, self.file_handler, self.refresh_content)
    
    def refresh_content(self):
        """Rafraîchir le contenu affiché"""
        self.load_folder(self.current_folder_id)
