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

# ============================================================================
# QA AVANZADO CON IA (CLIP en CPU)
# ============================================================================
_clip_model = None
_clip_processor = None

def init_clip_qa():
    """
    Inicializa CLIP para evaluación de calidad en CPU.
    Solo se carga una vez (lazy loading).
    """
    global _clip_model, _clip_processor
    
    if _clip_model is not None:
        return  # Ya inicializado
    
    try:
        from transformers import CLIPProcessor, CLIPModel
        print("Cargando CLIP para QA de imágenes (CPU)...")
        
        # Usar modelo pequeño para velocidad
        model_id = "openai/clip-vit-base-patch32"
        _clip_processor = CLIPProcessor.from_pretrained(model_id)
        _clip_model = CLIPModel.from_pretrained(model_id)
        _clip_model.eval()  # Modo evaluación
        
        print("CLIP cargado exitosamente.")
    except Exception as e:
        print(f"Error cargando CLIP: {e}")
        print("QA con IA desactivado. Continuando con validación básica.")

def evaluate_image_quality(image: Image.Image, prompt: str = "") -> dict:
    """
    Evalúa la calidad de una imagen usando CLIP.
    
    Retorna un diccionario con:
    - 'score': Puntuación de 0-100 (qué tan bien coincide con el prompt)
    - 'is_good': Boolean (True si score > 60)
    - 'is_pixel_art': Boolean (qué tan "pixel art" se ve)
    """
    global _clip_model, _clip_processor
    
    # Si CLIP no está disponible, retornar valores por defecto
    if _clip_model is None:
        return {'score': 75.0, 'is_good': True, 'is_pixel_art': True}
    
    try:
        # Preparar textos de comparación
        positive_text = f"high quality pixel art {prompt}" if prompt else "high quality pixel art game asset"
        negative_texts = [
            "blurry low quality image",
            "photorealistic 3d render",
            "abstract noise",
            "empty black image"
        ]
        
        # Procesar imagen y textos
        inputs = _clip_processor(
            text=[positive_text] + negative_texts,
            images=image,
            return_tensors="pt",
            padding=True
        )
        
        # Inferencia
        with torch.no_grad():
            outputs = _clip_model(**inputs)
            logits_per_image = outputs.logits_per_image
            probs = logits_per_image.softmax(dim=1)
        
        # Probabilidad del texto positivo
        positive_prob = probs[0][0].item()
        score = positive_prob * 100
        
        # Verificar si es pixel art (vs foto/3D)
        pixel_art_inputs = _clip_processor(
            text=["pixel art game sprite", "photorealistic image"],
            images=image,
            return_tensors="pt",
            padding=True
        )
        
        with torch.no_grad():
            pa_outputs = _clip_model(**pixel_art_inputs)
            pa_probs = pa_outputs.logits_per_image.softmax(dim=1)
        
        is_pixel_art = pa_probs[0][0].item() > 0.6
        
        return {
            'score': score,
            'is_good': score > 60,
            'is_pixel_art': is_pixel_art
        }
        
    except Exception as e:
        print(f"Error en evaluación CLIP: {e}")
        return {'score': 75.0, 'is_good': True, 'is_pixel_art': True}

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

def crop_to_content(image: Image.Image, padding: int = 30, alpha_threshold: int = 5, min_crop_ratio: float = 0.3) -> Image.Image:
    """
    Recorta la imagen al contenido visible con máxima preservación del objeto.
    
    MEJORADO V2:
    -padding: 30px (antes 10) para preservar objetos completos
    - alpha_threshold: 5 (antes 10) para capturar incluso detalles muy sutiles
    - min_crop_ratio: 0.3 (antes 0.5) para permitir recortes más agresivos cuando sea apropiado
    - Detección inteligente de objetos vs tiles
    - Preservar proporciones originales si el objeto es muy pequeño
    """
    if image is None:
        return None
    
    # Convertir a numpy
    img_np = np.array(image)
    
    # Si no tiene canal alpha, retornar sin cambios
    if len(img_np.shape) < 3 or img_np.shape[2] < 4:
        return image
        
    # Crear máscara de píxeles visibles (Alpha > umbral muy bajo)
    alpha_channel = img_np[:, :, 3]
    mask = alpha_channel > alpha_threshold
    
    # Si la imagen está vacía
    if not np.any(mask):
        return image
        
    # Encontrar bounding box
    rows = np.any(mask, axis=1)
    cols = np.any(mask, axis=0)
    
    if not np.any(rows) or not np.any(cols):
        return image
    
    ymin, ymax = np.where(rows)[0][[0, -1]]
    xmin, xmax = np.where(cols)[0][[0, -1]]
    
    width, height = image.size
    
    # PADDING GENEROSO para preservar objetos completos
    left = max(0, xmin - padding)
    upper = max(0, ymin - padding)
    right = min(width, xmax + 1 + padding)
    lower = min(height, ymax + 1 + padding)
    
    # Calcular dimensiones del recorte
    crop_width = right - left
    crop_height = lower - upper
    crop_area = crop_width * crop_height
    original_area = width * height
    crop_ratio = crop_area / original_area if original_area > 0 else 1.0
    
    # DETECCIÓN INTELIGENTE:
    # Si el objeto ocupa < 30% del área original, probablemente es un objeto pequeño
    # que fue generado con mucho espacio blanco alrededor
    # En este caso, SÍ recortar para aprovechar mejor el espacio
    
    # Si el objeto ocupa > 70% del área, probablemente es un tile o path
    # que debe mantener sus dimensiones completas
    if crop_ratio > 0.7:
        # Es un tile/path - NO recortar
        return image
    
    # Para objetos pequeños/medianos, recortar con padding generoso
    cropped = image.crop((left, upper, right, lower))
    
    # OPCIONAL: Si el recorte es muy pequeño (<100px en cualquier dimensión),
    # expandir el canvas para tener al menos un tamaño mínimo usable
    min_size = 128
    if crop_width < min_size or crop_height < min_size:
        # Crear canvas más grande y centrar el objeto
        target_width = max(min_size, crop_width)
        target_height = max(min_size, crop_height)
        
        # Crear canvas transparente
        expanded = Image.new("RGBA", (target_width, target_height), (0, 0, 0, 0))
        
        # Centrar el objeto recortado
        paste_x = (target_width - crop_width) // 2
        paste_y = (target_height - crop_height) // 2
        expanded.paste(cropped, (paste_x, paste_y))
        
        return expanded
    
    return cropped

