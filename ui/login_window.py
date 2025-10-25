import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable

class LoginWindow:
    """Fenêtre de connexion - NON UTILISÉE dans la version actuelle
    
    L'application démarre directement sur la fenêtre principale.
    L'authentification admin se fait via un popup dans MainWindow.
    """
    
    def __init__(self, root: tk.Tk, on_login_success: Callable):
        self.root = root
        self.on_login_success = on_login_success
        
        self.root.title("Connexion - Portail Document")
        self.root.geometry("400x500")
        self.root.resizable(False, False)
        
        # Centrer la fenêtre
        self.center_window()
        
        # Style
        self.setup_styles()
        
        # Interface
        self.create_widgets()
    
    def center_window(self):
        """Centrer la fenêtre sur l'écran"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_styles(self):
        """Configurer les styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Style pour les boutons
        style.configure(
            'Login.TButton',
            font=('Segoe UI', 11, 'bold'),
            padding=10,
            background='#ff4d4d',
            foreground='white'
        )
        style.map('Login.TButton',
            background=[('active', '#e63c3c')]
        )
    
    def create_widgets(self):
        """Créer les widgets de l'interface"""
        # Frame principal avec fond dégradé (simulé)
        main_frame = tk.Frame(self.root, bg='#f8f9fa')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Logo (emoji temporaire)
        logo_label = tk.Label(
            main_frame,
            text="📁",
            font=('Arial', 60),
            bg='#f8f9fa'
        )
        logo_label.pack(pady=(20, 10))
        
        # Titre de l'entreprise
        title_label = tk.Label(
            main_frame,
            text="Société Nationale des Travaux Publics",
            font=('Segoe UI', 14, 'bold'),
            bg='#f8f9fa',
            fg='#212529'
        )
        title_label.pack(pady=5)
        
        # Sous-titre
        subtitle_label = tk.Label(
            main_frame,
            text="Interface Employer",
            font=('Segoe UI', 10),
            bg='#f8f9fa',
            fg='#6c757d'
        )
        subtitle_label.pack(pady=(0, 30))
        
        # Frame de connexion
        login_frame = tk.Frame(main_frame, bg='white', relief=tk.RAISED, bd=1)
        login_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Titre de connexion
        login_title = tk.Label(
            login_frame,
            text="Connexion",
            font=('Segoe UI', 16, 'bold'),
            bg='white',
            fg='#212529'
        )
        login_title.pack(pady=(20, 30))
        
        # Champ utilisateur
        username_label = tk.Label(
            login_frame,
            text="Nom d'utilisateur",
            font=('Segoe UI', 10),
            bg='white',
            fg='#495057'
        )
        username_label.pack(anchor=tk.W, padx=20)
        
        self.username_entry = tk.Entry(
            login_frame,
            font=('Segoe UI', 11),
            relief=tk.SOLID,
            bd=1,
            bg='#f1f3f5'
        )
        self.username_entry.pack(fill=tk.X, padx=20, pady=(5, 15))
        self.username_entry.insert(0, "admin")  # Valeur par défaut
        
        # Champ mot de passe
        password_label = tk.Label(
            login_frame,
            text="Mot de passe",
            font=('Segoe UI', 10),
            bg='white',
            fg='#495057'
        )
        password_label.pack(anchor=tk.W, padx=20)
        
        self.password_entry = tk.Entry(
            login_frame,
            font=('Segoe UI', 11),
            relief=tk.SOLID,
            bd=1,
            bg='#f1f3f5',
            show='●'
        )
        self.password_entry.pack(fill=tk.X, padx=20, pady=(5, 20))
        self.password_entry.insert(0, "admin")  # Valeur par défaut
        
        # Bouton de connexion
        login_button = tk.Button(
            login_frame,
            text="Se connecter",
            font=('Segoe UI', 11, 'bold'),
            bg='#ff4d4d',
            fg='white',
            activebackground='#e63c3c',
            activeforeground='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=self.login
        )
        login_button.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Permettre la connexion avec Entrée
        self.root.bind('<Return>', lambda e: self.login())
    
    def login(self):
        """Gérer la connexion"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror(
                "Erreur",
                "Veuillez remplir tous les champs"
            )
            return
        
        # Appeler le callback de connexion
        self.on_login_success(username, password)