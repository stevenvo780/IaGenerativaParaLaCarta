# Configuración de Generación Masiva

# 10 Biomas solicitados
BIOMES = [
    "Forest",
    "Desert",
    "Snowy Tundra",
    "Volcanic Wasteland",
    "Swamp",
    "Tropical Beach",
    "Crystal Cave",
    "Dense Jungle",
    "Ethereal Floating Islands",
    "Ancient Ruins"
]

# Mapeo de assets solicitados
# Mapeo de assets solicitados (Lista Completa Expandida)
ASSETS = {
    "Terrain": [
        "grass tile", "water tile", "grass to water transition edge", "grass to water transition corner"
    ],
    "Paths": [
        "dirt path straight", "dirt path curve", "dirt path crossing", "dirt path intersection",
        "stone path straight", "stone path curve", "stone path crossing", "stone path intersection"
    ],
    "Vegetation": [
        "oak tree", "willow tree", "pine tree", "glowing magical tree", "dead tree",
        "bush", "flowering bush", "mushroom", "cluster of mushrooms", "flower patch", "single flower"
    ],
    "Minerals_Natural": [
        "small rock", "large boulder", "mossy rock", "ancient ruin pillar", "broken ruin wall"
    ],
    "Structures": [
        "small house", "wooden cottage", "stone well", "wooden fence", "stone wall", "castle gate",
        "mine entrance", "crafting workbench"
    ],
    "Props": [
        "wooden chair", "wooden bench", "wooden table", "window frame", "street lamp", "lantern post",
        "wooden barrel", "treasure chest", "wooden crate", "market stall umbrella", "clothesline with clothes", "glass bottle"
    ],
    "Characters": [
        "male warrior", "female mage", "male villager", "female villager",
        "male warrior dark skin", "female mage dark skin", "male villager blue clothes", "female villager red clothes"
    ],
    "Character_Accessories": [
        "golden crown", "headband", "scar overlay", "iron armor chestplate", "hero cape", 
        "magical aura effect", "fire aura effect"
    ],
    "Social_Markers": [
        "geometric circle symbol", "geometric star symbol", "geometric triangle symbol",
        "guild badge red", "guild badge blue", "friendship bracelet", "gold necklace"
    ],
    "Animals": [
        "rabbit", "deer", "wild boar", "bird", "fish"
    ],
    "Items": [
        "iron axe", "pickaxe", "fishing rod", "sword", "shield",
        "wood log", "stone ore", "gold ore", "iron ore",
        "bread", "red apple", "cooked meat", "raw fish", "honey jar",
        "health potion", "mana potion", "herb bundle", "water flask"
    ],
    "UI_Icons": [
        "shield icon (defense)", "bread icon (food)", "book icon (knowledge)", "coin icon (market)", 
        "cross icon (medic)", "bed icon (rest)", "speech bubble icon (social)", "star icon (spiritual)", 
        "chest icon (storage)", "sword icon (training)", "drop icon (water)", "hammer icon (work)"
    ],
    "Effects": [
        "dirt patch decal", "shadow blob", "animated campfire"
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

# Configuración de Prompts para SDXL (CALIDAD MÁXIMA)
PROMPT_TEMPLATES = {
    # Default: Enfocado en objeto único, máxima calidad pixel art
    "default": "masterpiece, best quality, pixel art, single {adjective} {item} in {biome} style, centered, isolated on white background, sharp pixels, clean lines, vibrant colors, professional game asset, 16-bit style, no shadows, no background scenery, no text, no ui, highly detailed",
    
    # Characters: Estilo heroico/místico de alta calidad
    "Characters": "masterpiece, best quality, pixel art, single {item}, {frame}, {biome} style, centered, full body, isolated on white background, sharp pixels, detailed sprite, professional character design, clean lines, vibrant colors, rpg style, no background, highly detailed",
    
    # Terrain: Texturas de alta calidad
    "Terrain": "masterpiece, best quality, pixel art, top down tile of {adjective} {item} in {biome} style, seamless texture, flat view, sharp pixels, clean tileable pattern, vibrant colors, professional game asset, 16-bit rpg style, no perspective, highly detailed",
    
    # Paths: Caminos detallados
    "Paths": "masterpiece, best quality, pixel art, top down tile of {adjective} {item} in {biome} style, seamless texture, flat view, sharp pixels, clean path pattern, vibrant colors, professional game asset, 16-bit rpg style, no perspective, highly detailed",
    
    # UI_Icons: Iconos nítidos
    "UI_Icons": "masterpiece, best quality, pixel art, icon of {item}, UI element, sharp pixels, clean design, high contrast, vibrant colors, centered, white background, simple, professional game ui, 16-bit style, highly detailed",
    
    # Effects: Efectos de alta calidad
    "Effects": "masterpiece, best quality, pixel art, {adjective} {item} in {biome} style, game effect, sharp pixels, vibrant colors, clean design, isolated, white background, professional vfx, highly detailed"
}
