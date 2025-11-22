#!/bin/bash
# PIXEL ART AI FORGE V7.0 - Look Pixel Art Auténtico
# Sistema Híbrido + Post-Procesado Pixelado Agresivo

echo "🎨 PIXEL ART AI FORGE V7.0 - Look Auténtico"
echo "============================================"
echo ""

source venv/bin/activate

if [ -z "$VIRTUAL_ENV" ]; then
    echo "❌ Error: No se pudo activar el entorno virtual"
    exit 1
fi

echo "✅ Entorno virtual activado"
echo ""

# Configuración OPTIMIZADA para pixel art auténtico
COUNT=10
STYLE_STRENGTH=0.6
CPU_WORKERS=30
MIN_CLIP_SCORE=70.0
MIN_AESTHETIC=6.0
MAX_RETRIES=3
PIXEL_SIZE=64      # Pixelado agresivo (64=muy pixelado, 128=moderado)
PALETTE_SIZE=16    # Paleta retro (16=NES, 4=Gameboy, 32=SNES)
SAVE_RAW=true      # Guardar versiones RAW para debug

echo "📊 Mejoras para Look Pixel Art Auténtico:"
echo "   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   Generación:"
echo "     • Resolución: 512x512 (reducida para pixelado)"
echo "     • LoRA Weight: 1.0 (máximo estilo pixel art)"
echo "     • Prompts: 16-bit sprite, gameboy style, crisp pixels"
echo ""
echo "   Post-Procesado Agresivo:"
echo "     • Pixelado: $PIXEL_SIZE px (downscale → paleta → upscale)"
echo "     • Paleta: $PALETTE_SIZE colores (look retro)"
echo "     • Remove BG: Pixel-safe (preserva píxeles)"
echo "     • Outline: 1px negro (opcional)"
echo ""
echo "   QA Estricto:"
echo "     • CLIP Score ≥ $MIN_CLIP_SCORE/100"
echo "     • Aesthetic Score ≥ $MIN_AESTHETIC/10"
echo "     • Auto-retry: Hasta $MAX_RETRIES intentos"
echo ""
echo "   Debugging:"
echo "     • Guardar RAW: Sí (carpeta raw/)"
echo ""
echo "   Variaciones: $COUNT por asset"
echo "   Biomas: 10"
echo "   Total estimado: ~10,000 assets"
echo ""
echo "⏱️  Tiempo estimado: 8-14 horas"
echo ""

read -p "¿Iniciar producción con look pixel art mejorado? (s/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Ss]$ ]]; then
    echo "🎨 Iniciando generación..."
    echo ""
    
    python batch_generator_queue.py \
        --count $COUNT \
        --style_strength $STYLE_STRENGTH \
        --cpu_workers $CPU_WORKERS \
        --min_clip_score $MIN_CLIP_SCORE \
        --min_aesthetic $MIN_AESTHETIC \
        --max_retries $MAX_RETRIES \
        --pixel_size $PIXEL_SIZE \
        --palette_size $PALETTE_SIZE \
        --save_raw
    
    EXIT_CODE=$?
    
    echo ""
    if [ $EXIT_CODE -eq 0 ]; then
        echo "✅ Generación completada!"
        echo "📁 Assets procesados: output_assets/"
        echo "📁 Versiones RAW: output_assets/*/raw/"
        echo ""
        echo "💡 Compara RAW vs procesadas para ajustar parámetros"
    else
        echo "❌ Error (código: $EXIT_CODE)"
    fi
else
    echo "❌ Cancelado"
    exit 0
fi
