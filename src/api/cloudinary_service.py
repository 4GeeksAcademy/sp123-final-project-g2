import cloudinary
import cloudinary.uploader
import os
import re
from flask import current_app
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()

class CloudinaryService:
    """Servicio para manejar uploads a Cloudinary específico para LSE"""
    
    # Configuración para lenguaje de señas
    ALLOWED_CONFIG = {
        'video': {
            'extensions': ['mp4', 'mov', 'avi', 'webm', 'mkv'],
            'max_size_mb': 100,
            'resource_type': 'video',
            'transformations': {'quality': 'auto', 'fetch_format': 'auto'}
        },
        'image': {
            'extensions': ['jpg', 'jpeg', 'png'],
            'max_size_mb': 10,
            'resource_type': 'image',
            'transformations': {'quality': 'auto'}
        },
        'gif': {
            'extensions': ['gif'],
            'max_size_mb': 20,
            'resource_type': 'image',
            'transformations': {}
        },
        'animation': {
            'extensions': ['gif', 'webp'],
            'max_size_mb': 20,
            'resource_type': 'image',
            'transformations': {}
        },
        'document': {
            'extensions': ['pdf', 'docx', 'txt', 'pptx'],
            'max_size_mb': 50,
            'resource_type': 'raw',
            'transformations': {}
        }
    }
    
    def __init__(self):
        self._configure()
    
    def _configure(self):
        """Configurar Cloudinary con variables de entorno"""
        cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
        api_key = os.getenv('CLOUDINARY_API_KEY')
        api_secret = os.getenv('CLOUDINARY_API_SECRET')
        
        if not all([cloud_name, api_key, api_secret]):
            raise ValueError("Faltan credenciales de Cloudinary en .env")
        
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True
        )
        
        self.upload_folder = os.getenv('CLOUDINARY_UPLOAD_FOLDER', 'lse_lessons')
    
    def validate_file(self, file, resource_type):
        """Validar archivo antes de subir"""
        if not file or not hasattr(file, 'filename') or not file.filename:
            raise ValueError("Archivo inválido o vacío")
        
        filename = secure_filename(file.filename)
        
        # Verificar extensión
        if '.' not in filename:
            raise ValueError("Archivo sin extensión")
        
        ext = filename.rsplit('.', 1)[1].lower()
        
        # Verificar tipo permitido
        config = self.ALLOWED_CONFIG.get(resource_type)
        if not config:
            allowed = ', '.join(self.ALLOWED_CONFIG.keys())
            raise ValueError(f"Tipo '{resource_type}' no permitido. Permitidos: {allowed}")
        
        # Verificar extensión
        if ext not in config['extensions']:
            raise ValueError(
                f"Extensión .{ext} no permitida para {resource_type}. "
                f"Permitidas: {', '.join(config['extensions'])}"
            )
        
        # Verificar tamaño
        file.seek(0, 2)
        file_size_mb = file.tell() / (1024 * 1024)
        file.seek(0)
        
        if file_size_mb > config['max_size_mb']:
            raise ValueError(
                f"Archivo muy grande ({file_size_mb:.1f}MB). "
                f"Máximo: {config['max_size_mb']}MB"
            )
        
        return True
    
    def upload_file(self, file, resource_type, user_id, lesson_id, description=""):
        """Subir archivo a Cloudinary"""
        # Validar primero
        self.validate_file(file, resource_type)
        
        config = self.ALLOWED_CONFIG[resource_type]
        
        # Crear nombre seguro
        original_name = secure_filename(file.filename)
        name_without_ext = original_name.rsplit('.', 1)[0]
        safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', name_without_ext)
        
        # Public ID único
        public_id = f"{self.upload_folder}/user_{user_id}/lesson_{lesson_id}/{safe_name}"
        
        # Parámetros de upload
        upload_params = {
            'public_id': public_id,
            'resource_type': config['resource_type'],
            'folder': f"{self.upload_folder}/user_{user_id}/lesson_{lesson_id}",
            'use_filename': True,
            'unique_filename': True,
            'overwrite': False,
        }
        
        # Contexto para descripción
        if description:
            upload_params['context'] = f"description={description}"
        
        # Transformaciones
        if config.get('transformations'):
            upload_params.update(config['transformations'])
        
        try:
            result = cloudinary.uploader.upload(file, **upload_params)
            
            return {
                'url': result['secure_url'],
                'public_id': result['public_id'],
                'format': result.get('format'),
                'bytes': result.get('bytes'),
                'duration': result.get('duration'),
                'width': result.get('width'),
                'height': result.get('height'),
                'resource_type': result['resource_type'],
                'original_filename': original_name
            }
            
        except cloudinary.exceptions.Error as e:
            raise Exception(f"Error Cloudinary: {str(e)}")
        except Exception as e:
            raise Exception(f"Error subiendo archivo: {str(e)}")
    
    def delete_file(self, public_id, resource_type='image'):
        """Eliminar archivo de Cloudinary"""
        try:
            result = cloudinary.uploader.destroy(public_id, resource_type=resource_type)
            return result.get('result') == 'ok'
        except Exception as e:
            current_app.logger.error(f"Error eliminando Cloudinary: {str(e)}")
            return False

# Instancia global para importar
cloudinary_service = CloudinaryService()