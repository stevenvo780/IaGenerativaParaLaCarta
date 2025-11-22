import torch
from diffusers import StableDiffusionXLPipeline, EulerDiscreteScheduler
from PIL import Image

class PixelArtGenerator:
    def __init__(self, model_id: str = "stabilityai/stable-diffusion-xl-base-1.0", device: str = "cuda"):
        self.device = device
        self.model_id = model_id
        self.pipe = None
        # LoRA específico para Pixel Art en SDXL
        self.lora_id = "nerijs/pixel-art-xl"
        
    def load_model(self):
        """Carga el modelo SDXL y el LoRA en memoria."""
        print(f"Cargando modelo SDXL {self.model_id} en {self.device}...")
        
        # Cargar pipeline SDXL
        self.pipe = StableDiffusionXLPipeline.from_pretrained(
            self.model_id, 
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            use_safetensors=True,
            variant="fp16"
        )
        
        # Configurar Scheduler
        self.pipe.scheduler = EulerDiscreteScheduler.from_config(self.pipe.scheduler.config)
        
        # Cargar LoRA
        print(f"Cargando LoRA: {self.lora_id}...")
        self.pipe.load_lora_weights(self.lora_id)
        self.pipe.fuse_lora() # Fusionar para mejor rendimiento
        
        # Revertido a .to(device) por problemas de tipos con Offload
        self.pipe.to(self.device)
        
        # OPTIMIZACIÓN DE MEMORIA CRÍTICA:
        # En lugar de mover todo a GPU (.to("cuda")), usamos CPU Offload.
        # Esto mantiene solo los componentes activos en VRAM.
        # Esencial para SDXL + IP-Adapter en 16GB VRAM.
        # self.pipe.enable_model_cpu_offload()
        
        # Cargar IP-Adapter (Clonación de Estilo)
        self.load_ip_adapter()
        
        # Optimización: Compilar UNet (Solo funciona bien en Linux + Ampere/Ada)
        # DESACTIVADO: Causa OOM en SDXL + LoRA + IP-Adapter con 16GB VRAM
        # try:
        #     print("Optimizando modelo con torch.compile()... (Esto puede tardar un poco la primera vez)")
        #     self.pipe.unet = torch.compile(self.pipe.unet, mode="reduce-overhead", fullgraph=True)
        # except Exception as e:
        #     print(f"Advertencia: No se pudo compilar el modelo: {e}")
            
        print("Modelo SDXL + LoRA cargado exitosamente.")

    def generate(
        self,
        prompt: str,
        negative_prompt: str = "blurry, low quality, photo, realistic, 3d render, multiple objects, grid, collage, text, watermark, signature, cropped, out of frame",
        num_inference_steps: int = 30,
        guidance_scale: float = 7.5,
        width: int = 768, # Reducido de 1024 para evitar OOM con IP-Adapter
        height: int = 768, # Reducido de 1024 para evitar OOM con IP-Adapter
        num_images: int = 1,
        seed: int = None,
        ip_adapter_image = None, # Imagen de referencia para estilo
        ip_adapter_scale: float = 0.6
    ):
        """
        Genera imágenes basadas en el prompt.
        Retorna: (lista_de_imagenes, metadatos_dict)
        """
        if self.pipe is None:
            raise RuntimeError("El modelo no está cargado. Llama a load_model() primero.")
            
        # Trigger word del LoRA suele ser 'pixel art'
        prompt = f"pixel art, {prompt}, sharp, detailed, 8-bit, retro game asset"
        negative_prompt = f"blur, fuzzy, realistic, photo, 3d render, vector, smooth, {negative_prompt}"

        # Gestión de Seed para reproducibilidad
        if seed is None:
            seed = torch.randint(0, 2**32 - 1, (1,)).item()
        
        # Con CPU Offload, es mejor usar un generador en CPU para evitar conflictos de dispositivo
        # o dejar que diffusers maneje el dispositivo si pasamos un int.
        # Pero para reproducibilidad exacta, usamos CPU generator.
        generator = torch.Generator(device="cpu").manual_seed(seed)
            
        # Configurar IP-Adapter scale si se usa
        if ip_adapter_image is not None:
            if hasattr(self.pipe, "set_ip_adapter_scale"): # Check if method exists
                self.pipe.set_ip_adapter_scale(ip_adapter_scale)
            
        kwargs = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "num_inference_steps": num_inference_steps,
            "guidance_scale": guidance_scale,
            "width": width,
            "height": height,
            "num_images_per_prompt": num_images,
            "generator": generator,
        }
        
        if ip_adapter_image is not None:
            kwargs["ip_adapter_image"] = ip_adapter_image
            
        output = self.pipe(**kwargs)
        
        metadata = {
            "prompt": prompt,
            "seed": seed,
            "steps": num_inference_steps,
            "cfg": guidance_scale,
            "width": width,
            "height": height,
            "model": "SDXL 1.0 + Pixel Art LoRA",
            "ip_adapter_scale": ip_adapter_scale if ip_adapter_image else 0.0
        }
        
        return output.images, metadata

    def load_ip_adapter(self):
        """Carga el IP-Adapter para SDXL."""
        try:
            print("Cargando IP-Adapter para SDXL...")
            # Nota: Esto requiere descargar modelos adicionales (~1.2GB)
            # Usamos el modelo oficial de IP-Adapter para SDXL
            # ID correcto: h94/IP-Adapter
            self.pipe.load_ip_adapter("h94/IP-Adapter", subfolder="sdxl_models", weight_name="ip-adapter_sdxl.bin")
            # Nota: La implementación exacta depende de la librería diffusers instalada.
            # En versiones recientes, load_ip_adapter descarga automáticamente.
            print("IP-Adapter cargado.")
        except Exception as e:
            print(f"Error cargando IP-Adapter: {e}")
            print("Continuando sin IP-Adapter.")
