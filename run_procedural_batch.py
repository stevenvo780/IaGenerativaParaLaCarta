import os
import argparse
from procedural_engine import ProceduralEngine
from assets_config import ASSETS, BIOMES

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=10, help="Cantidad por asset")
    parser.add_argument("--size", type=int, default=64, help="Tamaño de tile/sprite")
    args = parser.parse_args()

    engine = ProceduralEngine(tile_size=args.size)
    
    # Categorías soportadas por el motor procedural actual
    SUPPORTED_CATEGORIES = [
        "Terrain", "Terrain_Transitions", "Paths", "Effects_Simple",
        "Vegetation", "Minerals_Natural",
        "Structures", "Props"  # Nuevas categorías
    ]
    
    print(f"🚀 Generando {args.count} variantes por asset...")
    
    for biome in BIOMES:
        print(f"\n🌍 Bioma: {biome}")
        
        for category in SUPPORTED_CATEGORIES:
            if category not in ASSETS: continue
            
            print(f"  📦 Categoría: {category}")
            items = ASSETS[category]
            
            for item in items:
                # Generar lote
                images = engine.generate_batch(category, item, biome, count=args.count)
                
                # Guardar
                save_dir = os.path.join("output_assets_procedural", biome, category)
                ensure_dir(save_dir)
                
                for i, img in enumerate(images):
                    filename = f"{item.replace(' ', '_')}_{i}.png"
                    img.save(os.path.join(save_dir, filename))
                
                print(f"    ✅ {item}: {len(images)} generados")

if __name__ == "__main__":
    main()
