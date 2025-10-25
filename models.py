from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

@dataclass
class Admin:
    """Modèle pour un administrateur"""
    id: int
    email: str
    password: str
    created_at: datetime

@dataclass
class Folder:
    """Modèle pour un dossier"""
    id: int
    name: str
    parent_id: Optional[int]
    created_at: datetime
    
    def __str__(self):
        return self.name

@dataclass
class File:
    """Modèle pour un fichier"""
    id: int
    folder_id: int
    filename: str
    filepath: str
    uploaded_at: datetime
    
    def __str__(self):
        return self.filename
    
    @property
    def extension(self) -> str:
        """Récupérer l'extension du fichier"""
        return self.filename.rsplit('.', 1)[-1].lower() if '.' in self.filename else ''
    
    @property
    def size(self) -> int:
        """Récupérer la taille du fichier en octets"""
        import os
        try:
            return os.path.getsize(self.filepath) if os.path.exists(self.filepath) else 0
        except:
            return 0
    
    @property
    def size_formatted(self) -> str:
        """Récupérer la taille du fichier formatée"""
        size = self.size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"