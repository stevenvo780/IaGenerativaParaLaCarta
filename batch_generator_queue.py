"""
Generador Masivo con Sistema de Colas Retroalimentativo
GPU genera → CPU evalúa en paralelo → Auto-retry si falla QA
"""
import argparse
import os
import torch
import multiprocessing as mp
from multiprocessing import Queue, Process, Manager
import queue
import time
from PIL import Image
import gc
import json

from pixel_engine import PixelArtGenerator
from image_utils import remove_background, crop_to_content, quantize_colors, add_pixel_outline, create_gif, create_sprite_sheet
from qa_evaluator import init_advanced_qa, evaluate_advanced
from assets_config import BIOMES, ASSETS, PROMPT_TEMPLATES, BIOME_ADJECTIVES, CHARACTER_FRAMES

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def process_and_save_worker(task_queue, results_queue, apply_quantize, apply_outline, min_clip_score, min_aesthetic):
    """
    Worker CPU: Procesa y evalúa imágenes en paralelo.
    Si falla QA, envía señal para re-encolar.
    """
    # Inicializar evaluador en este proceso
    init_advanced_qa(device="cpu")
    
    while True:
        try:
            task = task_queue.get(timeout=5)
            if task is None:  # Señal de terminación
                break
            
            image = task['image']
            save_path = task['save_path']
            prompt = task['prompt']
            metadata = task['metadata']
            task_id = task['task_id']
            
            # 1. Evaluación con IA
            qa_result = evaluate_advanced(image, prompt, min_clip_score, min_aesthetic)
            
            if not qa_result['is_good']:
                # ❌ Falló QA - Enviar señal de retry
                print(f"   ❌ QA FAIL: {task_id} - {qa_result['reason']}")
                results_queue.put({
                    'status': 'retry',
                    'task_id': task_id,
                    'reason': qa_result['reason']
                })
                continue
            
            # ✅ Aprobada - Procesar y guardar
            print(f"   ✅ QA PASS: {task_id} (CLIP: {qa_result['clip_score']:.1f}, Aesthetic: {qa_result['aesthetic_score']:.1f})")
            
            # 2. Procesamiento
            img_no_bg = remove_background(image)
            img_cropped = crop_to_content(img_no_bg)
            
            if apply_quantize:
                img_cropped = quantize_colors(img_cropped, num_colors=32)
            if apply_outline:
                img_cropped = add_pixel_outline(img_cropped)
            
            # 3. Guardar imagen
            img_cropped.save(save_path)
            
            # 4. Guardar metadata (con scores de QA)
            metadata['qa_scores'] = {
                'clip_score': qa_result['clip_score'],
                'aesthetic_score': qa_result['aesthetic_score'],
                'is_pixel_art': qa_result['is_pixel_art']
            }
            
            meta_dir = os.path.join(os.path.dirname(save_path), "metadata")
            ensure_dir(meta_dir)
            meta_filename = os.path.basename(save_path).replace('.png', '.json')
            meta_path = os.path.join(meta_dir, meta_filename)
            
            with open(meta_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # 5. Notificar éxito
            results_queue.put({
                'status': 'success',
                'task_id': task_id,
                'save_path': save_path
            })
            
        except queue.Empty:
            continue
        except Exception as e:
            print(f"Error en worker: {e}")
            if 'task_id' in locals():
                results_queue.put({
                    'status': 'error',
                    'task_id': task_id,
                    'reason': str(e)
                })

def main():
    parser = argparse.ArgumentParser(description="Generador con Colas Retroalimentativas")
    parser.add_argument("--output", type=str, default="output_assets", help="Carpeta de salida")
    parser.add_argument("--biome", type=str, default="all", help="Bioma específico o 'all'")
    parser.add_argument("--category", type=str, default="all", help="Categoría específica o 'all'")
    parser.add_argument("--count", type=int, default=10, help="Número de variaciones por asset")
    parser.add_argument("--style_strength", type=float, default=0.6, help="Fuerza del estilo IP-Adapter")
    parser.add_argument("--no_quantize", action="store_true", help="Desactivar paleta")
    parser.add_argument("--no_outline", action="store_true", help="Desactivar outline")
    parser.add_argument("--min_clip_score", type=float, default=70.0, help="Score mínimo CLIP (0-100)")
    parser.add_argument("--min_aesthetic", type=float, default=6.0, help="Score mínimo estético (0-10)")
    parser.add_argument("--max_retries", type=int, default=3, help="Máximo de reintentos por imagen")
    parser.add_argument("--cpu_workers", type=int, default=30, help="Workers CPU para evaluación")
    
    args = parser.parse_args()
    
    apply_quantize = not args.no_quantize
    apply_outline = not args.no_outline
    
    ensure_dir(args.output)
    
    print("🚀 Iniciando Generador con Colas Retroalimentativas")
    print(f"   GPU: Generación continua")
    print(f"   CPU: {args.cpu_workers} workers evaluando en paralelo")
    print(f"   QA: CLIP ≥ {args.min_clip_score}, Aesthetic ≥ {args.min_aesthetic}")
    print(f"   Retries: Máximo {args.max_retries} por imagen")
    print("")
    
    # Cargar generador (GPU)
    generator = PixelArtGenerator()
    generator.load_model()
    
    # Cargar estilo
    style_image = None
    if os.path.exists("style_reference.png"):
        style_image = Image.open("style_reference.png").convert("RGB")
        print(f"✅ Estilo cargado (fuerza: {args.style_strength})")
    
    # Preparar biomas y categorías
    biomes_to_process = BIOMES if args.biome == "all" else [args.biome]
    categories_to_process = ASSETS.keys() if args.category == "all" else [args.category]
    
    # Crear colas
    task_queue = Queue(maxsize=200)  # Cola de procesamiento
    results_queue = Queue()
    
    # Iniciar workers CPU
    print(f"🔧 Iniciando {args.cpu_workers} workers CPU...")
    workers = []
    for _ in range(args.cpu_workers):
        p = Process(
            target=process_and_save_worker,
            args=(task_queue, results_queue, apply_quantize, apply_outline, args.min_clip_score, args.min_aesthetic)
        )
        p.start()
        workers.append(p)
    
    print("✅ Workers listos\n")
    
    # Tracking
    manager = Manager()
    pending_tasks = manager.dict()  # {task_id: {retry_count, ...}}
    completed_count = manager.Value('i', 0)
    total_generated = manager.Value('i', 0)
    
    # Loop principal de generación
    for biome in biomes_to_process:
        gc.collect()
        torch.cuda.empty_cache()
        print(f"--- Bioma: {biome} ---")
        
        biome_adj = BIOME_ADJECTIVES.get(biome, "")
        
        for category in categories_to_process:
            if category not in ASSETS:
                continue
            
            items = ASSETS[category]
            for item in items:
                print(f"\n📦 {item} ({biome})")
                
                # Manejo especial para Characters (con frames de animación)
                if category == "Characters":
                    # Generar cada frame del personaje
                    for frame_idx, frame_desc in enumerate(CHARACTER_FRAMES):
                        task_id = f"{biome}_{category}_{item}_frame{frame_idx}"
                        
                        pending_tasks[task_id] = {
                            'retry_count': 0,
                            'biome': biome,
                            'category': category,
                            'item': item,
                            'frame_idx': frame_idx
                        }
                        
                        # Generar imagen del frame
                        template = PROMPT_TEMPLATES.get("Characters")
                        prompt = template.format(item=item, biome=biome, frame=frame_desc)
                        
                        print(f"  🎨 Generando frame {frame_idx+1}/{len(CHARACTER_FRAMES)}: {frame_desc[:30]}...")
                        
                        images, meta = generator.generate(
                            prompt=prompt,
                            num_inference_steps=50,  # Aumentado para mejor calidad
                            guidance_scale=7.5,      # Más fiel al prompt
                            width=768,
                            height=768,
                            num_images=1,
                            ip_adapter_image=style_image,
                            ip_adapter_scale=args.style_strength
                        )
                        
                        total_generated.value += 1
                        
                        # Preparar tarea para evaluación
                        save_dir = os.path.join(args.output, biome, category, item.replace(" ", "_"))
                        ensure_dir(save_dir)
                        safe_frame_name = frame_desc.replace(" ", "_").replace(",", "")
                        filename = f"frame_{frame_idx}_{safe_frame_name}.png"
                        save_path = os.path.join(save_dir, filename)
                        
                        task = {
                            'task_id': task_id,
                            'image': images[0],
                            'save_path': save_path,
                            'prompt': prompt,
                            'metadata': meta
                        }
                        
                        # Encolar para evaluación
                        task_queue.put(task)
                        
                        # Procesar resultados mientras generamos
                        while not results_queue.empty():
                            result = results_queue.get_nowait()
                            result_task_id = result['task_id']
                            
                            if result['status'] == 'success':
                                completed_count.value += 1
                                if result_task_id in pending_tasks:
                                    del pending_tasks[result_task_id]
                                
                            elif result['status'] == 'retry':
                                task_info = pending_tasks.get(result_task_id)
                                if task_info:
                                    task_info['retry_count'] += 1
                                    
                                    if task_info['retry_count'] < args.max_retries:
                                        print(f"  🔄 Retry {task_info['retry_count']}/{args.max_retries}: {result_task_id}")
                                        # TODO: Re-generar
                                    else:
                                        print(f"  ⚠️  Max retries alcanzado: {result_task_id}")
                                        del pending_tasks[result_task_id]
                    
                    # TODO: Generar sprite sheet y GIF para el personaje
                    
                else:
                    # Generar variaciones para otros assets
                    for var_idx in range(args.count):
                        task_id = f"{biome}_{category}_{item}_{var_idx}"
                        
                        # Inicializar tracking
                        pending_tasks[task_id] = {
                            'retry_count': 0,
                            'biome': biome,
                            'category': category,
                            'item': item,
                            'var_idx': var_idx
                        }
                        
                        # Generar imagen
                        template = PROMPT_TEMPLATES.get(category, PROMPT_TEMPLATES["default"])
                        prompt = template.format(item=item, biome=biome, adjective=biome_adj)
                        
                        print(f"  🎨 Generando variación {var_idx+1}/{args.count}...")
                        
                        images, meta = generator.generate(
                            prompt=prompt,
                            num_inference_steps=50,  # Aumentado para mejor calidad
                            guidance_scale=7.5,      # Más fiel al prompt
                            width=768,
                            height=768,
                            num_images=1,
                            ip_adapter_image=style_image,
                            ip_adapter_scale=args.style_strength
                        )
                        
                        total_generated.value += 1
                        
                        # Preparar tarea para evaluación
                        save_dir = os.path.join(args.output, biome, category)
                        ensure_dir(save_dir)
                        filename = f"{item.replace(' ', '_')}_{var_idx+1}.png"
                        save_path = os.path.join(save_dir, filename)
                        
                        task = {
                            'task_id': task_id,
                            'image': images[0],
                            'save_path': save_path,
                            'prompt': prompt,
                            'metadata': meta
                        }
                        
                        # Encolar para evaluación
                        task_queue.put(task)
                        
                        # Procesar resultados mientras generamos
                        while not results_queue.empty():
                            result = results_queue.get_nowait()
                            result_task_id = result['task_id']
                            
                            if result['status'] == 'success':
                                completed_count.value += 1
                                if result_task_id in pending_tasks:
                                    del pending_tasks[result_task_id]
                                
                            elif result['status'] == 'retry':
                                task_info = pending_tasks.get(result_task_id)
                                if task_info:
                                    task_info['retry_count'] += 1
                                    
                                    if task_info['retry_count'] < args.max_retries:
                                        print(f"  🔄 Retry {task_info['retry_count']}/{args.max_retries}: {result_task_id}")
                                        # TODO: Re-generar
                                    else:
                                        print(f"  ⚠️  Max retries alcanzado: {result_task_id}")
                                        del pending_tasks[result_task_id]
                
                # Limpiar memoria cada item
                if total_generated.value % 10 == 0:
                    gc.collect()
                    torch.cuda.empty_cache()
    
    # Esperar a que se procesen todas las tareas pendientes
    print("\n⏳ Esperando a que terminen las evaluaciones...")
    while len(pending_tasks) > 0:
        time.sleep(1)
        while not results_queue.empty():
            result = results_queue.get_nowait()
            if result['status'] == 'success':
                completed_count.value += 1
                if result['task_id'] in pending_tasks:
                    del pending_tasks[result['task_id']]
    
    # Terminar workers
    print("🛑 Terminando workers...")
    for _ in range(args.cpu_workers):
        task_queue.put(None)
    
    for w in workers:
        w.join()
    
    print(f"\n✅ Generación completada!")
    print(f"   Total generadas: {total_generated.value}")
    print(f"   Total guardadas: {completed_count.value}")
    print(f"   Tasa de aprobación: {(completed_count.value/total_generated.value*100):.1f}%")

if __name__ == "__main__":
    # Necesario para multiprocessing en algunos sistemas
    mp.set_start_method('spawn', force=True)
    main()
