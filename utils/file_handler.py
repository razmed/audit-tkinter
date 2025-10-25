import os
import shutil
from typing import Optional, Tuple
from pathlib import Path

class FileHandler:
    """Gestionnaire de fichiers avec import récursif corrigé"""
    
    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = upload_dir
        self.create_upload_directory()
    
    def create_upload_directory(self):
        """Créer le répertoire d'upload s'il n'existe pas"""
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir, exist_ok=True)
            print(f"✅ Répertoire {self.upload_dir} créé")
    
    def save_file(self, source_path: str, filename: str) -> Tuple[bool, str]:
        """
        Copier un fichier dans le répertoire d'upload
        
        Returns:
            Tuple[bool, str]: (succès, chemin_destination)
        """
        try:
            # Générer un nom de fichier unique
            import time
            timestamp = int(time.time() * 1000)  # Millisecondes pour plus d'unicité
            safe_filename = self.sanitize_filename(filename)
            unique_filename = f"{timestamp}_{safe_filename}"
            
            destination = os.path.join(self.upload_dir, unique_filename)
            
            # Copier le fichier
            shutil.copy2(source_path, destination)
            print(f"✅ Fichier copié: {source_path} -> {destination}")
            
            return True, destination
        except Exception as e:
            print(f"❌ Erreur lors de la copie du fichier {source_path}: {e}")
            return False, ""
    
    def save_files_from_folder(self, folder_path: str, db, parent_folder_id: Optional[int] = None) -> int:
        """
        ✅ CORRECTION MAJEURE: Importer récursivement TOUS les fichiers d'un dossier
        
        Cette fonction importe maintenant:
        - TOUS les fichiers (.docx, .pdf, .xlsx, .txt, images, etc.)
        - Toute l'arborescence de sous-dossiers
        - Conserve la structure exacte du dossier source
        
        Args:
            folder_path: Chemin du dossier source à importer
            db: Instance de la base de données
            parent_folder_id: ID du dossier parent dans la DB (None pour racine)
        
        Returns:
            int: Nombre de fichiers importés
        """
        count = 0
        folder_name = os.path.basename(folder_path)
        
        print(f"\n📂 IMPORTATION: {folder_name}")
        print(f"   📍 Source: {folder_path}")
        print(f"   🔗 Parent ID: {parent_folder_id}")
        
        # Créer le dossier dans la base de données
        try:
            folder_id = db.create_folder(folder_name, parent_folder_id)
            print(f"   ✅ Dossier DB créé (ID: {folder_id})")
        except Exception as e:
            print(f"   ❌ Erreur création dossier DB: {e}")
            return 0
        
        try:
            # Lister TOUS les éléments du dossier
            items = os.listdir(folder_path)
            print(f"   📋 {len(items)} élément(s) trouvé(s)")
            
            for item in items:
                item_path = os.path.join(folder_path, item)
                
                # CAS 1: C'est un FICHIER
                if os.path.isfile(item_path):
                    print(f"      📄 Fichier: {item}")
                    
                    # ✅ CORRECTION: On importe TOUS les fichiers, pas de filtre
                    # Copier le fichier dans uploads/
                    success, dest_path = self.save_file(item_path, item)
                    
                    if success:
                        # Ajouter à la base de données
                        try:
                            file_id = db.add_file(folder_id, item, dest_path)
                            count += 1
                            print(f"         ✅ Ajouté à la DB (ID: {file_id})")
                        except Exception as db_error:
                            print(f"         ❌ Erreur DB: {db_error}")
                    else:
                        print(f"         ❌ Échec de la copie")
                
                # CAS 2: C'est un SOUS-DOSSIER
                elif os.path.isdir(item_path):
                    print(f"      📁 Sous-dossier: {item}")
                    
                    # ✅ APPEL RÉCURSIF pour traiter le sous-dossier
                    subfolder_count = self.save_files_from_folder(item_path, db, folder_id)
                    count += subfolder_count
                    print(f"      ✅ {subfolder_count} fichier(s) depuis '{item}'")
        
        except Exception as e:
            print(f"   ❌ ERREUR lors de l'importation: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"📂 FIN '{folder_name}': {count} fichier(s) importé(s)\n")
        return count
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Nettoyer un nom de fichier pour éviter les caractères problématiques"""
        import re
        # Remplacer les caractères non autorisés par des underscores
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Limiter la longueur à 200 caractères
        if len(filename) > 200:
            name, ext = os.path.splitext(filename)
            filename = name[:200-len(ext)] + ext
        return filename
    
    @staticmethod
    def open_file(filepath: str) -> bool:
        """Ouvrir un fichier avec l'application par défaut du système"""
        try:
            import platform
            import subprocess
            
            if not os.path.exists(filepath):
                print(f"❌ Le fichier n'existe pas: {filepath}")
                return False
            
            system = platform.system()
            
            if system == 'Windows':
                os.startfile(filepath)
            elif system == 'Darwin':  # macOS
                subprocess.call(['open', filepath])
            else:  # Linux et autres Unix
                subprocess.call(['xdg-open', filepath])
            
            print(f"✅ Fichier ouvert: {filepath}")
            return True
        except Exception as e:
            print(f"❌ Erreur lors de l'ouverture du fichier: {e}")
            return False
    
    @staticmethod
    def get_file_icon(extension: str) -> str:
        """
        Récupérer l'emoji icône correspondant à l'extension du fichier
        
        Args:
            extension: Extension du fichier (sans le point)
        
        Returns:
            str: Emoji représentant le type de fichier
        """
        # Dictionnaire des icônes par extension
        icons = {
            # Documents
            'pdf': '📄',
            'doc': '📝', 'docx': '📝', 'odt': '📝',
            'txt': '📃', 'rtf': '📃',
            
            # Tableurs
            'xls': '📊', 'xlsx': '📊', 'ods': '📊', 'csv': '📊',
            
            # Présentations
            'ppt': '📽️', 'pptx': '📽️', 'odp': '📽️',
            
            # Images
            'jpg': '🖼️', 'jpeg': '🖼️', 'png': '🖼️', 
            'gif': '🖼️', 'bmp': '🖼️', 'svg': '🖼️',
            'ico': '🖼️', 'webp': '🖼️',
            
            # Archives
            'zip': '🗜️', 'rar': '🗜️', '7z': '🗜️',
            'tar': '🗜️', 'gz': '🗜️', 'bz2': '🗜️',
            
            # Audio
            'mp3': '🎵', 'wav': '🎵', 'ogg': '🎵',
            'flac': '🎵', 'aac': '🎵', 'm4a': '🎵',
            
            # Vidéo
            'mp4': '🎬', 'avi': '🎬', 'mov': '🎬',
            'mkv': '🎬', 'flv': '🎬', 'wmv': '🎬',
            'webm': '🎬',
            
            # Code
            'py': '🐍', 'js': '💛', 'html': '🌐',
            'css': '🎨', 'java': '☕', 'cpp': '⚙️',
            'c': '⚙️', 'php': '🐘', 'rb': '💎',
            'go': '🔷', 'rs': '🦀', 'ts': '🔷',
            
            # Autres
            'json': '📋', 'xml': '📋', 'yaml': '📋',
            'md': '📝', 'log': '📋',
        }
        
        # Retourner l'icône correspondante ou une icône par défaut
        return icons.get(extension.lower(), '📄')
