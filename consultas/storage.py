from cloudinary_storage.storage import RawMediaCloudinaryStorage, MediaCloudinaryStorage

class SmartCloudinaryStorage(RawMediaCloudinaryStorage):
    """Storage que determina automáticamente si usar image o raw"""
    
    def _get_resource_type(self, name):
        """Determina el tipo de recurso basado en la extensión"""
        if name:
            extension = name.lower().split('.')[-1]
            # Extensiones de imagen usan 'image'
            if extension in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'bmp']:
                return 'image'
            # Todo lo demás usa 'raw' (PDFs, Word, Excel, etc.)
        return 'raw'
    
    def _save(self, name, content):
        """Override para establecer el resource_type correcto"""
        resource_type = self._get_resource_type(name)
        
        # Guardar el resource_type en las opciones
        if not hasattr(self, 'RESOURCE_TYPE'):
            self.RESOURCE_TYPE = resource_type
            
        return super()._save(name, content)