import torch
import time
import subprocess
from pixel_engine import PixelArtGenerator
import psutil
import os

def get_gpu_memory():
    try:
        # Usamos query-gpu con csv format. Debería retornar "used, total"
        result = subprocess.check_output(
            ['nvidia-smi', '--query-gpu=memory.used,memory.total', '--format=csv,nounits,noheader'],
            encoding='utf-8'
        )
        # Limpiar espacios y saltos de línea
        lines = result.strip().split('\n')
        if not lines: return 0, 0
        
        # Tomar la primera GPU (si hay varias)
        parts = lines[0].split(',')
        used = int(parts[0].strip())
        total = int(parts[1].strip())
        return used, total
    except Exception as e:
        print(f"Error leyendo nvidia-smi: {e}")
        return 0, 0

def log_resources(stage):
    cpu_percent = psutil.cpu_percent()
    ram_percent = psutil.virtual_memory().percent
    gpu_used, gpu_total = get_gpu_memory()
    torch_allocated = torch.cuda.memory_allocated() / 1024**2 if torch.cuda.is_available() else 0
    
    print(f"[{stage}]")
    print(f"  CPU: {cpu_percent}% | RAM: {ram_percent}%")
    print(f"  GPU VRAM (System): {gpu_used}/{gpu_total} MB")
    print(f"  Torch Allocated: {torch_allocated:.2f} MB")
    print("-" * 40)

def main():
    print("=== INICIANDO DIAGNÓSTICO DE GPU ===")
    log_resources("Inicio")
    
    try:
        print("1. Inicializando Generador...")
        start_load = time.time()
        generator = PixelArtGenerator()
        generator.load_model()
        load_time = time.time() - start_load
        print(f"Modelo cargado en {load_time:.2f}s")
        log_resources("Modelo Cargado")
        
        print("2. Generando Imagen Única (1024x1024)...")
        start_gen = time.time()
        
        # Generamos 1 sola imagen para probar
        images = generator.generate(
            prompt="pixel art diagnostic test, simple cube",
            num_inference_steps=20, # Reducido ligeramente para test rápido
            width=1024,
            height=1024,
            num_images=1
        )
        
        gen_time = time.time() - start_gen
        print(f"Generación completada en {gen_time:.2f}s")
        log_resources("Post-Generación")
        
        if images and images[0]:
            images[0].save("diagnostic_output.png")
            print("Imagen guardada exitosamente: diagnostic_output.png")
        else:
            print("ERROR: La lista de imágenes está vacía o es None")
            
    except torch.cuda.OutOfMemoryError:
        print("\n!!! CRITICAL ERROR: CUDA OUT OF MEMORY !!!")
        log_resources("CRASH OOM")
        print("Sugerencia: Habilitar model_cpu_offload o reducir resolución.")
    except Exception as e:
        print(f"\n!!! ERROR NO ESPERADO: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("=== DIAGNÓSTICO FINALIZADO ===")

if __name__ == "__main__":
    main()
