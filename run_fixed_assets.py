import os
from procedural_engine import ProceduralEngine
from PIL import Image
from image_utils import validate_image, evaluate_image_quality, init_clip_qa

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
    "ancient ruins": "Mountain"
}

def resolve_biome_folder(label: str) -> str:
    key = label.lower()
    if key in BIOME_FOLDER_MAP:
        return BIOME_FOLDER_MAP[key]
    if key in BIOME_FOLDER_ALIASES:
        return BIOME_FOLDER_ALIASES[key]
    return label.title() if label.islower() else label

def main():
    engine = ProceduralEngine(tile_size=64)
    base_path = os.path.join("public", "assets", "Biomes")
    init_clip_qa()
    
    print("🏭 Generando Assets Fijos y Críticos (V13.0)...")
    
    # Tareas estructuradas
    tasks = []

    def add_task(target_category: str, subpath: str, generator_category: str, item: str, biome: str, variation: int = 0, color_override=None):
        tasks.append({
            "target_category": target_category,
            "subpath": subpath,
            "generator_category": generator_category,
            "item": item,
            "biome": biome,
            "variation": variation,
            "color_override": color_override
        })
    
    # 1. PERSONAJES BASE
    # whomen1-4, man1-4
    for i in range(1, 5):
        add_task("Entities", f"animated/characters/whomen{i}.png", "Characters", "villager", "Forest", i)
        add_task("Entities", f"animated/characters/man{i}.png", "Characters", "villager", "Forest", i + 10)
        
    # 2. VARIANTES GENÉTICAS (Colores forzados)
    # man1/2, whomen1/2 -> golden, orange, blue, purple, gray, sepia
    variants = ["golden", "orange", "blue", "purple", "gray", "sepia"]
    base_chars = ["man1", "man2", "whomen1", "whomen2"]
    
    color_map = {
        "golden": (255, 215, 0),
        "orange": (255, 165, 0),
        "blue": (100, 149, 237),
        "purple": (147, 112, 219),
        "gray": (128, 128, 128),
        "sepia": (112, 66, 20)
    }
    
    for char in base_chars:
        for var in variants:
            add_task(
                "Entities",
                f"animated/characters/genetic_variants/{char}_{var}.png",
                "Characters",
                "villager",
                "Forest",
                0,
                color_map[var]
            )

    # 3. COMIDA ESPECÍFICA
    food_items = [
        ("05_apple_pie.png", "apple pie"),
        ("88_salmon.png", "raw fish"),
        ("40_eggsalad.png", "salad"),
        ("15_burger.png", "burger"),
        ("81_pizza.png", "pizza"),
        ("07_bread.png", "bread"),
        ("57_icecream.png", "icecream"),
        ("92_sandwich.png", "sandwich"),
        ("54_hotdog.png", "hotdog"),
        ("44_frenchfries.png", "fries"),
        ("30_chocolatecake.png", "cake"),
        ("34_donut.png", "donut"),
        ("83_popcorn.png", "popcorn"),
        ("28_cookies.png", "cookie")
    ]
    for filename, item_name in food_items:
        add_task("Props", f"consumable_items/food/{filename}", "Items", item_name, "Forest")

    # 4. ZONAS
    zones = [
        "food", "water", "rest", "work", "storage", "medical", 
        "training", "knowledge", "spiritual", "market", "defense", "social"
    ]
    for zone in zones:
        add_task("Props", f"zones/zone_{zone}.png", "UI_Icons", f"{zone} icon", "Forest")

    # 5. ESTRUCTURAS BASE
    add_task("Structures", "agent_built_house.png", "Structures", "house", "Forest")
    add_task("Structures", "agent_built_mine.png", "Structures", "mine entrance", "Mountain")
    add_task("Structures", "agent_built_workbench.png", "Structures", "crafting workbench", "Forest")
    add_task("Props", "flags/checkpoint_flag_idle1.png", "Props", "flag", "Forest")
    add_task("Props", "flags/checkpoint_flag_out1.png", "Props", "flag", "Forest", 1)
    add_task("Props", "ui/pointer_idle.png", "UI_Icons", "pointer", "Forest")

    # 6. ANIMALES BASE
    animals = [
        ("rabbit_32.png", "rabbit"), ("deer_32.png", "deer"), ("boar_32.png", "pig"),
        ("bird_32.png", "bird"), ("fish_32.png", "fish"), ("chicken.png", "chicken"), ("pig.png", "pig")
    ]
    for filename, animal in animals:
        add_task("Entities", f"animals/{filename}", "Animals", animal, "Forest")
        
    # 7. RECURSOS DE MUNDO (Fallbacks)
    resources = [
        ("oak_tree.png", "Vegetation", "tree", "Forest"),
        ("rock_1_1.png", "Minerals_Natural", "rock", "Mountain"),
        ("water.png", "Terrain", "water tile", "Forest"),
        ("berry_bush.png", "Vegetation", "bush", "Forest"),
        ("mushroom.png", "Vegetation", "mushroom cluster", "Forest"),
        ("trash.png", "Props", "crate", "Forest") # Trash pile fallback
    ]
    # Estos van en la raíz de assets o donde corresponda según el loader, 
    # pero el usuario indicó rutas relativas en su análisis. Asumiremos assets/
    # Ajuste: El usuario listó "oak_tree.png" sin ruta completa en la sección 11, 
    # pero en la 4 dice "assets/foliage/trees/oak_tree.png". Usaremos rutas lógicas.
    
    add_task("Trees", "foliage/oak_tree.png", "Vegetation", "tree", "Forest")
    add_task("Rocks", "rocks/rock_1_1.png", "Minerals_Natural", "rock", "Mountain")
    
    # EJECUCIÓN
    for task in tasks:
        folder = os.path.join(base_path, resolve_biome_folder(task["biome"]), task["target_category"])
        full_path = os.path.join(folder, task["subpath"])
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        # Generar
        # Nota: generate_batch devuelve lista, aquí queremos 1.
        # Usaremos métodos directos si es posible o batch[0]
        
        # Hack para color override en personajes:
        # Modificamos temporalmente el engine o pasamos un parámetro extra si pudiéramos.
        # Como no podemos cambiar la firma de generate_character fácilmente desde aquí sin editar engine,
        # usaremos un truco: Si hay color_override, tintamos la imagen resultante.
        
        # Llamada genérica
        category = task["generator_category"]
        item = task["item"]
        biome = task["biome"]
        variation = task["variation"]
        color_override = task["color_override"]

        if category == "Characters":
            img = engine.generate_character(biome, item, variation)
        elif category == "Items":
            img = engine.generate_item(biome, item, variation)
        elif category == "UI_Icons":
            img = engine.generate_icon(biome, item, variation)
        elif category == "Structures":
            img = engine.generate_structure(biome, item, variation)
        elif category == "Props":
            img = engine.generate_prop(biome, item, variation)
        elif category == "Animals":
            img = engine.generate_animal(biome, item, variation)
        elif category == "Vegetation":
            if "tree" in item:
                img = engine.generate_tree(biome, variation)
            elif "bush" in item:
                img = engine.generate_bush(biome, variation)
            else:
                img = engine.generate_bush(biome, variation)
        elif category == "Minerals_Natural":
            img = engine.generate_rock(biome, variation)
        elif category == "Terrain":
            img = engine.generate_terrain_tile("water" if "water" in item else "grass", biome, variation)
        else:
            img = Image.new("RGBA", (64, 64), (255, 0, 255, 255)) # Error placeholder
            
        # Aplicar Color Override (Tintado simple)
        if color_override:
            r, g, b = color_override
            data = img.getdata()
            new_data = []
            for item in data:
                if item[3] > 0: # Si no es transparente
                    # Mezclar con color override (Multiply)
                    new_r = int(item[0] * (r/255))
                    new_g = int(item[1] * (g/255))
                    new_b = int(item[2] * (b/255))
                    new_data.append((new_r, new_g, new_b, item[3]))
                else:
                    new_data.append(item)
            img.putdata(new_data)
            
        prompt = f"{biome} {item}"
        if not validate_image(img):
            print(f"  ⚠️  {task['subpath']} descartado: imagen vacía o inválida")
            continue
        qa = evaluate_image_quality(img, prompt=prompt)
        if qa["score"] < 60:
            print(f"  ⚠️  {task['subpath']} descartado: score {qa['score']:.1f}")
            continue
        rel_output = os.path.relpath(full_path, base_path)
        print(f"  ✅ Generado: {rel_output} (score {qa['score']:.1f})")
        img.save(full_path)

if __name__ == "__main__":
    main()
