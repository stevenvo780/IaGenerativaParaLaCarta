from PIL import Image
from rembg import remove
import numpy as np

def remove_background(image: Image.Image) -> Image.Image:
    """Elimina el fondo de una imagen usando rembg."""
    if image is None:
        return None
    return remove(image)

def pixelate(image: Image.Image, pixel_size: int = 8) -> Image.Image:
    """
    Simula efecto pixel art reduciendo y re-escalando la imagen.
    pixel_size: Tamaño del 'pixel' lógico. Cuanto mayor, más 'bloque' se ve.
    Para una imagen de 512x512, un pixel_size de 8 reduce a 64x64.
    """
    if image is None:
        return None
    
    # Calcular nuevas dimensiones
    w, h = image.size
    # Asegurar que no sea 0
    small_w = max(1, w // pixel_size)
    small_h = max(1, h // pixel_size)
    
    # Reducir usando Nearest para mantener bordes duros si ya fuera pixel art, 
    # pero para convertir arte normal, BILINEAR puede ser mejor antes del resize up.
    # Sin embargo, para 'pixelar' lo mejor es bajar resolución y subir con NEAREST.
    image_small = image.resize((small_w, small_h), resample=Image.Resampling.BILINEAR)
    
    # Escalar de vuelta al tamaño original usando NEAREST para el efecto pixelado
    return image_small.resize((w, h), resample=Image.Resampling.NEAREST)

def create_sprite_sheet(images: list[Image.Image], columns: int = 4) -> Image.Image:
    """Combina una lista de imágenes en un sprite sheet."""
    if not images:
        return None
    
    width, height = images[0].size
    
    # Calcular filas necesarias
    rows = (len(images) + columns - 1) // columns
    
    sheet_width = width * columns
    sheet_height = height * rows
    
    sprite_sheet = Image.new("RGBA", (sheet_width, sheet_height), (0, 0, 0, 0))
    
    for i, img in enumerate(images):
        if img is None: continue
        # Asegurar que todas tengan el mismo tamaño o redimensionar
        if img.size != (width, height):
            img = img.resize((width, height))
            
        x = (i % columns) * width
        y = (i // columns) * height
        sprite_sheet.paste(img, (x, y))
        
    return sprite_sheet

def crop_to_content(image: Image.Image, padding: int = 2) -> Image.Image:
    """
    Recorta la imagen al contenido visible (no transparente).
    Añade un pequeño padding alrededor.
    """
    if image is None:
        return None
    
    # Obtener bounding box del contenido no cero (alpha > 0)
    bbox = image.getbbox()
    
    if bbox:
        # Añadir padding
        left, upper, right, lower = bbox
        width, height = image.size
        
        left = max(0, left - padding)
        upper = max(0, upper - padding)
        right = min(width, right + padding)
        lower = min(height, lower + padding)
        
        return image.crop((left, upper, right, lower))
    
    return image # Si está vacía, devolver original
