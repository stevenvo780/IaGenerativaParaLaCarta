import os
import argparse
from procedural_engine import ProceduralEngine

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

# Lista de Props a generar por bioma
PROPS_LIST = [
    "crate", "barrel", "table", "chair", "bench", 
    "lantern", "street lamp", "chest", "window frame",
    "market umbrella", "clothesline", "glass bottle"
]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=5, help="Cantidad por asset")
    parser.add_argument("--size", type=int, default=64, help="Tamaño de tile/sprite")
    args = parser.parse_args()

    engine = ProceduralEngine(tile_size=args.size)
    base_path = "public/assets"
    
    print(f"🚀 Generando estructura RECURSIVA con PROPS VARIADOS en '{base_path}'...")
    
    tasks = []
    
    # --- 1. TILES ---
    for user_biome, engine_biome in BIOME_MAP.items():
        tasks.append({"path": f"tiles/terrain/{user_biome}", "cat": "Terrain", "item": "grass tile", "biome": engine_biome})
    
    tasks.append({"path": "tiles/water/lake", "cat": "Terrain", "item": "water tile", "biome": "Forest"})
    tasks.append({"path": "tiles/water/ocean", "cat": "Terrain", "item": "water tile", "biome": "Beach"})
    tasks.append({"path": "tiles/water/river", "cat": "Terrain", "item": "water tile", "biome": "Grassland"})

    # --- 2. OBJECTS ---
    for user_biome, engine_biome in BIOME_MAP.items():
        # Trees
        tasks.append({"path": f"objects/trees/{user_biome}", "cat": "Vegetation", "item": "tree", "biome": engine_biome})
        # Plants
        tasks.append({"path": f"objects/plants/{user_biome}", "cat": "Vegetation", "item": "bush", "biome": engine_biome})
        
        # PROPS VARIADOS (Corrección)
        for prop_name in PROPS_LIST:
            tasks.append({
                "path": f"objects/props/{user_biome}", 
                "cat": "Props", 
                "item": prop_name, 
                "biome": engine_biome
            })
        
    # Rocks
    tasks.append({"path": "objects/rocks", "cat": "Minerals_Natural", "item": "rock", "biome": "Mountain"})

    # --- 3. DECALS ---
    for user_biome, engine_biome in BIOME_MAP.items():
        tasks.append({"path": f"decals/{user_biome}", "cat": "Effects_Simple", "item": "dirt_patch", "biome": engine_biome})

    # --- 4. ENTITIES ---
    tasks.append({"path": "entities/animals", "cat": "Animals", "item": "pig", "biome": "Grassland"})
    tasks.append({"path": "entities/animals", "cat": "Animals", "item": "cow", "biome": "Grassland"})
    tasks.append({"path": "entities/animals", "cat": "Animals", "item": "chicken", "biome": "Forest"})
    tasks.append({"path": "entities/characters", "cat": "Characters", "item": "villager", "biome": "Forest"})
    
    # --- 5. ITEMS & CONSUMABLES ---
    tasks.append({"path": "items", "cat": "Items", "item": "sword", "biome": "Forest"})
    tasks.append({"path": "items", "cat": "Items", "item": "shield", "biome": "Forest"})
    tasks.append({"path": "consumable_items/food", "cat": "Items", "item": "apple", "biome": "Forest"})
    tasks.append({"path": "consumable_items/food", "cat": "Items", "item": "bread", "biome": "Forest"})

    # --- 6. STRUCTURES ---
    tasks.append({"path": "structures/estructuras_completas", "cat": "Structures", "item": "house", "biome": "Forest"})
    tasks.append({"path": "structures/ruins", "cat": "Structures", "item": "wall", "biome": "Ancient Ruins"})
    tasks.append({"path": "structures/interiores", "cat": "Props", "item": "table", "biome": "Forest"})

    # EJECUCIÓN
    for task in tasks:
        full_path = os.path.join(base_path, task["path"])
        if not os.path.exists(full_path):
            os.makedirs(full_path)
            
        # print(f"  📂 {task['path']} -> {task['item']}...") # Menos verboso
        
        images = engine.generate_batch(
            task["cat"], 
            task["item"], 
            task["biome"], 
            count=args.count
        )
        
        for i, img in enumerate(images):
            filename = f"{task['item']}_{task['biome']}_{i}.png"
            img.save(os.path.join(full_path, filename))
            
    print("✅ Generación finalizada.")

if __name__ == "__main__":
    main()
