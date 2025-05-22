import os
from werkzeug.utils import secure_filename
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

class FileStorage:
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.upload_folder = app.config['UPLOAD_FOLDER']
        self.max_content_length = app.config['MAX_CONTENT_LENGTH']
        
        # Créer les dossiers nécessaires
        for folder in ['logos', 'profiles', 'candidates']:
            os.makedirs(os.path.join(self.upload_folder, folder), exist_ok=True)

    def save_file(self, file, folder):
        """Sauvegarde un fichier dans le dossier spécifié"""
        try:
            if not file or not self._allowed_file(file.filename):
                raise ValueError('Type de fichier non autorisé')

            # Générer un nom de fichier unique
            filename = secure_filename(file.filename)
            unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}_{filename}"
            
            # Chemin complet du fichier
            file_path = os.path.join(self.upload_folder, folder, unique_filename)
            
            # Sauvegarder le fichier
            file.save(file_path)
            
            # Retourner le chemin relatif
            return os.path.join('uploads', folder, unique_filename)

        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du fichier: {str(e)}")
            raise

    def delete_file(self, file_path):
        """Supprime un fichier"""
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du fichier: {str(e)}")
            return False

    def _allowed_file(self, filename):
        """Vérifie si le type de fichier est autorisé"""
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS 