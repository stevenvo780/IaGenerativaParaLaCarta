import torch
from rembg import remove, new_session
from PIL import Image
import numpy as np

# Configuración Multi-GPU para rembg
# Intentamos usar la GPU secundaria (cuda:1) si está disponible.
# CAMBIO: La GPU 1 (RTX 2060) está saturada (menos de 200MB libres).
# Revertimos a CPU para garantizar estabilidad.
providers = ['CPUExecutionProvider'] 

# if torch.cuda.is_available():
#     device_count = torch.cuda.device_count()
#     if device_count > 1:
#         providers = [
#             ('CUDAExecutionProvider', {
#                 'device_id': 1,
#                 'arena_extend_strategy': 'kSameAsRequested',
#             }),
#             'CPUExecutionProvider',
#         ]
#         print(f"Configurando rembg (u2netp) en GPU Secundaria (device_id: 1)")
#     else:
#         print("Solo 1 GPU detectada. Usando CPU para rembg.")

# Usamos 'u2netp' en lugar de 'u2net' por ser mucho más ligero y rápido
session = new_session("u2netp", providers=providers)

def remove_background(image: Image.Image) -> Image.Image:
    """Elimina el fondo de una imagen usando rembg (GPU Secundaria o CPU)."""
    if image is None:
        return None
    return remove(image, session=session)

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

def quantize_colors(image: Image.Image, num_colors: int = 32) -> Image.Image:
    """
    Reduce la paleta de colores de la imagen para un look más 'pixel art'.
    Usa K-Means (via PIL quantize) para encontrar los colores dominantes.
    """
    if image.mode != "RGBA":
        image = image.convert("RGBA")
        
    # Separar alfa para no cuantizarlo mal
    alpha = image.split()[3]
    rgb_image = image.convert("RGB")
    
    # Cuantizar (Fast Octree es el default de PIL y funciona bien para pixel art)
    quantized_rgb = rgb_image.quantize(colors=num_colors, method=1).convert("RGB")
    
    # Restaurar alfa
    quantized_rgb.putalpha(alpha)
    return quantized_rgb

def add_pixel_outline(image: Image.Image, color: tuple = (0, 0, 0), thickness: int = 1) -> Image.Image:
    """
    Añade un contorno de pixel art alrededor del contenido opaco.
    """
    if image.mode != "RGBA":
        image = image.convert("RGBA")
        
    # Obtener máscara de transparencia
    alpha = np.array(image.split()[3])
    
    # Crear kernel para dilatación
    # Un kernel de 3x3 con cruz central expande 1 pixel en 4 direcciones
    kernel_size = 1 + (thickness * 2)
    kernel = np.ones((kernel_size, kernel_size), dtype=np.uint8)
    
    # Binarizar alfa (>0 es contenido)
    mask = (alpha > 0).astype(np.uint8) * 255
    
    # Dilatar máscara (expandir bordes)
    # Usamos scipy.ndimage.binary_dilation o max filter manual si no queremos deps extra
    # Aquí usamos PIL filter para simplicidad y velocidad
    from PIL import ImageFilter
    
    # Método simple: Desplazar la imagen en 8 direcciones y combinar
    outline_mask = Image.new("L", image.size, 0)
    alpha_layer = image.split()[3]
    
    # Desplazamientos para grosor 1: 8 vecinos
    offsets = [(-1, -1), (0, -1), (1, -1),
               (-1,  0),          (1,  0),
               (-1,  1), (0,  1), (1,  1)]
               
    for ox, oy in offsets:
        # Desplazar canal alfa
        shifted = alpha_layer.transform(alpha_layer.size, Image.AFFINE, (1, 0, -ox, 0, 1, -oy))
        # Sumar a la máscara de borde
        outline_mask = Image.fromarray(np.maximum(np.array(outline_mask), np.array(shifted)))
    
    # El borde es: (Dilatado - Original) > 0
    # Pero queremos dibujar el borde DETRÁS de la imagen original
    
    # Crear imagen solida del color del borde
    outline_layer = Image.new("RGBA", image.size, color + (255,))
    outline_layer.putalpha(outline_mask)
    
    # Componer: Borde abajo, Imagen original arriba
    final_image = Image.alpha_composite(outline_layer, image)
    return final_image

def create_gif(frames: list, output_path: str, duration: int = 150, loop: int = 0):
    """Crea un GIF animado a partir de una lista de imágenes PIL."""
    if not frames:
        return
    
    # Asegurar que todos sean RGBA y del mismo tamaño (ya deberían serlo por crop_to_content si se procesaron igual)
    # Pero para seguridad, usamos el tamaño del primero
    base_size = frames[0].size
    processed_frames = []
    for f in frames:
        if f.size != base_size:
            f = f.resize(base_size, Image.NEAREST)
        processed_frames.append(f)
        
    processed_frames[0].save(
        output_path,
        save_all=True,
        append_images=processed_frames[1:],
        optimize=False, # False para mantener calidad pixel art
        duration=duration,
        loop=loop,
        disposal=2 # Restaurar fondo para transparencia
    )

def validate_image(image: Image.Image) -> bool:
    """
    QA Básico: Retorna False si la imagen es inválida (negra, vacía, corrupta).
    """
    if image is None: return False
    
    # Verificar si es totalmente transparente
    if image.mode == "RGBA":
        extrema = image.getextrema()
        if extrema[3][1] == 0: # Canal Alfa max es 0 (totalmente transparente)
            return False
            
    # Verificar si es totalmente negra (en canales RGB)
    # Convertir a grayscale para chequeo rápido
    gray = image.convert("L")
    extrema = gray.getextrema()
    if extrema[0] == 0 and extrema[1] == 0: # Todo negro
        return False
        
    return True

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

def crop_to_content(image: Image.Image, padding: int = 2, alpha_threshold: int = 50) -> Image.Image:
    """
    Recorta la imagen al contenido visible.
    - alpha_threshold: Valor mínimo de alpha (0-255) para considerar un pixel como 'visible'.
      Ayuda a eliminar sombras tenues o 'fantasmas' dejados por rembg.
    """
    if image is None:
        return None
    
    # Convertir a numpy para filtrado rápido
    img_np = np.array(image)
    
    # Si no tiene canal alpha, añadirlo
    if img_np.shape[2] == 3:
        return image
        
    # Crear máscara de píxeles visibles (Alpha > umbral)
    alpha_channel = img_np[:, :, 3]
    mask = alpha_channel > alpha_threshold
    
    # Si la imagen está vacía tras el filtrado
    if not np.any(mask):
        return image
        
    # Encontrar bounding box de la máscara
    rows = np.any(mask, axis=1)
    cols = np.any(mask, axis=0)
    
    ymin, ymax = np.where(rows)[0][[0, -1]]
    xmin, xmax = np.where(cols)[0][[0, -1]]
    
    # Añadir padding
    width, height = image.size
    
    left = max(0, xmin - padding)
    upper = max(0, ymin - padding)
    right = min(width, xmax + 1 + padding)
    lower = min(height, ymax + 1 + padding)
    
    return image.crop((left, upper, right, lower))
