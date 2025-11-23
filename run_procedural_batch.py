import os
import argparse
from procedural_engine import ProceduralEngine
from image_utils import validate_image, evaluate_image_quality, init_clip_qa

# Mapeo de Biomas
BIOME_MAP = {
    "beach": "Beach",
    "desert": "Desert",
    "forest": "Forest",
    "grassland": "Grassland",
    "mountain": "Mountain",
    "swamp": "Swamp",
    "tundra": "Snowy Tundra"
}

BIOME_FOLDER_MAP = {
    "beach": "Beach",
    "desert": "Desert",
    "forest": "Forest",
    "grassland": "Grassland",
    "mountain": "Mountain",
    "swamp": "Swamp",
    "tundra": "Tundra"
}

BIOME_FOLDER_ALIASES = {
    "snowy tundra": "Tundra",
    "ancient ruins": "Mountain",
    "volcanic wasteland": "Mountain"
}

def resolve_biome_folder(label: str) -> str:
    key = label.lower()
    if key in BIOME_FOLDER_MAP:
        return BIOME_FOLDER_MAP[key]
    if key in BIOME_FOLDER_ALIASES:
        return BIOME_FOLDER_ALIASES[key]
    return label.title() if label.islower() else label

# Lista de Props a generar por bioma (EXPANDIDA)
PROPS_LIST = [
    # Muebles básicos
    "crate", "barrel", "table", "chair", "bench", "chest",
    # Iluminación
    "lantern", "street lamp", "torch", "candelabra",
    # Decoración
    "window frame", "market umbrella", "clothesline", "glass bottle",
    "flower pot", "vase", "painting", "rug", "curtain", "skull",
    # Herramientas/Trabajo
    "anvil", "forge", "loom", "spinning wheel", "workbench",
    # Almacenamiento
    "shelf", "bookshelf", "wardrobe", "cabinet",
    # Cocina/Comida
    "oven", "cauldron", "cooking pot", "food barrel",
    # Exterior
    "well", "fountain", "statue", "signpost", "flag"
]

# Lista de Animales (EXPANDIDA)
ANIMALS_LIST = [
    "pig", "cow", "sheep", "chicken", "horse",
    "rabbit", "deer", "wolf", "bear", "fox",
    "duck", "goose", "cat", "dog", "goat"
]

PATH_VARIANTS = [
    "path tile",
    "stone path",
    "wooden path"
]

BUSH_VARIANTS = [
    "bush",
    "dense bush",
    "flower bush"
]

ROCK_VARIANTS = [
    "rock",
    "boulder",
    "ore rock"
]

STRUCTURE_VARIANTS = [
    "house",
    "watchtower",
    "workshop"
]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=5, help="Cantidad por asset")
    parser.add_argument("--size", type=int, default=64, help="Tamaño de tile/sprite")
    args = parser.parse_args()

    engine = ProceduralEngine(tile_size=args.size)
    base_path = os.path.join("public", "assets", "Biomes")
    init_clip_qa()
    
    print(f"🚀 Generando estructura RECURSIVA con PROPS VARIADOS en '{base_path}'...")
    
    tasks = []
    
    # --- 1. TILES ---
    for user_biome, engine_biome in BIOME_MAP.items():
        tasks.append({
            "cat": "Terrain",
            "target_category": "Terrain",
            "item": "grass tile",
            "biome": engine_biome,
            "folder": resolve_biome_folder(user_biome)
        })
    
    tasks.append({"cat": "Terrain", "target_category": "Terrain", "item": "water tile", "biome": "Forest", "folder": resolve_biome_folder("forest")})
    tasks.append({"cat": "Terrain", "target_category": "Terrain", "item": "water tile", "biome": "Beach", "folder": resolve_biome_folder("beach")})
    tasks.append({"cat": "Terrain", "target_category": "Terrain", "item": "water tile", "biome": "Grassland", "folder": resolve_biome_folder("grassland")})

    # --- 2. OBJECTS ---
    for user_biome, engine_biome in BIOME_MAP.items():
        # Trees
        tasks.append({
            "cat": "Vegetation",
            "target_category": "Trees",
            "item": "tree",
            "biome": engine_biome,
            "folder": resolve_biome_folder(user_biome)
        })
        # Plants
        for bush in BUSH_VARIANTS:
            tasks.append({
                "cat": "Vegetation",
                "target_category": "Bushes",
                "item": bush,
                "biome": engine_biome,
                "folder": resolve_biome_folder(user_biome),
                "min_score": 40
            })
        
        # PROPS VARIADOS (Corrección)
        for prop_name in PROPS_LIST:
            tasks.append({
                "cat": "Props", 
                "target_category": "Props",
                "item": prop_name, 
                "biome": engine_biome,
                "folder": resolve_biome_folder(user_biome)
            })
        
    # Rocks
    for user_biome, engine_biome in BIOME_MAP.items():
        for rock in ROCK_VARIANTS:
            tasks.append({
                "cat": "Minerals_Natural",
                "target_category": "Rocks",
                "item": rock,
                "biome": engine_biome,
                "folder": resolve_biome_folder(user_biome),
                "min_score": 45
            })

    # Paths
    for user_biome, engine_biome in BIOME_MAP.items():
        for path_variant in PATH_VARIANTS:
            tasks.append({
                "cat": "Terrain",
                "target_category": "Paths",
                "item": path_variant,
                "biome": engine_biome,
                "folder": resolve_biome_folder(user_biome),
                "min_score": 50
            })

    # --- 3. DECALS ---
    for user_biome, engine_biome in BIOME_MAP.items():
        tasks.append({
            "cat": "Effects_Simple", 
            "target_category": "Decals", 
            "item": "dirt_patch", 
            "biome": engine_biome,
            "folder": resolve_biome_folder(user_biome)
        })

    # --- 4. ENTITIES ---
    # Animals (Variedad expandida)
    for animal_name in ANIMALS_LIST:
        tasks.append({
            "cat": "Animals", 
            "target_category": "Entities", 
            "item": animal_name, 
            "biome": "Grassland",
            "folder": resolve_biome_folder("grassland")
        })
    
    # Characters
    tasks.append({
        "cat": "Characters", 
        "target_category": "Entities", 
        "item": "villager", 
        "biome": "Forest",
        "folder": resolve_biome_folder("forest")
    })
    
    # --- 5. ITEMS & CONSUMABLES ---
    for item_name in ["sword", "shield"]:
        tasks.append({
            "cat": "Items", 
            "target_category": "Props", 
            "item": item_name, 
            "biome": "Forest",
            "folder": resolve_biome_folder("forest")
        })
    for food in ["apple", "bread"]:
        tasks.append({
            "cat": "Items", 
            "target_category": "Props", 
            "item": food, 
            "biome": "Forest",
            "folder": resolve_biome_folder("forest")
        })

    # --- 6. STRUCTURES ---
    for user_biome, engine_biome in BIOME_MAP.items():
        for structure in STRUCTURE_VARIANTS:
            tasks.append({
                "cat": "Structures",
                "target_category": "Structures",
                "item": structure,
                "biome": engine_biome,
                "folder": resolve_biome_folder(user_biome),
                "min_score": 55
            })
    tasks.append({
        "cat": "Props",
        "target_category": "Props",
        "item": "table",
        "biome": "Forest",
        "folder": resolve_biome_folder("forest")
    })

    # EJECUCIÓN
    for task in tasks:
        full_path = os.path.join(base_path, task["folder"], task["target_category"])
        os.makedirs(full_path, exist_ok=True)
            
        # print(f"  📂 {task['path']} -> {task['item']}...") # Menos verboso
        
        images = engine.generate_batch(
            task["cat"], 
            task["item"], 
            task["biome"], 
            count=args.count
        )
        
        for i, img in enumerate(images):
            prompt = f"{task['biome']} {task['item']}"
            if not validate_image(img):
                print(f"⚠️  Descarta {task['item']} idx {i}: imagen vacía")
                continue
            qa = evaluate_image_quality(img, prompt=prompt)
            min_score = task.get("min_score", 60)
            if qa["score"] < min_score:
                print(f"⚠️  QA fallido ({qa['score']:.1f}) en {task['item']} idx {i}")
                continue
            filename = f"{task['item']}_{task['biome']}_{i}_s{int(qa['score'])}.png"
            img.save(os.path.join(full_path, filename))
            
    print("✅ Generación finalizada.")

if __name__ == "__main__":
    main()
