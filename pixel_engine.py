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
        
        self.pipe.to(self.device)
        print("Modelo SDXL + LoRA cargado exitosamente.")

    def generate(
        self, 
        prompt: str, 
        negative_prompt: str = "", 
        num_inference_steps: int = 30, 
        guidance_scale: float = 7.0, # SDXL suele usar valores menores que SD1.5
        width: int = 1024, # Resolución nativa de SDXL
        height: int = 1024,
        num_images: int = 1
    ) -> list[Image.Image]:
        """Genera imágenes basadas en el prompt usando SDXL."""
        if self.pipe is None:
            self.load_model()
            
        # Trigger word del LoRA suele ser 'pixel art'
        enhanced_prompt = f"pixel art, {prompt}, sharp, detailed, 8-bit, retro game asset"
        enhanced_negative = f"blur, fuzzy, realistic, photo, 3d render, vector, smooth, {negative_prompt}"
        
        images = self.pipe(
            prompt=enhanced_prompt,
            negative_prompt=enhanced_negative,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            width=width,
            height=height,
            num_images_per_prompt=num_images
        ).images
        
        return images
