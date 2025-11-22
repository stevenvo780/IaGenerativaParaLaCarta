from pixel_engine import PixelArtGenerator
import time

print("Iniciando prueba de generación...")
start = time.time()
generator = PixelArtGenerator()
generator.load_model()
print(f"Modelo cargado en {time.time() - start:.2f}s")

print("Generando imagen...")
images = generator.generate("pixel art cat", num_inference_steps=20)
print(f"Imagen generada. Tamaño: {images[0].size}")
images[0].save("test_output.png")
print("Guardado en test_output.png")
