import os
import argparse
import concurrent.futures
from queue import Queue
from pixel_engine import PixelArtGenerator
from image_utils import remove_background, pixelate, crop_to_content
from assets_config import BIOMES, ASSETS, PROMPT_TEMPLATES, BIOME_ADJECTIVES
from PIL import Image

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def process_and_save_image(image, save_path):
    """Función worker para procesar y guardar imágenes en segundo plano."""
    try:
        # 1. Quitar fondo
        img_no_bg = remove_background(image)
        # 2. Recorte automático
        img_cropped = crop_to_content(img_no_bg)
        # 3. Guardar
        img_cropped.save(save_path)
        # print(f"Guardado: {save_path}") # Demasiado ruido en consola
    except Exception as e:
        print(f"Error procesando {save_path}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Generador Masivo de Pixel Art (Asíncrono)")
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
    print(f"Iniciando generación de {total_tasks} assets con Pipeline Asíncrono...")
    
    # ThreadPool para procesamiento en background (CPU bound tasks)
    # Usamos max_workers=4 para no saturar la CPU si la generación es muy rápida, 
    # aunque con SDXL la GPU es el cuello de botella principal, así que la CPU tendrá tiempo.
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        current = 0
        for biome in biomes_to_process:
            biome_adj = BIOME_ADJECTIVES.get(biome, "")
            
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
                            # No usamos adjetivo aquí porque el template de Characters es diferente, 
                            # pero podríamos añadirlo si quisiéramos. Por ahora mantenemos simple.
                            prompt = template.format(item=item, biome=biome, frame=frame_desc)
                            
                            print(f"  > Generando Frame: {frame_desc}")
                            images = generator.generate(
                                prompt=prompt,
                                num_inference_steps=40,
                                guidance_scale=6.5,
                                width=1024,
                                height=1024,
                                num_images=1
                            )
                            frames_images.append(images[0])
                        
                        # Guardar frames individuales y sprite sheet
                        save_dir = os.path.join(args.output, biome, category, item.replace(" ", "_"))
                        ensure_dir(save_dir)
                        
                        # Procesar frames en paralelo? No, necesitamos orden para el sprite sheet.
                        # Procesamos síncronamente o en grupo para este caso específico complejo.
                        # Para simplificar, procesamos síncronamente la creación del sprite sheet 
                        # pero el guardado de frames individuales podría ser async.
                        # Dado que Characters son complejos, los hacemos en el hilo principal para evitar race conditions en la lista.
                        
                        processed_frames = []
                        for i, (img, frame_name) in enumerate(zip(frames_images, CHARACTER_FRAMES)):
                            img_no_bg = remove_background(img)
                            img_cropped = crop_to_content(img_no_bg)
                            processed_frames.append(img_cropped)
                            
                            safe_frame_name = frame_name.replace(" ", "_").replace(",", "")
                            path = os.path.join(save_dir, f"frame_{i}_{safe_frame_name}.png")
                            img_cropped.save(path)
                        
                        from image_utils import create_sprite_sheet
                        sprite_sheet = create_sprite_sheet(processed_frames, columns=len(processed_frames))
                        if sprite_sheet:
                            sprite_sheet.save(os.path.join(save_dir, "sprite_sheet_full.png"))
                            
                    else:
                        # Lógica estándar para otros assets (PIPELINE ASÍNCRONO)
                        template = PROMPT_TEMPLATES.get(category, PROMPT_TEMPLATES["default"])
                        # Inyectar adjetivo
                        prompt = template.format(item=item, biome=biome, adjective=biome_adj)
                        
                        images = generator.generate(
                            prompt=prompt,
                            num_inference_steps=40, 
                            guidance_scale=6.5,
                            width=1024,
                            height=1024,
                            num_images=args.count
                        )
                        
                        save_dir = os.path.join(args.output, biome, category)
                        ensure_dir(save_dir)
                        
                        for i, img in enumerate(images):
                            filename = f"{item.replace(' ', '_')}_{i+1}.png"
                            save_path = os.path.join(save_dir, filename)
                            
                            # ENVIAR A WORKER (No bloquea el loop principal)
                            executor.submit(process_and_save_image, img, save_path)
                    
                    current += args.count

    print("Generación masiva completada. Esperando a que terminen los procesos de fondo...")
    # El 'with' del executor esperará automáticamente a que terminen las tareas pendientes.

if __name__ == "__main__":
    main()
