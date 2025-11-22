"""
Post-Procesado Agresivo para Pixel Art Auténtico
Convierte imágenes suaves en sprites pixelados reales
"""
from PIL import Image
import numpy as np

def pixelate_aggressive(
    image: Image.Image,
    target_pixel_size: int = 64,
    final_size: int = 256,
    palette_size: int = 16,
    dither: bool = False
) -> Image.Image:
    """
    Post-procesado AGRESIVO para look pixel art auténtico.
    
    Pipeline:
    1. Downscale drástico (fuerza pixelado)
    2. Reducción de paleta (look retro)
    3. Upscale sin suavizado (píxeles nítidos)
    
    Args:
        target_pixel_size: Tamaño intermedio (64=muy pixelado, 128=moderado)
        final_size: Tamaño final de salida
        palette_size: Número de colores (16=NES, 4=Gameboy, 32=SNES)
        dither: Aplicar dithering (False para píxeles sólidos)
    """
    if image.mode != "RGBA":
        image = image.convert("RGBA")
    
    # Separar alpha
    alpha = image.split()[3]
    rgb = image.convert("RGB")
    
    # 1. DOWNSCALE DRÁSTICO (fuerza el pixelado)
    small = rgb.resize((target_pixel_size, target_pixel_size), Image.NEAREST)
    small_alpha = alpha.resize((target_pixel_size, target_pixel_size), Image.NEAREST)
    
    # 2. REDUCCIÓN DE PALETA (look retro)
    dither_method = Image.FLOYDSTEINBERG if dither else Image.NONE
    quantized = small.quantize(colors=palette_size, method=2, dither=dither_method)
    quantized_rgb = quantized.convert("RGB")
    
    # 3. UPSCALE SIN SUAVIZADO (píxeles nítidos)
    pixelated = quantized_rgb.resize((final_size, final_size), Image.NEAREST)
    pixelated_alpha = small_alpha.resize((final_size, final_size), Image.NEAREST)
    
    # Recombinar con alpha
    pixelated = pixelated.convert("RGBA")
    pixelated.putalpha(pixelated_alpha)
    
    return pixelated

def apply_retro_palette(image: Image.Image, palette_name: str = "NES") -> Image.Image:
    """
    Aplica paletas de consolas retro específicas.
    
    Paletas:
    - NES: 64 colores
    - Gameboy: 4 tonos de verde
    - SNES: 256 colores
    - Genesis: 64 colores
    """
    PALETTE_SIZES = {
        "NES": 64,
        "Gameboy": 4,
        "GameboyColor": 32,
        "SNES": 256,
        "Genesis": 64,
        "CGA": 16,
        "EGA": 64
    }
    
    palette_size = PALETTE_SIZES.get(palette_name, 16)
    
    if image.mode != "RGBA":
        image = image.convert("RGBA")
    
    alpha = image.split()[3]
    rgb = image.convert("RGB")
    
    # Quantizar con paleta específica
    quantized = rgb.quantize(colors=palette_size, method=2, dither=Image.NONE)
    
    # Para Gameboy, forzar tonos de verde
    if "Gameboy" in palette_name:
        # Convertir a escala de grises primero
        gray = quantized.convert("L")
        # Mapear a tonos de verde
        palette_data = []
        green_shades = [
            (15, 56, 15),      # Más oscuro
            (48, 98, 48),      # Oscuro
            (139, 172, 15),    # Claro
            (155, 188, 15)     # Más claro
        ]
        for shade in green_shades:
            palette_data.extend(shade)
        # Rellenar resto con negro
        palette_data.extend([0, 0, 0] * (256 - len(green_shades)))
        
        # Aplicar paleta
        quantized.putpalette(palette_data)
    
    result = quantized.convert("RGBA")
    result.putalpha(alpha)
    
    return result

def remove_background_pixel_safe(image: Image.Image) -> Image.Image:
    """
    Eliminación de fondo que preserva los píxeles.
    Elimina SOLO blanco puro (255, 255, 255) - nada más.
    
    ULTRA CONSERVADOR: Solo blanco 100% puro se hace transparente.
    Cualquier tono gris claro, beige, etc. se preserva.
    """
    if image.mode != "RGBA":
        image = image.convert("RGBA")
    
    # Convertir a numpy
    img_array = np.array(image)
    
    # SOLO BLANCO PURO (255, 255, 255)
    # NO threshold - comparación exacta
    is_pure_white = (img_array[:, :, 0] == 255) & \
                    (img_array[:, :, 1] == 255) & \
                    (img_array[:, :, 2] == 255)
    
    # Hacer transparente SOLO el blanco puro
    img_array[is_pure_white, 3] = 0
    
    return Image.fromarray(img_array)
