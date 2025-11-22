import argparse
import os
import torch
import concurrent.futures
from PIL import Image
import gc
import json
from pixel_engine import PixelArtGenerator
from image_utils import remove_background, crop_to_content, create_sprite_sheet
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
    parser.add_argument("--biome", type=str, default="all", help="Bioma específico o 'all'")
    parser.add_argument("--category", type=str, default="all", help="Categoría específica o 'all'")
    parser.add_argument("--count", type=int, default=1, help="Número de variaciones por asset")
    parser.add_argument("--style_strength", type=float, default=0.6, help="Fuerza del estilo IP-Adapter (0.0 a 1.0)")
    
    args = parser.parse_args()
    
    ensure_dir(args.output)
    
    # Inicializar generador
    generator = PixelArtGenerator()
    generator.load_model()
    
    # Cargar imagen de referencia de estilo (si existe)
    style_image = None
    style_path = "style_reference.png"
    if os.path.exists(style_path):
        print(f"Imagen de referencia de estilo encontrada: {style_path}")
        try:
            style_image = Image.open(style_path).convert("RGB")
            print(f"Estilo cargado. Fuerza: {args.style_strength}")
        except Exception as e:
            print(f"Error cargando imagen de estilo: {e}")
    else:
        print("No se encontró 'style_reference.png'. Generando sin clonación de estilo.")

    biomes_to_process = BIOMES if args.biome == "all" else [args.biome]
    categories_to_process = ASSETS.keys() if args.category == "all" else [args.category]
    
    total_tasks = len(biomes_to_process) * sum(len(ASSETS[c]) for c in categories_to_process) * args.count
    print(f"Iniciando generación de {total_tasks} assets con Pipeline Asíncrono...")
    
    # ThreadPool para procesamiento en background (CPU bound tasks)
    # Aumentamos a 30 workers para aprovechar la CPU de 32 hilos del usuario
    # Dejamos 2 hilos libres para el sistema y la gestión de la GPU
    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
        current = 0
        for biome in biomes_to_process:
            # LIMPIEZA DE MEMORIA ENTRE BIOMAS
            gc.collect()
            torch.cuda.empty_cache()
            print(f"--- Iniciando Bioma: {biome} (Memoria Liberada) ---")
            
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
                        frames_metadata = []
                        
                        # Generar cada frame
                        for frame_desc in CHARACTER_FRAMES:
                            template = PROMPT_TEMPLATES.get("Characters")
                            prompt = template.format(item=item, biome=biome, frame=frame_desc)
                            
                            print(f"  > Generando Frame: {frame_desc}")
                            # Desempaquetar tupla (imagenes, metadatos)
                            images, meta = generator.generate(
                                prompt=prompt,
                                num_inference_steps=40,
                                guidance_scale=6.5,
                                width=1024,
                                height=1024,
                                num_images=1,
                                ip_adapter_image=style_image, # Inyectar estilo
                                ip_adapter_scale=args.style_strength # Fuerza del estilo variable
                            )
                            frames_images.append(images[0])
                            frames_metadata.append(meta)
                        
                        # Guardar frames individuales y sprite sheet
                        save_dir = os.path.join(args.output, biome, category, item.replace(" ", "_"))
                        ensure_dir(save_dir)
                        
                        processed_frames = []
                        for i, (img, frame_name) in enumerate(zip(frames_images, CHARACTER_FRAMES)):
                            img_no_bg = remove_background(img)
                            img_cropped = crop_to_content(img_no_bg)
                            processed_frames.append(img_cropped)
                            
                            safe_frame_name = frame_name.replace(" ", "_").replace(",", "")
                            path = os.path.join(save_dir, f"frame_{i}_{safe_frame_name}.png")
                            img_cropped.save(path)
                            
                            # Guardar metadatos del frame
                            meta_path = os.path.join(save_dir, f"frame_{i}_{safe_frame_name}.json")
                            with open(meta_path, 'w') as f:
                                json.dump(frames_metadata[i], f, indent=2)
                        
                        from image_utils import create_sprite_sheet
                        sprite_sheet = create_sprite_sheet(processed_frames, columns=len(processed_frames))
                        if sprite_sheet:
                            sprite_sheet.save(os.path.join(save_dir, "sprite_sheet_full.png"))
                            
                    else:
                        # Lógica estándar para otros assets (BATCHING REAL + ASYNC)
                        template = PROMPT_TEMPLATES.get(category, PROMPT_TEMPLATES["default"])
                        # Inyectar adjetivo
                        prompt = template.format(item=item, biome=biome, adjective=biome_adj)
                        
                        # Generar TODAS las variaciones de una vez (Batching)
                        # SDXL procesará esto mucho más rápido que 1 a 1
                        print(f"  > Generando {args.count} variaciones en paralelo...")
                        images, meta = generator.generate(
                            prompt=prompt,
                            num_inference_steps=40, 
                            guidance_scale=6.5,
                            width=1024,
                            height=1024,
                            num_images=args.count, # Batch size real
                            ip_adapter_image=style_image, # Inyectar estilo
                            ip_adapter_scale=args.style_strength # Fuerza del estilo variable
                        )
                        
                        save_dir = os.path.join(args.output, biome, category)
                        ensure_dir(save_dir)
                        
                        # Guardar metadatos generales del batch
                        base_filename = item.replace(' ', '_')
                        batch_meta_path = os.path.join(save_dir, f"{base_filename}_metadata.json")
                        with open(batch_meta_path, 'w') as f:
                            json.dump(meta, f, indent=2)
                        
                        for i, img in enumerate(images):
                            filename = f"{base_filename}_{i+1}.png"
                            save_path = os.path.join(save_dir, filename)
                            
                            # ENVIAR A WORKER (No bloquea el loop principal)
                            executor.submit(process_and_save_image, img, save_path)
                    
                    # No sumamos args.count aquí porque el bucle 'current' es solo visual
                    # pero si queremos mantener la barra de progreso precisa:
                    current += args.count

    print("Generación masiva completada. Esperando a que terminen los procesos de fondo...")
    # El 'with' del executor esperará automáticamente a que terminen las tareas pendientes.

if __name__ == "__main__":
    main()
