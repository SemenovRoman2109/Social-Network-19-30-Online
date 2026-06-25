from django.core.files.base import ContentFile
from PIL import Image
from io import BytesIO

MAX_COMPRESSED_IMAGE_SIZE = 5 * 1024 * 1024 # 5 Mb

def _compressed_image(image):
        '''
            повна робота з модулем Pillow
        '''
        
        image.seek(0)
        compressed_image = Image.open(image)
        compressed_image = compressed_image.convert("RGB")
        
        quality = 85
        width, height = compressed_image.size
        
        while True:
            buffer = BytesIO()
            compressed_image.save(fp= buffer, format= 'JPEG', quality= quality, optimize= True)
            
            if buffer.tell() <= MAX_COMPRESSED_IMAGE_SIZE:
                break
            
            if quality > 35:
                quality -= 10
            else:
                if width <= 1 or height <= 1:
                    break
                # Якщо якість вже низька, зменшуємо зображення на 10%
                width = int(width * 0.9)
                height = int(height * 0.9)
                compressed_image = compressed_image.resize((width, height), Image.Resampling.LANCZOS)
                
        image.seek(0)
        
        compressed_name = f'compressed_{image.name.rsplit(".", 1)[0]}.jpg'
        
        return ContentFile(buffer.getvalue(), name= compressed_name)
        
        
        