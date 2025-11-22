import os
import argparse
from pixel_engine import PixelArtGenerator
from image_utils import remove_background, pixelate, crop_to_content
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
                print(f"[{current+1}/{total_tasks}] Procesando: {item} ({biome})...")
                
                # Manejo especial para Personajes (Frame a Frame)
                if category == "Characters":
                    from assets_config import CHARACTER_FRAMES
                    frames_images = []
                    
                    # Generar cada frame
                    for frame_desc in CHARACTER_FRAMES:
                        template = PROMPT_TEMPLATES.get("Characters")
                        prompt = template.format(item=item, biome=biome, frame=frame_desc)
                        
                        print(f"  > Generando Frame: {frame_desc}")
                        images = generator.generate(
                            prompt=prompt,
                            num_inference_steps=40, # Más pasos para calidad
                            guidance_scale=6.5,     # Menor guidance para mejor estilo pixel art en SDXL
                            width=1024,
                            height=1024,
                            num_images=1
                        )
                        frames_images.append(images[0])
                    
                    # Guardar frames individuales y sprite sheet
                    save_dir = os.path.join(args.output, biome, category, item.replace(" ", "_"))
                    ensure_dir(save_dir)
                    
                    processed_frames = []
                    for i, (img, frame_name) in enumerate(zip(frames_images, CHARACTER_FRAMES)):
                        # Post-procesado
                        img_no_bg = remove_background(img)
                        # Recorte automático
                        img_cropped = crop_to_content(img_no_bg)
                        processed_frames.append(img_cropped)
                        
                        # Guardar frame individual
                        safe_frame_name = frame_name.replace(" ", "_").replace(",", "")
                        img_cropped.save(os.path.join(save_dir, f"frame_{i}_{safe_frame_name}.png"))
                    
                    # Crear Sprite Sheet (unir frames)
                    # Usamos una función simple aquí o importamos de image_utils
                    from image_utils import create_sprite_sheet
                    sprite_sheet = create_sprite_sheet(processed_frames, columns=len(processed_frames))
                    if sprite_sheet:
                        sprite_sheet.save(os.path.join(save_dir, "sprite_sheet_full.png"))
                        
                else:
                    # Lógica estándar para otros assets
                    template = PROMPT_TEMPLATES.get(category, PROMPT_TEMPLATES["default"])
                    prompt = template.format(item=item, biome=biome)
                    
                    images = generator.generate(
                        prompt=prompt,
                        num_inference_steps=40, # Aumentado para calidad
                        guidance_scale=6.5,
                        width=1024,
                        height=1024,
                        num_images=args.count
                    )
                    
                    save_dir = os.path.join(args.output, biome, category)
                    ensure_dir(save_dir)
                    
                    for i, img in enumerate(images):
                        img_no_bg = remove_background(img)
                        # Recorte automático
                        img_cropped = crop_to_content(img_no_bg)
                        
                        filename = f"{item.replace(' ', '_')}_{i+1}.png"
                        img_cropped.save(os.path.join(save_dir, filename))
                
                current += args.count

    print("Generación masiva completada.")

if __name__ == "__main__":
    main()
