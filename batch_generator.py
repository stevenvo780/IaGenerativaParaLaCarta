import argparse
import os
import torch
import concurrent.futures
from PIL import Image
import gc
import json
from pixel_engine import PixelArtGenerator
from image_utils import (
    remove_background, 
    crop_to_content, 
    create_sprite_sheet, 
    quantize_colors, 
    add_pixel_outline, 
    create_gif, 
    validate_image
)
from assets_config import BIOMES, ASSETS, PROMPT_TEMPLATES, BIOME_ADJECTIVES
from PIL import Image

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def process_and_save_image(image, save_path, apply_quantize=True, apply_outline=True):
    """Función worker para procesar y guardar imágenes en segundo plano."""
    try:
        # 0. QA Básico
        if not validate_image(image):
            print(f"Skipping invalid image: {save_path}")
            return

        # 1. Quitar fondo
        img_no_bg = remove_background(image)
        
        # 2. Recorte automático
        img_cropped = crop_to_content(img_no_bg)
        
        # 3. Cuantización de Color (Paleta)
        if apply_quantize:
            img_cropped = quantize_colors(img_cropped, num_colors=32)
            
        # 4. Outline (Borde)
        if apply_outline:
            img_cropped = add_pixel_outline(img_cropped, color=(0,0,0), thickness=1)
            
        # 5. Guardar
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
    parser.add_argument("--no_quantize", action="store_true", help="Desactivar reducción de paleta")
    parser.add_argument("--no_outline", action="store_true", help="Desactivar borde negro")
    
    args = parser.parse_args()
    
    # Lógica inversa para flags negativos
    apply_quantize = not args.no_quantize
    apply_outline = not args.no_outline
    
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
    print(f"Mejoras activas: Paleta={apply_quantize}, Outline={apply_outline}")
    
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
                                width=768, # Reducido para estabilidad
                                height=768, # Reducido para estabilidad
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
                            # Procesado manual aquí para poder usar los frames procesados en el GIF/SpriteSheet
                            if not validate_image(img): continue
                            
                            img_no_bg = remove_background(img)
                            img_cropped = crop_to_content(img_no_bg)
                            
                            if apply_quantize:
                                img_cropped = quantize_colors(img_cropped, num_colors=32)
                            if apply_outline:
                                img_cropped = add_pixel_outline(img_cropped)
                                
                            processed_frames.append(img_cropped)
                            
                            safe_frame_name = frame_name.replace(" ", "_").replace(",", "")
                            path = os.path.join(save_dir, f"frame_{i}_{safe_frame_name}.png")
                            img_cropped.save(path)
                            
                            # Guardar metadatos del frame
                            meta_path = os.path.join(save_dir, f"frame_{i}_{safe_frame_name}.json")
                            with open(meta_path, 'w') as f:
                                json.dump(frames_metadata[i], f, indent=2)
                        
                        # Crear Sprite Sheet
                        from image_utils import create_sprite_sheet
                        sprite_sheet = create_sprite_sheet(processed_frames, columns=len(processed_frames))
                        if sprite_sheet:
                            sprite_sheet.save(os.path.join(save_dir, "sprite_sheet_full.png"))
                            
                        # Crear GIF Animado (NUEVO)
                        if processed_frames:
                            gif_path = os.path.join(save_dir, "animation_preview.gif")
                            create_gif(processed_frames, gif_path, duration=200, loop=0)
                            
                    else:
                        # Lógica estándar para otros assets
                        template = PROMPT_TEMPLATES.get(category, PROMPT_TEMPLATES["default"])
                        # Inyectar adjetivo
                        prompt = template.format(item=item, biome=biome, adjective=biome_adj)
                        
                        save_dir = os.path.join(args.output, biome, category)
                        ensure_dir(save_dir)
                        base_filename = item.replace(' ', '_')
                        
                        # GENERAR DE A 1 para evitar OOM (en lugar de batch)
                        # Aunque es más lento, es más estable con IP-Adapter
                        for variation_idx in range(args.count):
                            print(f"  > Generando variación {variation_idx+1}/{args.count}...")
                            
                            images, meta = generator.generate(
                                prompt=prompt,
                                num_inference_steps=40, 
                                guidance_scale=6.5,
                                width=768,
                                height=768,
                                num_images=1, # Solo 1 imagen a la vez
                                ip_adapter_image=style_image,
                                ip_adapter_scale=args.style_strength
                            )
                            
                            # Guardar metadatos de esta variación
                            meta_path = os.path.join(save_dir, f"{base_filename}_{variation_idx+1}_metadata.json")
                            with open(meta_path, 'w') as f:
                                json.dump(meta, f, indent=2)
                            
                            # Procesar y guardar (con argumentos de mejoras)
                            filename = f"{base_filename}_{variation_idx+1}.png"
                            save_path = os.path.join(save_dir, filename)
                            executor.submit(process_and_save_image, images[0], save_path, apply_quantize, apply_outline)
                            
                            # Limpiar memoria después de cada imagen
                            if variation_idx % 5 == 0:  # Cada 5 imágenes
                                gc.collect()
                                torch.cuda.empty_cache()
                    
                    current += args.count

    print("Generación masiva completada. Esperando a que terminen los procesos de fondo...")
    # El 'with' del executor esperará automáticamente a que terminen las tareas pendientes.

if __name__ == "__main__":
    main()
