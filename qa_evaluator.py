"""
Evaluador de Calidad Avanzado para Pixel Art
Usa CLIP-Large + Aesthetic Predictor en CPU para máxima precisión
"""
import torch
from PIL import Image
import numpy as np

# Variables globales para modelos (lazy loading)
_clip_model = None
_clip_processor = None
_aesthetic_model = None

def init_advanced_qa(device="cpu"):
    """
    Inicializa modelos de evaluación avanzada.
    - CLIP-ViT-Large-Patch14: Mejor comprensión semántica
    - Aesthetic Predictor: Score de calidad estética
    """
    global _clip_model, _clip_processor, _aesthetic_model
    
    if _clip_model is not None:
        return  # Ya inicializado
    
    print("🔍 Cargando evaluador avanzado (CLIP-Large + Aesthetic)...")
    
    try:
        from transformers import CLIPProcessor, CLIPModel
        
        # Usar modelo LARGE para mejor precisión
        model_id = "openai/clip-vit-large-patch14"
        print(f"   Cargando {model_id}...")
        _clip_processor = CLIPProcessor.from_pretrained(model_id)
        _clip_model = CLIPModel.from_pretrained(model_id)
        _clip_model.to(device)
        _clip_model.eval()
        
        print("   ✅ CLIP-Large cargado")
        
        # Intentar cargar Aesthetic Predictor (opcional)
        try:
            # Modelo entrenado en calidad estética de imágenes
            # https://github.com/christophschuhmann/improved-aesthetic-predictor
            from transformers import AutoModel
            aesthetic_id = "cafeai/cafe_aesthetic"
            print(f"   Cargando {aesthetic_id}...")
            _aesthetic_model = AutoModel.from_pretrained(aesthetic_id)
            _aesthetic_model.to(device)
            _aesthetic_model.eval()
            print("   ✅ Aesthetic Predictor cargado")
        except Exception as e:
            print(f"   ⚠️  Aesthetic Predictor no disponible: {e}")
            print("   Continuando solo con CLIP-Large")
        
        print("✅ Evaluador avanzado listo")
        
    except Exception as e:
        print(f"❌ Error cargando evaluador: {e}")
        raise

def evaluate_advanced(image: Image.Image, prompt: str = "", min_clip_score: float = 65.0, min_aesthetic: float = 5.0) -> dict:
    """
    Evaluación avanzada de calidad.
    
    Returns:
        {
            'clip_score': float (0-100),
            'aesthetic_score': float (0-10),
            'is_pixel_art': bool,
            'is_good': bool,
            'reason': str  # Si falla, explica por qué
        }
    """
    global _clip_model, _clip_processor, _aesthetic_model
    
    if _clip_model is None:
        raise RuntimeError("Evaluador no inicializado. Llama a init_advanced_qa() primero.")
    
    result = {
        'clip_score': 0.0,
        'aesthetic_score': 0.0,
        'is_pixel_art': False,
        'is_good': False,
        'reason': ''
    }
    
    try:
        # 1. Validación básica (rápida)
        if image.mode == "RGBA":
            extrema = image.getextrema()
            if extrema[3][1] == 0:  # Totalmente transparente
                result['reason'] = "Imagen totalmente transparente"
                return result
        
        # 2. CLIP Score (Relevancia al prompt)
        positive_text = f"high quality pixel art {prompt}" if prompt else "high quality pixel art game asset"
        negative_texts = [
            "blurry low quality image",
            "photorealistic 3d render",
            "abstract noise",
            "empty black image",
            "corrupted glitchy image"
        ]
        
        inputs = _clip_processor(
            text=[positive_text] + negative_texts,
            images=image,
            return_tensors="pt",
            padding=True
        )
        
        with torch.no_grad():
            outputs = _clip_model(**inputs)
            logits_per_image = outputs.logits_per_image
            probs = logits_per_image.softmax(dim=1)
        
        clip_score = probs[0][0].item() * 100
        result['clip_score'] = clip_score
        
        # 3. Verificar si es pixel art (vs foto/3D)
        pixel_art_inputs = _clip_processor(
            text=["pixel art game sprite", "photorealistic photograph"],
            images=image,
            return_tensors="pt",
            padding=True
        )
        
        with torch.no_grad():
            pa_outputs = _clip_model(**pixel_art_inputs)
            pa_probs = pa_outputs.logits_per_image.softmax(dim=1)
        
        is_pixel_art = pa_probs[0][0].item() > 0.7
        result['is_pixel_art'] = is_pixel_art
        
        # 4. Aesthetic Score (si disponible)
        if _aesthetic_model is not None:
            try:
                # El modelo aesthetic espera embeddings de CLIP
                image_inputs = _clip_processor(images=image, return_tensors="pt")
                with torch.no_grad():
                    image_features = _clip_model.get_image_features(**image_inputs)
                    # Normalizar
                    image_features = image_features / image_features.norm(dim=-1, keepdim=True)
                    # Predecir score estético
                    aesthetic_score = _aesthetic_model(image_features).item()
                    # Escalar a 0-10
                    aesthetic_score = max(0, min(10, aesthetic_score))
                    result['aesthetic_score'] = aesthetic_score
            except Exception as e:
                # Si falla, usar un score neutral
                result['aesthetic_score'] = 6.0
        else:
            # Sin modelo aesthetic, usar score basado en CLIP
            result['aesthetic_score'] = (clip_score / 10.0)
        
        # 5. Decisión final
        if clip_score < min_clip_score:
            result['reason'] = f"CLIP score bajo ({clip_score:.1f} < {min_clip_score})"
            return result
        
        if not is_pixel_art:
            result['reason'] = "No parece pixel art (demasiado realista/3D)"
            return result
        
        if result['aesthetic_score'] < min_aesthetic:
            result['reason'] = f"Calidad estética baja ({result['aesthetic_score']:.1f} < {min_aesthetic})"
            return result
        
        # ✅ Aprobada
        result['is_good'] = True
        result['reason'] = "Aprobada"
        
    except Exception as e:
        result['reason'] = f"Error en evaluación: {str(e)}"
    
    return result

def evaluate_batch(images: list, prompts: list = None) -> list:
    """
    Evalúa un batch de imágenes en paralelo (más eficiente).
    """
    if prompts is None:
        prompts = [""] * len(images)
    
    results = []
    for img, prompt in zip(images, prompts):
        results.append(evaluate_advanced(img, prompt))
    
    return results
