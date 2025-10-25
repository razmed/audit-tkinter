import os
import shutil
from typing import Optional, Tuple
from pathlib import Path

class FileHandler:
    """Gestionnaire de fichiers"""
    
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
        Importer récursivement tous les fichiers d'un dossier
        CORRECTION: Cette fonction importe maintenant TOUS les fichiers (.docx, .pdf, .xlsx, etc.)
        
        Args:
            folder_path: Chemin du dossier source à importer
            db: Instance de la base de données
            parent_folder_id: ID du dossier parent dans la DB (None pour racine)
        
        Returns:
            int: Nombre de fichiers importés
        """
        count = 0
        folder_name = os.path.basename(folder_path)
        
        print(f"\n📂 Importation du dossier: {folder_name}")
        print(f"   Chemin source: {folder_path}")
        print(f"   Parent ID: {parent_folder_id}")
        
        # Créer le dossier dans la base de données
        folder_id = db.create_folder(folder_name, parent_folder_id)
        print(f"   ✅ Dossier créé dans la DB avec ID: {folder_id}")
        
        try:
            # Lister tous les éléments du dossier
            items = os.listdir(folder_path)
            print(f"   📋 {len(items)} élément(s) trouvé(s)")
            
            for item in items:
                item_path = os.path.join(folder_path, item)
                
                if os.path.isfile(item_path):
                    # C'est un fichier - L'IMPORTER
                    print(f"      📄 Fichier détecté: {item}")
                    
                    # Vérifier l'extension
                    extension = item.rsplit('.', 1)[-1].lower() if '.' in item else ''
                    
                    # Liste des extensions supportées (ajouter selon besoin)
                    supported_extensions = [
                        'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
                        'txt', 'csv', 'jpg', 'jpeg', 'png', 'gif', 'bmp',
                        'zip', 'rar', '7z', 'mp3', 'mp4', 'avi', 'mov'
                    ]
                    
                    # Copier le fichier dans uploads/
                    success, dest_path = self.save_file(item_path, item)
                    
                    if success:
                        # Ajouter à la base de données
                        try:
                            file_id = db.add_file(folder_id, item, dest_path)
                            count += 1
                            print(f"         ✅ Fichier ajouté à la DB (ID: {file_id})")
                        except Exception as db_error:
                            print(f"         ❌ Erreur DB pour {item}: {db_error}")
                    else:
                        print(f"         ❌ Échec de la copie de {item}")
                
                elif os.path.isdir(item_path):
                    # C'est un sous-dossier - APPEL RÉCURSIF
                    print(f"      📁 Sous-dossier détecté: {item}")
                    subfolder_count = self.save_files_from_folder(item_path, db, folder_id)
                    count += subfolder_count
                    print(f"      ✅ {subfolder_count} fichier(s) importé(s) depuis {item}")
        
        except Exception as e:
            print(f"❌ Erreur lors de l'importation du dossier {folder_path}: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"📂 Fin importation de {folder_name}: {count} fichier(s) total\n")
        return count
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Nettoyer un nom de fichier"""
        import re
        # Remplacer les caractères non autorisés
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Limiter la longueur
        if len(filename) > 200:
            name, ext = os.path.splitext(filename)
            filename = name[:200-len(ext)] + ext
        return filename
    
    @staticmethod
    def open_file(filepath: str) -> bool:
        """Ouvrir un fichier avec l'application par défaut"""
        try:
            import platform
            import subprocess
            
            if not os.path.exists(filepath):
                print(f"❌ Le fichier n'existe pas: {filepath}")
                return False
            
            if platform.system() == 'Windows':
                os.startfile(filepath)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', filepath])
            else:  # Linux
                subprocess.call(['xdg-open', filepath])
            
            print(f"✅ Fichier ouvert: {filepath}")
            return True
        except Exception as e:
            print(f"❌ Erreur lors de l'ouverture du fichier: {e}")
            return False
    
    @staticmethod
    def get_file_icon(extension: str) -> str:
        """Récupérer l'icône correspondant à l'extension"""
        icons = {
            'pdf': '📄',
            'doc': '📝', 'docx': '📝',
            'xls': '📊', 'xlsx': '📊',
            'ppt': '📽️', 'pptx': '📽️',
            'jpg': '🖼️', 'jpeg': '🖼️', 'png': '🖼️', 'gif': '🖼️', 'bmp': '🖼️',
            'zip': '🗜️', 'rar': '🗜️', '7z': '🗜️',
            'txt': '📃', 'csv': '📃',
            'mp3': '🎵', 'wav': '🎵',
            'mp4': '🎬', 'avi': '🎬', 'mov': '🎬',
        }
        return icons.get(extension.lower(), '📄')