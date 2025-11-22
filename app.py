import gradio as gr
from pixel_engine import PixelArtGenerator
from image_utils import remove_background, pixelate, create_sprite_sheet

# Inicializar generador (carga perezosa al primer uso o al iniciar)
generator = PixelArtGenerator()

def generate_images(prompt, neg_prompt, steps, cfg, count, w, h):
    return generator.generate(prompt, neg_prompt, steps, cfg, w, h, count)

def process_image(image, pixel_size, do_remove_bg):
    if image is None:
        return None
    
    processed = image
    
    if pixel_size > 1:
        processed = pixelate(processed, int(pixel_size))
        
    if do_remove_bg:
        processed = remove_background(processed)
        
    return processed

def make_sheet(files, cols):
    # files es una lista de rutas temporales o objetos file de gradio
    images = []
    if files:
        for f in files:
            # Gradio pasa rutas de archivos en 'files' si se usa file_count="multiple" en un componente File
            # O una lista de imágenes si se usa Gallery? Depende del input.
            # Vamos a asumir que usamos una Gallery de salida como input para esto, o subida de archivos.
            # Para simplificar, usaremos subida de archivos por ahora.
            pass
    return None # Placeholder

# Definición de la UI
with gr.Blocks(title="Pixel Art AI Forge", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🎨 Pixel Art AI Forge")
    gr.Markdown("Genera assets de pixel art, personajes y texturas para tu juego usando tu GPU.")
    
    with gr.Tab("Generación"):
        with gr.Row():
            with gr.Column(scale=1):
                prompt_input = gr.Textbox(label="Prompt", placeholder="Ej: warrior character, sword, shield, fantasy")
                neg_prompt_input = gr.Textbox(label="Negative Prompt", value="blur, low quality")
                
                with gr.Accordion("Configuración Avanzada", open=False):
                    steps_slider = gr.Slider(minimum=10, maximum=100, value=30, step=1, label="Pasos de Inferencia")
                    cfg_slider = gr.Slider(minimum=1, maximum=20, value=7.5, step=0.5, label="Guidance Scale")
                    width_slider = gr.Slider(minimum=256, maximum=1024, value=512, step=64, label="Ancho")
                    height_slider = gr.Slider(minimum=256, maximum=1024, value=512, step=64, label="Alto")
                    batch_slider = gr.Slider(minimum=1, maximum=4, value=1, step=1, label="Cantidad de Imágenes")
                
                gen_btn = gr.Button("Generar", variant="primary")
                
            with gr.Column(scale=2):
                gallery_output = gr.Gallery(label="Resultados", columns=2, height="auto")
                
        gen_btn.click(
            generate_images,
            inputs=[prompt_input, neg_prompt_input, steps_slider, cfg_slider, batch_slider, width_slider, height_slider],
            outputs=[gallery_output]
        )

    with gr.Tab("Procesamiento"):
        with gr.Row():
            with gr.Column():
                img_input = gr.Image(label="Imagen de Entrada", type="pil")
                pixel_size_slider = gr.Slider(minimum=1, maximum=32, value=1, step=1, label="Factor de Pixelado (1 = Original)")
                remove_bg_checkbox = gr.Checkbox(label="Eliminar Fondo", value=True)
                process_btn = gr.Button("Procesar")
            
            with gr.Column():
                img_output = gr.Image(label="Imagen Procesada", type="pil")
        
        process_btn.click(
            process_image,
            inputs=[img_input, pixel_size_slider, remove_bg_checkbox],
            outputs=[img_output]
        )

    with gr.Tab("Sprite Sheet"):
        gr.Markdown("Sube varias imágenes para crear un Sprite Sheet.")
        with gr.Row():
            with gr.Column():
                sheet_files = gr.File(file_count="multiple", label="Subir Sprites (PNG/JPG)", type="filepath")
                cols_slider = gr.Slider(minimum=1, maximum=10, value=4, step=1, label="Columnas")
                sheet_btn = gr.Button("Crear Sprite Sheet")
            
            with gr.Column():
                sheet_output = gr.Image(label="Sprite Sheet Resultante")
        
        def process_sheet(file_paths, columns):
            if not file_paths:
                return None
            from PIL import Image
            imgs = [Image.open(f) for f in file_paths]
            return create_sprite_sheet(imgs, int(columns))

        sheet_btn.click(
            process_sheet,
            inputs=[sheet_files, cols_slider],
            outputs=[sheet_output]
        )

if __name__ == "__main__":
    demo.launch(share=False)
