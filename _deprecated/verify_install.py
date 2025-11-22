import torch
import diffusers
import rembg
import gradio

print(f"Torch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"CUDA device: {torch.cuda.get_device_name(0)}")
print(f"Diffusers version: {diffusers.__version__}")
print(f"Rembg version: {rembg.__version__}")
print(f"Gradio version: {gradio.__version__}")
