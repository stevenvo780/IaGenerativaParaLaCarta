# Configuración de Generación Masiva

# Lista de Biomas
BIOMES = ["Forest", "Desert", "Snowy Tundra", "Volcanic Wasteland", "Swamp",
          "Underwater Realm", "Sky Islands", "Crystal Caves", "Mushroom Grove", "Ancient Ruins"]

# Clasificación de métodos de generación
PROCEDURAL_CATEGORIES = {
    "Terrain",              # grass, water, dirt tiles
    "Terrain_Transitions",  # 16 tiles de transición césped-agua
    "Paths",                # 15 tiles de caminos (horizontal, vertical, curvas, T, cross, ends)
    "Effects_Simple"        # dirt patches, sombras
}

AI_CATEGORIES = {
    "Vegetation",           # Árboles, arbustos, flores
    "Minerals_Natural",     # Rocas, minerales, ruinas
    "Structures",           # Casas, pozos, cercas
    "Props",                # Muebles, cofres, lámparas
    "Characters",           # Personajes con animación
    "Character_Accessories",# Overlays de personajes
    "Social_Markers",       # Símbolos y badges
    "Animals",              # Fauna
    "Items",                # Herramientas, comida, consumibles
    "UI_Icons",             # Iconos de interfaz
    "Effects_Complex"       # Fogata animada (requiere IA)
}

# Catálogo de Assets (Según Solicitud Completa)
ASSETS = {
    # ===== PROCEDURAL (Rápido, Seamless Garantizado) =====
    "Terrain": [
        "grass tile",
        "water tile",
        "dirt tile"
    ],
    "Terrain_Transitions": [
        # Bordes (4)
        "grass_water_edge_N", "grass_water_edge_S", "grass_water_edge_E", "grass_water_edge_W",
        # Esquinas externas (4)
        "grass_water_corner_NE", "grass_water_corner_NW", "grass_water_corner_SE", "grass_water_corner_SW",
        # Esquinas internas (4)
        "grass_water_inner_NE", "grass_water_inner_NW", "grass_water_inner_SE", "grass_water_inner_SW"
    ],
    "Paths": [
        # Rectos (2)
        "path_horizontal", "path_vertical",
        # Curvas (4)
        "path_curve_NE", "path_curve_NW", "path_curve_SE", "path_curve_SW",
        # T-junctions (4)
        "path_T_N", "path_T_S", "path_T_E", "path_T_W",
        # Cruce y terminaciones
        "path_cross",
        "path_end_N", "path_end_S", "path_end_E", "path_end_W"
    ],
    "Effects_Simple": [
        "dirt_patch",
        "shadow_circular",
        "shadow_square"
    ],
    
    # ===== IA (Objetos Complejos) =====
    "Vegetation": [
        "oak tree", "willow tree", "pine tree", "glowing magical tree", "dead tree",
        "bush", "flowering bush", "mushroom cluster", "flower patch"
    ],
    "Minerals_Natural": [
        "small rock", "large boulder", "mossy rock", "ancient ruin pillar", "broken ruin wall"
    ],
    "Structures": [
        "small house", "wooden cottage", "stone well", "wooden fence", "stone wall segment", "castle gate",
        "mine entrance", "crafting workbench"
    ],
    "Props": [
        "wooden chair", "wooden bench", "wooden table", "window frame", "street lamp", "lantern post",
        "wooden barrel", "treasure chest", "wooden crate", "market umbrella", "clothesline", "glass bottle"
    ],
    "Characters": [
        "male warrior", "female mage", "male villager", "female villager"
    ],
    "Character_Accessories": [
        "golden crown", "headband", "scar overlay", "iron armor overlay", "hero cape",
        "magical aura", "fire aura"
    ],
    "Social_Markers": [
        "circle symbol", "star symbol", "triangle symbol",
        "red badge", "blue badge", "green badge",
        "bracelet", "necklace"
    ],
    "Animals": [
        "rabbit", "deer", "wild boar", "bird", "fish"
    ],
    "Items": [
        # Herramientas
        "iron axe", "pickaxe", "fishing rod", "sword", "shield",
        # Recursos
        "wood log", "stone ore", "gold ore", "iron ore",
        # Comida
        "bread", "red apple", "cooked meat", "raw fish", "honey jar",
        # Consumibles
        "health potion", "mana potion", "herb bundle", "water flask"
    ],
    "UI_Icons": [
        "defense icon", "food icon", "knowledge icon", "market icon",
        "medic icon", "rest icon", "social icon", "spiritual icon",
        "storage icon", "training icon", "water icon", "work icon"
    ],
    "Effects_Complex": [
        "animated campfire"  # Animado, necesita IA
    ]
}

# Definición de Frames para Animaciones
CHARACTER_FRAMES = [
    "idle pose, front view",
    "walking pose, left leg forward, side view",
    "walking pose, right leg forward, side view",
    "attack pose, swinging weapon, dynamic action"
]

# Adjetivos por Bioma para mejorar coherencia (Fusión de Biomas)
BIOME_ADJECTIVES = {
    "Forest": "lush, mossy, wooden, natural",
    "Desert": "sandy, dry, ancient, sun-bleached",
    "Snowy Tundra": "frozen, icy, snow-covered, cold",
    "Volcanic Wasteland": "charred, burning, obsidian, dark",
    "Swamp": "slimy, muddy, rotten, vine-covered",
    "Tropical Beach": "sandy, bright, tropical, sun-kissed",
    "Crystal Cave": "crystalline, glowing, translucent, magical",
    "Dense Jungle": "overgrown, vine-covered, exotic, vibrant",
    "Ethereal Floating Islands": "celestial, floating, glowing, airy",
    "Ancient Ruins": "cracked, broken, mossy stone, weathered"
}

# Configuración de Prompts para SDXL (UN SOLO OBJETO, CALIDAD MÁXIMA)
PROMPT_TEMPLATES = {
    # Default: UN SOLO objeto, aislado, centrado
    "default": "single {item}, ONE object only, centered, isolated sprite, white background, {adjective} {biome} style, masterpiece, best quality, sharp pixels, clean lines, vibrant colors, professional game asset, 16-bit style, no background elements",
    
    # Characters: UN personaje, cuerpo completo
    "Characters": "single {item}, {frame}, ONE character only, {biome} style, centered, full body sprite, isolated, white background, masterpiece, best quality, sharp pixels, detailed character, professional design, clean lines, vibrant colors, rpg style, no background",
    
    # Terrain: Tiles limpios (estos sí pueden tener textura completa)
    "Terrain": "top down tile, {adjective} {item}, {biome} style, seamless texture, flat view, sharp pixels, clean tileable pattern, vibrant colors, professional game asset, 16-bit rpg style, no perspective",
    
    # Paths: Caminos limpios
    "Paths": "top down tile, {adjective} {item}, {biome} style, seamless texture, flat view, sharp pixels, clean path pattern, vibrant colors, professional game asset, 16-bit rpg style, no perspective",
    
    # UI_Icons: Iconos simples
    "UI_Icons": "single icon, {item}, ONE object only, UI element, sharp pixels, clean design, high contrast, vibrant colors, centered, white background, simple, professional game ui, 16-bit style",
    
    # Effects: Efectos aislados
    "Effects": "single effect, {item}, ONE object only, {adjective} {biome} style, game effect, sharp pixels, vibrant colors, clean design, isolated, white background, professional vfx"
}
