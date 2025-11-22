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

# Mapeo de assets solicitados (Traducidos a Inglés para mejor prompting)
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
        "male warrior", "female mage", "male villager", "female villager"
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

# Configuración de Prompts para SDXL
PROMPT_TEMPLATES = {
    "default": "pixel art, {item} in {biome}, isometric game asset, white background, clean lines, detailed, 8-bit style",
    "Characters": "pixel art, sprite sheet of {item} in {biome}, character grid, walking animation frames, side view, white background, retro style",
    "Terrain": "pixel art, top down tile of {item} in {biome}, seamless texture, flat view, game asset, rpg style",
    "Paths": "pixel art, top down tile of {item} in {biome}, seamless texture, flat view, game asset, rpg style",
    "UI_Icons": "pixel art, icon of {item}, UI element, vector style, flat, white background, simple, high contrast",
    "Effects": "pixel art, {item} in {biome}, game effect, sprite sheet, white background"
}
