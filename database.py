import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

class Database:
    """Gestion de la base de données SQLite"""
    
    def __init__(self, db_path: str = "portal.db"):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()
        self.create_default_admin()
    
    def connect(self):
        """Établir la connexion à la base de données"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            print(f"✅ Connexion à la base de données réussie: {self.db_path}")
        except sqlite3.Error as e:
            print(f"❌ Erreur de connexion à la base de données: {e}")
            raise
    
    def create_tables(self):
        """Créer les tables nécessaires"""
        try:
            # Table admins
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS admins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table folders
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS folders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    parent_id INTEGER DEFAULT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (parent_id) REFERENCES folders(id) ON DELETE CASCADE
                )
            """)
            
            # Table files
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    folder_id INTEGER NOT NULL,
                    filename TEXT NOT NULL,
                    filepath TEXT NOT NULL,
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (folder_id) REFERENCES folders(id) ON DELETE CASCADE
                )
            """)
            
            self.conn.commit()
            print("✅ Tables créées avec succès")
        except sqlite3.Error as e:
            print(f"❌ Erreur lors de la création des tables: {e}")
            raise
    
    def create_default_admin(self):
        """Créer un compte admin par défaut"""
        try:
            self.cursor.execute(
                "SELECT COUNT(*) FROM admins WHERE email = ?", 
                ('admin',)
            )
            if self.cursor.fetchone()[0] == 0:
                self.cursor.execute(
                    "INSERT INTO admins (email, password) VALUES (?, ?)",
                    ('admin', 'admin')  # En production, hasher le mot de passe
                )
                self.conn.commit()
                print("✅ Admin par défaut créé (admin/admin)")
        except sqlite3.Error as e:
            print(f"❌ Erreur lors de la création de l'admin: {e}")
    
    def authenticate_admin(self, email: str, password: str) -> bool:
        """Authentifier un administrateur"""
        try:
            self.cursor.execute(
                "SELECT * FROM admins WHERE email = ? AND password = ?",
                (email, password)
            )
            result = self.cursor.fetchone()
            return result is not None
        except sqlite3.Error as e:
            print(f"❌ Erreur d'authentification: {e}")
            return False
    
    # ==================== GESTION DES DOSSIERS ====================
    
    def create_folder(self, name: str, parent_id: Optional[int] = None) -> int:
        """Créer un nouveau dossier"""
        try:
            self.cursor.execute(
                "INSERT INTO folders (name, parent_id) VALUES (?, ?)",
                (name, parent_id)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"❌ Erreur lors de la création du dossier: {e}")
            raise
    
    def get_folder(self, folder_id: int) -> Optional[Dict[str, Any]]:
        """Récupérer un dossier par son ID"""
        try:
            self.cursor.execute(
                "SELECT * FROM folders WHERE id = ?",
                (folder_id,)
            )
            row = self.cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            print(f"❌ Erreur lors de la récupération du dossier: {e}")
            return None
    
    def get_all_folders(self) -> List[Dict[str, Any]]:
        """Récupérer tous les dossiers"""
        try:
            self.cursor.execute("SELECT * FROM folders ORDER BY name ASC")
            return [dict(row) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"❌ Erreur lors de la récupération des dossiers: {e}")
            return []
    
    def get_subfolders(self, parent_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Récupérer les sous-dossiers d'un dossier parent"""
        try:
            if parent_id is None:
                self.cursor.execute(
                    "SELECT * FROM folders WHERE parent_id IS NULL ORDER BY name ASC"
                )
            else:
                self.cursor.execute(
                    "SELECT * FROM folders WHERE parent_id = ? ORDER BY name ASC",
                    (parent_id,)
                )
            return [dict(row) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"❌ Erreur lors de la récupération des sous-dossiers: {e}")
            return []
    
    def update_folder(self, folder_id: int, name: str) -> bool:
        """Renommer un dossier"""
        try:
            self.cursor.execute(
                "UPDATE folders SET name = ? WHERE id = ?",
                (name, folder_id)
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"❌ Erreur lors de la mise à jour du dossier: {e}")
            return False
    
    def delete_folder(self, folder_id: int) -> bool:
        """Supprimer un dossier et ses fichiers"""
        try:
            # Supprimer les fichiers du dossier
            self.cursor.execute(
                "SELECT filepath FROM files WHERE folder_id = ?",
                (folder_id,)
            )
            files = self.cursor.fetchall()
            
            # Supprimer les fichiers physiques
            for file in files:
                try:
                    if os.path.exists(file['filepath']):
                        os.remove(file['filepath'])
                except Exception as e:
                    print(f"⚠️ Impossible de supprimer le fichier {file['filepath']}: {e}")
            
            # Supprimer le dossier de la base
            self.cursor.execute("DELETE FROM folders WHERE id = ?", (folder_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"❌ Erreur lors de la suppression du dossier: {e}")
            return False
    
    def get_folder_path(self, folder_id: int) -> List[Dict[str, Any]]:
        """Récupérer le chemin complet d'un dossier (breadcrumb)"""
        path = []
        current_id = folder_id
        
        while current_id is not None:
            folder = self.get_folder(current_id)
            if folder:
                path.insert(0, folder)
                current_id = folder['parent_id']
            else:
                break
        
        return path
    
    # ==================== GESTION DES FICHIERS ====================
    
    def add_file(self, folder_id: int, filename: str, filepath: str) -> int:
        """Ajouter un fichier à la base de données"""
        try:
            self.cursor.execute(
                "INSERT INTO files (folder_id, filename, filepath) VALUES (?, ?, ?)",
                (folder_id, filename, filepath)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"❌ Erreur lors de l'ajout du fichier: {e}")
            raise
    
    def get_files_in_folder(self, folder_id: int) -> List[Dict[str, Any]]:
        """Récupérer tous les fichiers d'un dossier"""
        try:
            self.cursor.execute(
                "SELECT * FROM files WHERE folder_id = ? ORDER BY uploaded_at DESC",
                (folder_id,)
            )
            return [dict(row) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"❌ Erreur lors de la récupération des fichiers: {e}")
            return []
    
    def get_file(self, file_id: int) -> Optional[Dict[str, Any]]:
        """Récupérer un fichier par son ID"""
        try:
            self.cursor.execute("SELECT * FROM files WHERE id = ?", (file_id,))
            row = self.cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            print(f"❌ Erreur lors de la récupération du fichier: {e}")
            return None
    
    def delete_file(self, file_id: int) -> bool:
        """Supprimer un fichier"""
        try:
            # Récupérer le chemin du fichier
            file = self.get_file(file_id)
            if file:
                # Supprimer le fichier physique
                try:
                    if os.path.exists(file['filepath']):
                        os.remove(file['filepath'])
                except Exception as e:
                    print(f"⚠️ Impossible de supprimer le fichier physique: {e}")
                
                # Supprimer de la base
                self.cursor.execute("DELETE FROM files WHERE id = ?", (file_id,))
                self.conn.commit()
                return True
            return False
        except sqlite3.Error as e:
            print(f"❌ Erreur lors de la suppression du fichier: {e}")
            return False
    
    def count_files_in_folder(self, folder_id: int, recursive: bool = False) -> int:
        """Compter les fichiers dans un dossier"""
        try:
            if not recursive:
                self.cursor.execute(
                    "SELECT COUNT(*) as count FROM files WHERE folder_id = ?",
                    (folder_id,)
                )
                return self.cursor.fetchone()[0]
            else:
                # Compter récursivement
                count = self.count_files_in_folder(folder_id, recursive=False)
                subfolders = self.get_subfolders(folder_id)
                for subfolder in subfolders:
                    count += self.count_files_in_folder(subfolder['id'], recursive=True)
                return count
        except sqlite3.Error as e:
            print(f"❌ Erreur lors du comptage des fichiers: {e}")
            return 0
    
    def close(self):
        """Fermer la connexion à la base de données"""
        if self.conn:
            self.conn.close()
            print("✅ Connexion à la base de données fermée")