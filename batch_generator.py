import os
import argparse
from pixel_engine import PixelArtGenerator
from image_utils import remove_background, pixelate
from assets_config import BIOMES, ASSETS, PROMPT_TEMPLATES
from PIL import Image

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def main():
    parser = argparse.ArgumentParser(description="Generador Masivo de Pixel Art")
    parser.add_argument("--output", type=str, default="output_assets", help="Carpeta de salida")
    parser.add_argument("--count", type=int, default=1, help="Variaciones por asset")
    parser.add_argument("--biome", type=str, default="all", help="Bioma específico o 'all'")
    parser.add_argument("--category", type=str, default="all", help="Categoría específica o 'all'")
    
    args = parser.parse_args()
    
    # Inicializar generador
    generator = PixelArtGenerator()
    generator.load_model()
    
    biomes_to_process = BIOMES if args.biome == "all" else [args.biome]
    categories_to_process = ASSETS.keys() if args.category == "all" else [args.category]
    
    total_tasks = len(biomes_to_process) * sum(len(ASSETS[c]) for c in categories_to_process) * args.count
    print(f"Iniciando generación de {total_tasks} assets...")
    
    current = 0
    for biome in biomes_to_process:
        for category in categories_to_process:
            if category not in ASSETS: continue
            
            items = ASSETS[category]
            for item in items:
                # Construir prompt
                template = PROMPT_TEMPLATES.get(category, PROMPT_TEMPLATES["default"])
                prompt = template.format(item=item, biome=biome)
                
                print(f"[{current+1}/{total_tasks}] Generando: {item} ({biome})...")
                
                # Generar
                images = generator.generate(
                    prompt=prompt,
                    num_inference_steps=30,
                    guidance_scale=7.5,
                    width=512,
                    height=512,
                    num_images=args.count
                )
                
                # Procesar y Guardar
                save_dir = os.path.join(args.output, biome, category)
                ensure_dir(save_dir)
                
                for i, img in enumerate(images):
                    # Post-procesado
                    # 1. Pixelar (opcional, el modelo ya debería hacerlo, pero forzamos un poco)
                    # img = pixelate(img, pixel_size=4) 
                    
                    # 2. Quitar fondo
                    img_no_bg = remove_background(img)
                    
                    # Guardar
                    filename = f"{item.replace(' ', '_')}_{i+1}.png"
                    filepath = os.path.join(save_dir, filename)
                    img_no_bg.save(filepath)
                
                current += args.count

    print("Generación masiva completada.")

if __name__ == "__main__":
    main()
