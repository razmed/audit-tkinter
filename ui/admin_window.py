import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Callable, Optional
import os

class AdminWindow:
    """Fenêtre d'administration"""
    
    def __init__(self, root: tk.Toplevel, db, file_handler, on_changes: Callable):
        self.root = root
        self.db = db
        self.file_handler = file_handler
        self.on_changes = on_changes
        
        self.root.title("Administration - Gestion des Dossiers")
        self.root.geometry("900x600")
        
        # Centrer la fenêtre
        self.center_window()
        
        # Créer l'interface
        self.create_widgets()
        
        # Charger les dossiers
        self.load_folders()
    
    def center_window(self):
        """Centrer la fenêtre"""
        self.root.update_idletasks()
        width = 900
        height = 600
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Créer les widgets"""
        # En-tête
        header = tk.Frame(self.root, bg='#000', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title_label = tk.Label(
            header,
            text="📁 Gestion des Dossiers",
            font=('Segoe UI', 16, 'bold'),
            bg='#000',
            fg='white'
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        close_button = tk.Button(
            header,
            text="✖️ Fermer",
            font=('Segoe UI', 10),
            bg='#dc3545',
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=self.root.destroy
        )
        close_button.pack(side=tk.RIGHT, padx=20)
        
        # Barre d'outils
        toolbar = tk.Frame(self.root, bg='#f8f9fa', height=60)
        toolbar.pack(fill=tk.X, pady=10)
        
        # Bouton "Nouveau Dossier"
        new_folder_btn = tk.Button(
            toolbar,
            text="➕ Nouveau Dossier",
            font=('Segoe UI', 10, 'bold'),
            bg='#28a745',
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=self.create_folder
        )
        new_folder_btn.pack(side=tk.LEFT, padx=10)
        
        # Bouton "Importer Dossier"
        import_folder_btn = tk.Button(
            toolbar,
            text="📂 Importer Dossier",
            font=('Segoe UI', 10, 'bold'),
            bg='#007bff',
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=self.import_folder
        )
        import_folder_btn.pack(side=tk.LEFT, padx=10)
        
        # Bouton "Importer Fichiers"
        import_files_btn = tk.Button(
            toolbar,
            text="📄 Importer Fichiers",
            font=('Segoe UI', 10, 'bold'),
            bg='#17a2b8',
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=self.import_files
        )
        import_files_btn.pack(side=tk.LEFT, padx=10)
        
        # Bouton "Rafraîchir"
        refresh_btn = tk.Button(
            toolbar,
            text="🔄 Rafraîchir",
            font=('Segoe UI', 10),
            bg='#6c757d',
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=self.load_folders
        )
        refresh_btn.pack(side=tk.LEFT, padx=10)
        
        # TreeView pour afficher les dossiers
        tree_frame = tk.Frame(self.root)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbars
        tree_scroll_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        
        # TreeView
        self.tree = ttk.Treeview(
            tree_frame,
            columns=('id', 'fichiers'),
            show='tree headings',
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set
        )
        
        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)
        
        # Colonnes
        self.tree.heading('#0', text='Nom du Dossier')
        self.tree.heading('id', text='ID')
        self.tree.heading('fichiers', text='Fichiers')
        
        self.tree.column('#0', width=400)
        self.tree.column('id', width=80)
        self.tree.column('fichiers', width=100)
        
        # Pack
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Menu contextuel
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="➕ Ajouter sous-dossier", command=self.add_subfolder)
        self.context_menu.add_command(label="✏️ Renommer", command=self.rename_folder)
        self.context_menu.add_command(label="📄 Gérer les fichiers", command=self.manage_files)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🗑️ Supprimer", command=self.delete_folder)
        
        # Bind clic droit
        self.tree.bind('<Button-3>', self.show_context_menu)
    
    def show_context_menu(self, event):
        """Afficher le menu contextuel"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def load_folders(self):
        """Charger les dossiers dans le TreeView"""
        # Nettoyer le TreeView
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Charger les dossiers racine
        root_folders = self.db.get_subfolders(None)
        for folder in root_folders:
            self.insert_folder(folder, '')
    
    def insert_folder(self, folder: dict, parent: str):
        """Insérer un dossier dans le TreeView"""
        file_count = self.db.count_files_in_folder(folder['id'], recursive=True)
        
        item_id = self.tree.insert(
            parent,
            'end',
            text=f"📁 {folder['name']}",
            values=(folder['id'], file_count)
        )
        
        # Charger les sous-dossiers
        subfolders = self.db.get_subfolders(folder['id'])
        for subfolder in subfolders:
            self.insert_folder(subfolder, item_id)
    
    def create_folder(self):
        """Créer un nouveau dossier"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Nouveau Dossier")
        dialog.geometry("400x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centrer
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 200
        y = (dialog.winfo_screenheight() // 2) - 75
        dialog.geometry(f'400x150+{x}+{y}')
        
        # Label
        tk.Label(
            dialog,
            text="Nom du dossier:",
            font=('Segoe UI', 10)
        ).pack(pady=(20, 5))
        
        # Entry
        name_entry = tk.Entry(dialog, font=('Segoe UI', 11), width=30)
        name_entry.pack(pady=5)
        name_entry.focus()
        
        # Boutons
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=20)
        
        def on_create():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("Erreur", "Veuillez entrer un nom")
                return
            
            try:
                self.db.create_folder(name, None)
                messagebox.showinfo("Succès", "Dossier créé avec succès")
                dialog.destroy()
                self.load_folders()
                self.on_changes()
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de créer le dossier:\n{e}")
        
        tk.Button(
            button_frame,
            text="Créer",
            font=('Segoe UI', 10, 'bold'),
            bg='#28a745',
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=on_create
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Annuler",
            font=('Segoe UI', 10),
            bg='#6c757d',
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=dialog.destroy
        ).pack(side=tk.LEFT, padx=5)
        
        # Enter pour créer
        dialog.bind('<Return>', lambda e: on_create())
    
    def add_subfolder(self):
        """Ajouter un sous-dossier"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner un dossier parent")
            return
        
        parent_id = self.tree.item(selection[0])['values'][0]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Nouveau Sous-Dossier")
        dialog.geometry("400x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centrer
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 200
        y = (dialog.winfo_screenheight() // 2) - 75
        dialog.geometry(f'400x150+{x}+{y}')
        
        tk.Label(
            dialog,
            text="Nom du sous-dossier:",
            font=('Segoe UI', 10)
        ).pack(pady=(20, 5))
        
        name_entry = tk.Entry(dialog, font=('Segoe UI', 11), width=30)
        name_entry.pack(pady=5)
        name_entry.focus()
        
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=20)
        
        def on_create():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("Erreur", "Veuillez entrer un nom")
                return
            
            try:
                self.db.create_folder(name, parent_id)
                messagebox.showinfo("Succès", "Sous-dossier créé avec succès")
                dialog.destroy()
                self.load_folders()
                self.on_changes()
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de créer le sous-dossier:\n{e}")
        
        tk.Button(
            button_frame,
            text="Créer",
            font=('Segoe UI', 10, 'bold'),
            bg='#28a745',
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=on_create
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Annuler",
            font=('Segoe UI', 10),
            bg='#6c757d',
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=dialog.destroy
        ).pack(side=tk.LEFT, padx=5)
        
        dialog.bind('<Return>', lambda e: on_create())
    
    def rename_folder(self):
        """Renommer un dossier"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner un dossier")
            return
        
        folder_id = self.tree.item(selection[0])['values'][0]
        folder = self.db.get_folder(folder_id)
        
        if not folder:
            messagebox.showerror("Erreur", "Dossier introuvable")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Renommer le Dossier")
        dialog.geometry("400x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centrer
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 200
        y = (dialog.winfo_screenheight() // 2) - 75
        dialog.geometry(f'400x150+{x}+{y}')
        
        tk.Label(
            dialog,
            text="Nouveau nom:",
            font=('Segoe UI', 10)
        ).pack(pady=(20, 5))
        
        name_entry = tk.Entry(dialog, font=('Segoe UI', 11), width=30)
        name_entry.insert(0, folder['name'])
        name_entry.pack(pady=5)
        name_entry.focus()
        name_entry.select_range(0, tk.END)
        
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=20)
        
        def on_rename():
            new_name = name_entry.get().strip()
            if not new_name:
                messagebox.showerror("Erreur", "Veuillez entrer un nom")
                return
            
            try:
                self.db.update_folder(folder_id, new_name)
                messagebox.showinfo("Succès", "Dossier renommé avec succès")
                dialog.destroy()
                self.load_folders()
                self.on_changes()
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de renommer le dossier:\n{e}")
        
        tk.Button(
            button_frame,
            text="Renommer",
            font=('Segoe UI', 10,'bold'),
            bg='#ffc107',
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=on_rename
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Annuler",
            font=('Segoe UI', 10),
            bg='#6c757d',
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=dialog.destroy
        ).pack(side=tk.LEFT, padx=5)
        
        dialog.bind('<Return>', lambda e: on_rename())
    
    def delete_folder(self):
        """Supprimer un dossier"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner un dossier")
            return
        
        folder_id = self.tree.item(selection[0])['values'][0]
        folder = self.db.get_folder(folder_id)
        
        if not folder:
            messagebox.showerror("Erreur", "Dossier introuvable")
            return
        
        # Confirmation
        response = messagebox.askyesno(
            "Confirmation",
            f"Êtes-vous sûr de vouloir supprimer le dossier '{folder['name']}' ?\n\n"
            "Tous les fichiers et sous-dossiers seront également supprimés.",
            icon='warning'
        )
        
        if response:
            try:
                self.db.delete_folder(folder_id)
                messagebox.showinfo("Succès", "Dossier supprimé avec succès")
                self.load_folders()
                self.on_changes()
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de supprimer le dossier:\n{e}")
    
    def manage_files(self):
        """Gérer les fichiers d'un dossier"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner un dossier")
            return
        
        folder_id = self.tree.item(selection[0])['values'][0]
        folder = self.db.get_folder(folder_id)
        
        if not folder:
            messagebox.showerror("Erreur", "Dossier introuvable")
            return
        
        # Ouvrir une fenêtre de gestion des fichiers
        file_window = tk.Toplevel(self.root)
        FileManagerWindow(file_window, self.db, self.file_handler, folder, self.on_changes)
    
    def import_folder(self):
        """Importer un dossier complet avec son arborescence"""
        folder_path = filedialog.askdirectory(title="Sélectionner un dossier à importer")
        
        if not folder_path:
            return
        
        # Demander confirmation
        response = messagebox.askyesno(
            "Confirmation",
            f"Voulez-vous importer le dossier :\n\n{folder_path}\n\n"
            "Tous les fichiers et sous-dossiers seront importés.",
            icon='question'
        )
        
        if response:
            try:
                # Afficher une fenêtre de progression
                progress_window = tk.Toplevel(self.root)
                progress_window.title("Importation en cours...")
                progress_window.geometry("500x200")
                progress_window.transient(self.root)
                progress_window.grab_set()
                
                # Centrer
                progress_window.update_idletasks()
                x = (progress_window.winfo_screenwidth() // 2) - 250
                y = (progress_window.winfo_screenheight() // 2) - 100
                progress_window.geometry(f'500x200+{x}+{y}')
                
                tk.Label(
                    progress_window,
                    text="⏳ Importation en cours...",
                    font=('Segoe UI', 14, 'bold'),
                    fg='#007bff'
                ).pack(pady=20)
                
                progress_label = tk.Label(
                    progress_window,
                    text="Analyse du dossier et importation des fichiers...\nCela peut prendre quelques instants.",
                    font=('Segoe UI', 10),
                    fg='#6c757d',
                    justify=tk.CENTER
                )
                progress_label.pack(pady=10)
                
                # Message d'info
                info_label = tk.Label(
                    progress_window,
                    text="✓ Tous les fichiers (.docx, .pdf, .xlsx, etc.) seront importés\n✓ L'arborescence des dossiers sera conservée",
                    font=('Segoe UI', 9),
                    fg='#28a745',
                    justify=tk.LEFT
                )
                info_label.pack(pady=10)
                
                progress_window.update()
                
                # Importer les fichiers
                print("\n" + "="*60)
                print("DÉBUT DE L'IMPORTATION")
                print("="*60)
                count = self.file_handler.save_files_from_folder(folder_path, self.db, None)
                print("="*60)
                print(f"FIN DE L'IMPORTATION: {count} fichier(s)")
                print("="*60 + "\n")
                
                progress_window.destroy()
                
                messagebox.showinfo(
                    "Succès",
                    f"✅ {count} fichier(s) importé(s) avec succès !\n\n"
                    f"Le dossier '{os.path.basename(folder_path)}' et tous ses fichiers ont été ajoutés."
                )
                
                self.load_folders()
                self.on_changes()
                
            except Exception as e:
                if 'progress_window' in locals():
                    progress_window.destroy()
                messagebox.showerror("Erreur", f"Impossible d'importer le dossier:\n\n{e}")
                import traceback
                traceback.print_exc()
    
    def import_files(self):
        """Importer des fichiers dans un dossier"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning(
                "Attention",
                "Veuillez d'abord sélectionner un dossier de destination"
            )
            return
        
        folder_id = self.tree.item(selection[0])['values'][0]
        
        file_paths = filedialog.askopenfilenames(
            title="Sélectionner des fichiers à importer"
        )
        
        if not file_paths:
            return
        
        try:
            success_count = 0
            error_count = 0
            
            for file_path in file_paths:
                filename = os.path.basename(file_path)
                success, dest_path = self.file_handler.save_file(file_path, filename)
                
                if success:
                    self.db.add_file(folder_id, filename, dest_path)
                    success_count += 1
                else:
                    error_count += 1
            
            if error_count == 0:
                messagebox.showinfo(
                    "Succès",
                    f"✅ {success_count} fichier(s) importé(s) avec succès !"
                )
            else:
                messagebox.showwarning(
                    "Attention",
                    f"{success_count} fichier(s) importé(s), {error_count} erreur(s)"
                )
            
            self.load_folders()
            self.on_changes()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'importer les fichiers:\n{e}")


class FileManagerWindow:
    """Fenêtre de gestion des fichiers d'un dossier"""
    
    def __init__(self, root: tk.Toplevel, db, file_handler, folder: dict, on_changes: Callable):
        self.root = root
        self.db = db
        self.file_handler = file_handler
        self.folder = folder
        self.on_changes = on_changes
        
        self.root.title(f"Fichiers - {folder['name']}")
        self.root.geometry("800x500")
        
        # Centrer la fenêtre
        self.center_window()
        
        # Créer l'interface
        self.create_widgets()
        
        # Charger les fichiers
        self.load_files()
    
    def center_window(self):
        """Centrer la fenêtre"""
        self.root.update_idletasks()
        width = 800
        height = 500
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Créer les widgets"""
        # En-tête
        header = tk.Frame(self.root, bg='#17a2b8', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title_label = tk.Label(
            header,
            text=f"📄 Fichiers - {self.folder['name']}",
            font=('Segoe UI', 14, 'bold'),
            bg='#17a2b8',
            fg='white'
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        close_button = tk.Button(
            header,
            text="✖️ Fermer",
            font=('Segoe UI', 10),
            bg='#dc3545',
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=self.root.destroy
        )
        close_button.pack(side=tk.RIGHT, padx=20)
        
        # Barre d'outils
        toolbar = tk.Frame(self.root, bg='#f8f9fa', height=60)
        toolbar.pack(fill=tk.X, pady=10)
        
        # Bouton "Ajouter Fichiers"
        add_files_btn = tk.Button(
            toolbar,
            text="➕ Ajouter Fichiers",
            font=('Segoe UI', 10, 'bold'),
            bg='#28a745',
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=self.add_files
        )
        add_files_btn.pack(side=tk.LEFT, padx=10)
        
        # Bouton "Supprimer"
        delete_btn = tk.Button(
            toolbar,
            text="🗑️ Supprimer",
            font=('Segoe UI', 10, 'bold'),
            bg='#dc3545',
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=self.delete_file
        )
        delete_btn.pack(side=tk.LEFT, padx=10)
        
        # Bouton "Ouvrir"
        open_btn = tk.Button(
            toolbar,
            text="👁️ Ouvrir",
            font=('Segoe UI', 10, 'bold'),
            bg='#007bff',
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=self.open_file
        )
        open_btn.pack(side=tk.LEFT, padx=10)
        
        # Bouton "Rafraîchir"
        refresh_btn = tk.Button(
            toolbar,
            text="🔄 Rafraîchir",
            font=('Segoe UI', 10),
            bg='#6c757d',
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=self.load_files
        )
        refresh_btn.pack(side=tk.LEFT, padx=10)
        
        # Listbox pour afficher les fichiers
        list_frame = tk.Frame(self.root)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
        
        # Listbox
        self.file_listbox = tk.Listbox(
            list_frame,
            font=('Segoe UI', 10),
            yscrollcommand=scrollbar.set,
            selectmode=tk.SINGLE
        )
        
        scrollbar.config(command=self.file_listbox.yview)
        
        # Pack
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Double-clic pour ouvrir
        self.file_listbox.bind('<Double-Button-1>', lambda e: self.open_file())
    
    def load_files(self):
        """Charger les fichiers"""
        self.file_listbox.delete(0, tk.END)
        
        files = self.db.get_files_in_folder(self.folder['id'])
        
        for file in files:
            extension = file['filename'].rsplit('.', 1)[-1].lower() if '.' in file['filename'] else ''
            icon = self.file_handler.get_file_icon(extension)
            
            # Taille du fichier
            try:
                size = os.path.getsize(file['filepath']) if os.path.exists(file['filepath']) else 0
                size_formatted = self.format_file_size(size)
            except:
                size_formatted = "N/A"
            
            display_text = f"{icon} {file['filename']} ({size_formatted})"
            self.file_listbox.insert(tk.END, display_text)
        
        if not files:
            self.file_listbox.insert(tk.END, "Aucun fichier dans ce dossier")
    
    @staticmethod
    def format_file_size(size: int) -> str:
        """Formater la taille d'un fichier"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"
    
    def add_files(self):
        """Ajouter des fichiers"""
        file_paths = filedialog.askopenfilenames(
            title="Sélectionner des fichiers à ajouter"
        )
        
        if not file_paths:
            return
        
        try:
            success_count = 0
            error_count = 0
            
            for file_path in file_paths:
                filename = os.path.basename(file_path)
                success, dest_path = self.file_handler.save_file(file_path, filename)
                
                if success:
                    self.db.add_file(self.folder['id'], filename, dest_path)
                    success_count += 1
                else:
                    error_count += 1
            
            if error_count == 0:
                messagebox.showinfo(
                    "Succès",
                    f"✅ {success_count} fichier(s) ajouté(s) avec succès !"
                )
            else:
                messagebox.showwarning(
                    "Attention",
                    f"{success_count} fichier(s) ajouté(s), {error_count} erreur(s)"
                )
            
            self.load_files()
            self.on_changes()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'ajouter les fichiers:\n{e}")
    
    def delete_file(self):
        """Supprimer le fichier sélectionné"""
        selection = self.file_listbox.curselection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner un fichier")
            return
        
        index = selection[0]
        files = self.db.get_files_in_folder(self.folder['id'])
        
        if index >= len(files):
            return
        
        file = files[index]
        
        # Confirmation
        response = messagebox.askyesno(
            "Confirmation",
            f"Êtes-vous sûr de vouloir supprimer le fichier :\n\n{file['filename']} ?",
            icon='warning'
        )
        
        if response:
            try:
                self.db.delete_file(file['id'])
                messagebox.showinfo("Succès", "Fichier supprimé avec succès")
                self.load_files()
                self.on_changes()
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de supprimer le fichier:\n{e}")
    
    def open_file(self):
        """Ouvrir le fichier sélectionné"""
        selection = self.file_listbox.curselection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner un fichier")
            return
        
        index = selection[0]
        files = self.db.get_files_in_folder(self.folder['id'])
        
        if index >= len(files):
            return
        
        file = files[index]
        
        if not os.path.exists(file['filepath']):
            messagebox.showerror("Erreur", "Le fichier n'existe pas")
            return
        
        success = self.file_handler.open_file(file['filepath'])
        if not success:
            messagebox.showerror("Erreur", "Impossible d'ouvrir le fichier")