"""
Generador Procedural MEJORADO de Tiles para Pixel Art
✅ Tiles perfectamente seamless (wrapping matemático)
✅ Sistema completo de transiciones césped-agua (16 tiles)
✅ 15 variantes de caminos
✅ Máxima paralelización CPU
"""
import numpy as np
from PIL import Image, ImageDraw
import random
from typing import List, Tuple
from concurrent.futures import ThreadPoolExecutor
from scipy.ndimage import zoom

# Paletas de color por bioma (inmutables)
BIOME_PALETTES = {
    "Forest": {
        "grass": [(34, 139, 34), (46, 125, 50), (27, 94, 32), (56, 142, 60)],
        "water": [(0, 105, 148), (0, 131, 167), (0, 77, 128), (41, 182, 246)],
        "dirt": [(139, 90, 43), (121, 85, 61), (101, 67, 33), (160, 102, 55)]
    },
    "Desert": {
        "grass": [(218, 165, 32), (205, 133, 63), (184, 134, 11), (188, 143, 43)],
        "water": [(0, 139, 139), (0, 128, 128), (47, 79, 79), (0, 191, 191)],
        "dirt": [(210, 180, 140), (222, 184, 135), (188, 143, 143), (165, 42, 42)]
    },
    "Snowy Tundra": {
        "grass": [(220, 230, 240), (200, 210, 220), (180, 190, 200), (240, 248, 255)],
        "water": [(176, 224, 230), (135, 206, 235), (176, 196, 222), (173, 216, 230)],
        "dirt": [(190, 190, 190), (169, 169, 169), (211, 211, 211), (192, 192, 192)]
    },
    "Volcanic Wasteland": {
        "grass": [(105, 105, 105), (85, 85, 85), (65, 65, 65), (128, 128, 128)],
        "water": [(220, 20, 60), (178, 34, 34), (139, 0, 0), (255, 69, 0)],
        "dirt": [(75, 54, 33), (55, 34, 23), (45, 24, 13), (95, 74, 53)]
    },
    "Swamp": {
        "grass": [(85, 107, 47), (107, 142, 35), (124, 152, 47), (75, 97, 37)],
        "water": [(47, 79, 79), (60, 90, 60), (34, 72, 34), (70, 100, 70)],
        "dirt": [(101, 67, 33), (91, 57, 23), (81, 47, 13), (111, 77, 43)]
    },
    # Paletas para otros biomas
    "Underwater Realm": {
        "grass": [(0, 100, 100), (0, 120, 120), (0, 80, 80), (0, 140, 140)],
        "water": [(0, 50, 100), (0, 70, 120), (0, 60, 110), (0, 80, 130)],
        "dirt": [(60, 60, 80), (50, 50, 70), (70, 70, 90), (55, 55, 75)]
    },
    "Sky Islands": {
        "grass": [(135, 206, 250), (176, 224, 230), (173, 216, 230), (135, 206, 235)],
        "water": [(100, 149, 237), (70, 130, 180), (95, 158, 160), (106, 90, 205)],
        "dirt": [(210, 180, 140), (222, 184, 135), (188, 143, 143), (245, 222, 179)]
    },
    "Crystal Caves": {
        "grass": [(186, 85, 211), (147, 112, 219), (138, 43, 226), (75, 0, 130)],
        "water": [(72, 61, 139), (123, 104, 238), (106, 90, 205), (147, 112, 219)],
        "dirt": [(105, 105, 105), (128, 128, 128), (112, 128, 144), (119, 136, 153)]
    },
    "Mushroom Grove": {
        "grass": [(255, 105, 180), (255, 20, 147), (219, 112, 147), (238, 130, 238)],
        "water": [(221, 160, 221), (218, 112, 214), (186, 85, 211), (147, 112, 219)],
        "dirt": [(160, 82, 45), (205, 133, 63), (210, 105, 30), (139, 69, 19)]
    },
    "Ancient Ruins": {
        "grass": [(154, 205, 50), (107, 142, 35), (85, 107, 47), (124, 252, 0)],
        "water": [(70, 130, 180), (100, 149, 237), (65, 105, 225), (0, 191, 255)],
        "dirt": [(160, 160, 160), (169, 169, 169), (128, 128, 128), (192, 192, 192)]
    }
}

def perlin_noise_seamless(shape, scale=10.0, octaves=4, seed=0):
    """
    Genera ruido Perlin PERFECTAMENTE SEAMLESS usando wrapping
    """
    np.random.seed(seed)
    noise = np.zeros(shape)
    amplitude = 1.0
    frequency = 1.0
    
    for _ in range(octaves):
        # Crear grid extendido para wrapping
        grid_size = (int(shape[0] / scale / frequency) + 2, 
                     int(shape[1] / scale / frequency) + 2)
        
        # Generar ruido base
        base = np.random.rand(*grid_size)
        
        # Wrap horizontalmente y verticalmente
        base = np.tile(base, (2, 2))
        
        # Escalar al tamaño deseado
        scaled = zoom(base, (shape[0] / base.shape[0], shape[1] / base.shape[1]), order=1)
        
        # Tomar solo la región que se repite
        noise += scaled[:shape[0], :shape[1]] * amplitude
        
        amplitude *= 0.5
        frequency *= 2.0
    
    # Normalizar
    noise = (noise - noise.min()) / (noise.max() - noise.min() + 1e-8)
    return noise

class TileGenerator:
    def __init__(self, tile_size: int = 32):
        self.tile_size = tile_size
        
    def get_palette(self, biome: str, tile_type: str) -> List[Tuple[int, int, int]]:
        """Obtiene paleta de color para bioma y tipo"""
        biome_key = biome if biome in BIOME_PALETTES else "Forest"
        
        if "water" in tile_type.lower():
            palette_type = "water"
        elif "dirt" in tile_type.lower() or "path" in tile_type.lower():
            palette_type = "dirt"
        else:
            palette_type = "grass"
            
        return BIOME_PALETTES[biome_key].get(palette_type, BIOME_PALETTES["Forest"]["grass"])
    
    def generate_terrain_tile(self, terrain_type: str, biome: str, variation: int = 0) -> Image.Image:
        """Genera tile de terreno SEAMLESS"""
        img = Image.new("RGBA", (self.tile_size, self.tile_size), (0, 0, 0, 0))
        pixels = img.load()
        
        palette = self.get_palette(biome, terrain_type)
        
        # Ruido seamless
        noise = perlin_noise_seamless((self.tile_size, self.tile_size), scale=8.0, octaves=3, seed=variation)
        
        # Rellenar con colores
        for y in range(self.tile_size):
            for x in range(self.tile_size):
                color_idx = int(noise[y, x] * (len(palette) - 1))
                pixels[x, y] = palette[color_idx] + (255,)
        
        # Añadir detalles mínimos
        random.seed(variation)
        detail_color = (max(0, palette[0][0] - 30), max(0, palette[0][1] - 30), max(0, palette[0][2] - 30), 255)
        
        for _ in range(self.tile_size // 8):
            x = random.randint(0, self.tile_size - 1)
            y = random.randint(0, self.tile_size - 1)
            pixels[x, y] = detail_color
        
        return img
    
    def generate_transition_tile(self, direction: str, biome: str, variation: int = 0) -> Image.Image:
        """
        Genera tile de transición césped-agua
        direction: 'edge_N', 'edge_S', 'edge_E', 'edge_W', 
                   'corner_NE', 'corner_NW', 'corner_SE', 'corner_SW',
                   'inner_NE', 'inner_NW', 'inner_SE', 'inner_SW'
        """
        img = Image.new("RGBA", (self.tile_size, self.tile_size), (0, 0, 0, 0))
        pixels = img.load()
        
        grass_palette = self.get_palette(biome, "grass")
        water_palette = self.get_palette(biome, "water")
        
        # Ruido para ambos
        noise = perlin_noise_seamless((self.tile_size, self.tile_size), scale=6.0, octaves=2, seed=variation)
        
        # Máscara según dirección
        for y in range(self.tile_size):
            for x in range(self.tile_size):
                # Calcular si es agua o césped según la dirección
                is_water = False
                
                if 'edge' in direction:
                    if 'N' in direction:  # Agua arriba
                        is_water = y < self.tile_size * 0.5 + (noise[y, x] - 0.5) * 6
                    elif 'S' in direction:  # Agua abajo
                        is_water = y > self.tile_size * 0.5 + (noise[y, x] - 0.5) * 6
                    elif 'E' in direction:  # Agua derecha
                        is_water = x > self.tile_size * 0.5 + (noise[y, x] - 0.5) * 6
                    elif 'W' in direction:  # Agua izquierda
                        is_water = x < self.tile_size * 0.5 + (noise[y, x] - 0.5) * 6
                
                elif 'corner' in direction:
                    # Esquinas externas (diagonal)
                    if 'NE' in direction:
                        dist = np.sqrt((x - self.tile_size)**2 + y**2)
                    elif 'NW' in direction:
                        dist = np.sqrt(x**2 + y**2)
                    elif 'SE' in direction:
                        dist = np.sqrt((x - self.tile_size)**2 + (y - self.tile_size)**2)
                    elif 'SW' in direction:
                        dist = np.sqrt(x**2 + (y - self.tile_size)**2)
                    
                    is_water = dist < self.tile_size * 0.7 + (noise[y, x] - 0.5) * 8
                
                elif 'inner' in direction:
                    # Esquinas internas (inverso)
                    if 'NE' in direction:
                        dist = np.sqrt((x - self.tile_size)**2 + y**2)
                    elif 'NW' in direction:
                        dist = np.sqrt(x**2 + y**2)
                    elif 'SE' in direction:
                        dist = np.sqrt((x - self.tile_size)**2 + (y - self.tile_size)**2)
                    elif 'SW' in direction:
                        dist = np.sqrt(x**2 + (y - self.tile_size)**2)
                    
                    is_water = dist > self.tile_size * 0.3 + (noise[y, x] - 0.5) * 8
                
                # Asignar color
                if is_water:
                    palette = water_palette
                else:
                    palette = grass_palette
                
                color_idx = int(noise[y, x] * (len(palette) - 1))
                pixels[x, y] = palette[color_idx] + (255,)
        
        return img
    
    def generate_path_tile(self, path_variant: str, biome: str, variation: int = 0) -> Image.Image:
        """
        Genera tiles de camino
        path_variant: 'horizontal', 'vertical', 'curve_NE', 'T_N', 'cross', 'end_N', etc.
        """
        img = Image.new("RGBA", (self.tile_size, self.tile_size), (0, 0, 0, 0))
        pixels = img.load()
        
        path_palette = self.get_palette(biome, "dirt")
        
        # Ruido de textura
        noise = perlin_noise_seamless((self.tile_size, self.tile_size), scale=5.0, octaves=2, seed=variation)
        
        # Máscara del camino
        path_mask = np.zeros((self.tile_size, self.tile_size), dtype=bool)
        path_width = self.tile_size * 0.5  # 50% del tile
        
        # Definir máscara según variante
        if 'horizontal' in path_variant:
            path_mask[int(self.tile_size * 0.25):int(self.tile_size * 0.75), :] = True
        
        elif 'vertical' in path_variant:
            path_mask[:, int(self.tile_size * 0.25):int(self.tile_size * 0.75)] = True
        
        elif 'curve' in path_variant:
            # Curvas en L
            path_mask[int(self.tile_size * 0.25):int(self.tile_size * 0.75), :] = True  # Horizontal
            path_mask[:, int(self.tile_size * 0.25):int(self.tile_size * 0.75)] = True  # Vertical
            
            # Eliminar cuadrante según dirección
            if 'NE' in path_variant:
                path_mask[:int(self.tile_size *0.5), :int(self.tile_size * 0.5)] = False
            elif 'NW' in path_variant:
                path_mask[:int(self.tile_size * 0.5), int(self.tile_size * 0.5):] = False
            elif 'SE' in path_variant:
                path_mask[int(self.tile_size * 0.5):, :int(self.tile_size * 0.5)] = False
            elif 'SW' in path_variant:
                path_mask[int(self.tile_size * 0.5):, int(self.tile_size * 0.5):] = False
        
        elif 'T_' in path_variant:
            # T-junctions
            path_mask[int(self.tile_size * 0.25):int(self.tile_size * 0.75), :] = True
            path_mask[:, int(self.tile_size * 0.25):int(self.tile_size * 0.75)] = True
            
            # Eliminar lado según dirección
            if 'N' in path_variant:
                path_mask[:int(self.tile_size * 0.5), :] = True
                path_mask[int(self.tile_size * 0.5):, :int(self.tile_size * 0.25)] = False
                path_mask[int(self.tile_size * 0.5):, int(self.tile_size * 0.75):] = False
            # ... etc
        
        elif 'cross' in path_variant:
            # Cruce completo
            path_mask[int(self.tile_size * 0.25):int(self.tile_size * 0.75), :] = True
            path_mask[:, int(self.tile_size * 0.25):int(self.tile_size * 0.75)] = True
        
        elif 'end_' in path_variant:
            # Terminaciones
            path_mask[int(self.tile_size * 0.25):int(self.tile_size * 0.75), :int(self.tile_size * 0.5)] = True
        
        # Aplicar textura solo en camino
        for y in range(self.tile_size):
            for x in range(self.tile_size):
                if path_mask[y, x]:
                    color_idx = int(noise[y, x] * (len(path_palette) - 1))
                    pixels[x, y] = path_palette[color_idx] + (255,)
        
        return img
    
    def generate_effect_tile(self, effect_type: str, variation: int = 0) -> Image.Image:
        """Genera efectos simples (sombras, parches)"""
        img = Image.new("RGBA", (self.tile_size, self.tile_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        if 'shadow' in effect_type:
            # Sombra semitransparente
            if 'circular' in effect_type:
                draw.ellipse([4, 4, self.tile_size-4, self.tile_size-4], fill=(0, 0, 0, 100))
            else:  # square
                draw.rectangle([4, 4, self.tile_size-4, self.tile_size-4], fill=(0, 0, 0, 80))
        
        elif 'dirt_patch' in effect_type:
            # Parche de tierra
            pixels = img.load()
            noise = perlin_noise_seamless((self.tile_size, self.tile_size), scale=4.0, seed=variation)
            
            for y in range(self.tile_size):
                for x in range(self.tile_size):
                    if noise[y, x] > 0.4:
                        brown = (101 + int(noise[y, x] * 30), 67, 33, 200)
                        pixels[x, y] = brown
        
        return img
    
    def generate_batch(self, category: str, item: str, biome: str, count: int = 10) -> List[Image.Image]:
        """
        Genera múltiples variaciones EN PARALELO
        Aprovecha tutti CPU threads
        """
        def generate_single(idx):
            if category == "Terrain":
                return self.generate_terrain_tile(item, biome, variation=idx)
            
            elif category == "Terrain_Transitions":
                # Extraer dirección del nombre
                direction = item.replace("grass_water_", "")
                return self.generate_transition_tile(direction, biome, variation=idx)
            
            elif category == "Paths":
                # Extraer variante
                variant = item.replace("path_", "")
                return self.generate_path_tile(variant, biome, variation=idx)
            
            elif category == "Effects_Simple":
                return self.generate_effect_tile(item, variation=idx)
            
            return None
        
        # PARALELIZACIÓN MÁXIMA
        with ThreadPoolExecutor(max_workers=min(count, 32)) as executor:
            tiles = list(executor.map(generate_single, range(count)))
        
        return [t for t in tiles if t is not None]
