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

# Configuración de Prompts para SDXL (ESTILO ONÍRICO E HISTÓRICO + FUSIÓN)
PROMPT_TEMPLATES = {
    # Default: Enfocado en objeto único, estilo místico/histórico
    "default": "pixel art, single {adjective} {item} in {biome} style, centered, isolated on white background, oneiric, historical, dreamlike, ethereal, ancient, mystical, soft lighting, pastel colors, game asset, sharp focus, 8-bit, no shadows, no background scenery, no text, no ui",
    
    # Characters: Estilo heroico/místico
    "Characters": "pixel art, single {item}, {frame}, {biome} style, centered, full body, isolated on white background, historical fantasy, dreamlike, detailed armor/clothing, game sprite, retro style, clean lines, no background",
    
    # Terrain: Texturas antiguas
    "Terrain": "pixel art, top down tile of {adjective} {item} in {biome} style, seamless texture, flat view, ancient ruins aesthetic, dreamlike colors, game asset, rpg style, no perspective",
    
    # Paths: Caminos viejos
    "Paths": "pixel art, top down tile of {adjective} {item} in {biome} style, seamless texture, flat view, worn ancient path, historical, game asset, rpg style, no perspective",
    
    # UI_Icons: Estilo manuscrito/runas
    "UI_Icons": "pixel art, icon of {item}, UI element, ancient manuscript style, rune aesthetic, flat, white background, simple, high contrast, centered",
    
    # Effects: Magia etérea
    "Effects": "pixel art, {adjective} {item} in {biome} style, game effect, ethereal magic, dreamlike, isolated, white background"
}
