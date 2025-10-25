import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, Callable
import os

class FolderView(tk.Frame):
    """Vue pour afficher le contenu d'un dossier"""
    
    def __init__(self, parent, db, file_handler, folder_id: Optional[int] = None):
        super().__init__(parent, bg='#f8f9fa')
        
        self.db = db
        self.file_handler = file_handler
        self.folder_id = folder_id
        
        self.create_widgets()
        self.load_content()
    
    def create_widgets(self):
        """Créer les widgets"""
        # En-tête avec fil d'Ariane
        header_frame = tk.Frame(self, bg='white', relief=tk.SOLID, bd=1)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.breadcrumb_label = tk.Label(
            header_frame,
            text="",
            font=('Segoe UI', 10),
            bg='white',
            fg='#667eea',
            anchor=tk.W
        )
        self.breadcrumb_label.pack(side=tk.LEFT, padx=15, pady=10)
        
        # Frame de contenu avec scrollbar
        content_container = tk.Frame(self, bg='#f8f9fa')
        content_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Canvas et scrollbar
        canvas = tk.Canvas(content_container, bg='#f8f9fa', highlightthickness=0)
        scrollbar = ttk.Scrollbar(content_container, orient=tk.VERTICAL, command=canvas.yview)
        
        self.scrollable_frame = tk.Frame(canvas, bg='#f8f9fa')
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Permettre le scroll avec la molette
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)
    
    def load_content(self):
        """Charger le contenu du dossier"""
        # Nettoyer le contenu précédent
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Charger le fil d'Ariane
        self.load_breadcrumb()
        
        # Charger les sous-dossiers
        subfolders = self.db.get_subfolders(self.folder_id)
        if subfolders:
            self.create_section("📁 Sous-dossiers", subfolders, is_folder=True)
        
        # Charger les fichiers
        if self.folder_id is not None:
            files = self.db.get_files_in_folder(self.folder_id)
            if files:
                self.create_section("📄 Fichiers", files, is_folder=False)
        
        # Message si vide
        if not subfolders and (self.folder_id is None or not self.db.get_files_in_folder(self.folder_id)):
            empty_label = tk.Label(
                self.scrollable_frame,
                text="📭 Dossier vide",
                font=('Segoe UI', 14),
                bg='#f8f9fa',
                fg='#6c757d'
            )
            empty_label.pack(pady=50)
    
    def load_breadcrumb(self):
        """Charger le fil d'Ariane"""
        if self.folder_id is None:
            self.breadcrumb_label.config(text="🏠 Accueil")
        else:
            path = self.db.get_folder_path(self.folder_id)
            breadcrumb_text = "🏠 Accueil"
            for folder in path:
                breadcrumb_text += f" > {folder['name']}"
            self.breadcrumb_label.config(text=breadcrumb_text)
    
    def create_section(self, title: str, items: list, is_folder: bool):
        """Créer une section (dossiers ou fichiers)"""
        # Titre de section
        title_label = tk.Label(
            self.scrollable_frame,
            text=f"{title} ({len(items)})",
            font=('Segoe UI', 12, 'bold'),
            bg='#f8f9fa',
            fg='#212529'
        )
        title_label.pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        # Grille d'items
        grid_frame = tk.Frame(self.scrollable_frame, bg='#f8f9fa')
        grid_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Afficher les items en grille (3 colonnes)
        for idx, item in enumerate(items):
            row = idx // 3
            col = idx % 3
            
            if is_folder:
                card = self.create_folder_card(grid_frame, item)
            else:
                card = self.create_file_card(grid_frame, item)
            
            card.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
        
        # Configurer les colonnes pour qu'elles s'étendent uniformément
        for i in range(3):
            grid_frame.columnconfigure(i, weight=1, uniform='column')
    
    def create_folder_card(self, parent, folder: dict) -> tk.Frame:
        """Créer une carte pour un dossier"""
        card = tk.Frame(parent, bg='white', relief=tk.RAISED, bd=1, cursor='hand2')
        card.pack_propagate(False)
        card.configure(width=200, height=120)
        
        # Icône de dossier
        icon_label = tk.Label(
            card,
            text="📁",
            font=('Arial', 32),
            bg='white'
        )
        icon_label.pack(pady=(15, 5))
        
        # Nom du dossier
        name_label = tk.Label(
            card,
            text=folder['name'],
            font=('Segoe UI', 10, 'bold'),
            bg='white',
            fg='#212529',
            wraplength=180
        )
        name_label.pack(pady=5)
        
        # Nombre de fichiers
        file_count = self.db.count_files_in_folder(folder['id'], recursive=True)
        count_label = tk.Label(
            card,
            text=f"{file_count} fichier{'s' if file_count > 1 else ''}",
            font=('Segoe UI', 9),
            bg='white',
            fg='#6c757d'
        )
        count_label.pack()
        
        # Événement de clic - CORRECTION ICI
        def on_click(event=None):
            # Stocker l'ID dans un attribut temporaire
            self._folder_id = folder['id']
            # Générer l'événement personnalisé
            self.event_generate('<<FolderOpen>>')
        
        # Lier tous les widgets au clic
        card.bind('<Button-1>', on_click)
        icon_label.bind('<Button-1>', on_click)
        name_label.bind('<Button-1>', on_click)
        count_label.bind('<Button-1>', on_click)
        
        # Effet hover
        def on_enter(event):
            card.config(bg='#f8f9fa')
            icon_label.config(bg='#f8f9fa')
            name_label.config(bg='#f8f9fa')
            count_label.config(bg='#f8f9fa')
        
        def on_leave(event):
            card.config(bg='white')
            icon_label.config(bg='white')
            name_label.config(bg='white')
            count_label.config(bg='white')
        
        card.bind('<Enter>', on_enter)
        card.bind('<Leave>', on_leave)
        icon_label.bind('<Enter>', on_enter)
        icon_label.bind('<Leave>', on_leave)
        name_label.bind('<Enter>', on_enter)
        name_label.bind('<Leave>', on_leave)
        count_label.bind('<Enter>', on_enter)
        count_label.bind('<Leave>', on_leave)
        
        return card
    
    def create_file_card(self, parent, file: dict) -> tk.Frame:
        """Créer une carte pour un fichier"""
        card = tk.Frame(parent, bg='white', relief=tk.RAISED, bd=1)
        card.pack_propagate(False)
        card.configure(width=200, height=140)
        
        # Récupérer l'extension et l'icône
        extension = file['filename'].rsplit('.', 1)[-1].lower() if '.' in file['filename'] else ''
        icon = self.file_handler.get_file_icon(extension)
        
        # Icône du fichier
        icon_label = tk.Label(
            card,
            text=icon,
            font=('Arial', 32),
            bg='white'
        )
        icon_label.pack(pady=(10, 5))
        
        # Nom du fichier
        name_label = tk.Label(
            card,
            text=file['filename'],
            font=('Segoe UI', 9, 'bold'),
            bg='white',
            fg='#212529',
            wraplength=180
        )
        name_label.pack(pady=5)
        
        # Taille du fichier
        try:
            size = os.path.getsize(file['filepath']) if os.path.exists(file['filepath']) else 0
            size_formatted = self.format_file_size(size)
        except:
            size_formatted = "N/A"
        
        size_label = tk.Label(
            card,
            text=size_formatted,
            font=('Segoe UI', 8),
            bg='white',
            fg='#6c757d'
        )
        size_label.pack()
        
        # Boutons d'action
        button_frame = tk.Frame(card, bg='white')
        button_frame.pack(pady=5)
        
        # Bouton "Ouvrir"
        open_btn = tk.Button(
            button_frame,
            text="👁️ Voir",
            font=('Segoe UI', 8),
            bg='#4facfe',
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=lambda: self.open_file(file)
        )
        open_btn.pack(side=tk.LEFT, padx=2)
        
        # Bouton "Télécharger" (copier vers...)
        download_btn = tk.Button(
            button_frame,
            text="💾",
            font=('Segoe UI', 8),
            bg='#11998e',
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=lambda: self.save_file_as(file)
        )
        download_btn.pack(side=tk.LEFT, padx=2)
        
        return card
    
    @staticmethod
    def format_file_size(size: int) -> str:
        """Formater la taille d'un fichier"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"
    
    def open_file(self, file: dict):
        """Ouvrir un fichier"""
        if not os.path.exists(file['filepath']):
            messagebox.showerror("Erreur", "Le fichier n'existe pas")
            return
        
        success = self.file_handler.open_file(file['filepath'])
        if not success:
            messagebox.showerror("Erreur", "Impossible d'ouvrir le fichier")
    
    def save_file_as(self, file: dict):
        """Enregistrer une copie du fichier"""
        if not os.path.exists(file['filepath']):
            messagebox.showerror("Erreur", "Le fichier n'existe pas")
            return
        
        # Demander où enregistrer
        destination = filedialog.asksaveasfilename(
            defaultextension=f".{file['filename'].rsplit('.', 1)[-1]}",
            initialfile=file['filename'],
            title="Enregistrer sous"
        )
        
        if destination:
            try:
                import shutil
                shutil.copy2(file['filepath'], destination)
                messagebox.showinfo("Succès", "Fichier enregistré avec succès")
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible d'enregistrer le fichier:\n{e}")
