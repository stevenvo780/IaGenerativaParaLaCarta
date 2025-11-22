#!/bin/bash
# Test FINAL - Fondo blanco + Remove solo blanco puro

echo "🧪 Test FINAL - Optimizaciones Completas"
echo "========================================"
echo ""

source venv/bin/activate

echo "📊 Mejoras aplicadas:"
echo "   ✅ Prompt: 'plain white background, pure white background'"
echo "   ✅ Remove BG: SOLO blanco puro (255,255,255)"
echo "   ✅ NO recortar (preservar imagen completa)"
echo "   ✅ Pixelar: 64px, 16 colores"
echo ""

read -p "¿Ejecutar test final? (s/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Ss]$ ]]; then
    # Limpiar output anterior
    rm -rf output_assets/Forest/Vegetation/*.png
    rm -rf output_assets/Forest/Vegetation/raw/*.png
    
    echo "🚀 Generando con todas las optimizaciones..."
    echo ""
    
    python batch_generator_queue.py \
        --biome Forest \
        --category Vegetation \
        --count 2 \
        --cpu_workers 10 \
        --min_clip_score 70.0 \
        --min_aesthetic 6.0 \
        --pixel_size 64 \
        --palette_size 16 \
        --save_raw
    
    echo ""
    echo "✅ Test completado!"
    echo ""
    echo "📁 Compara:"
    echo "   RAW:       output_assets/Forest/Vegetation/raw/"
    echo "   Procesada: output_assets/Forest/Vegetation/"
    echo ""
    echo "💡 Debería verse perfecto ahora:"
    echo "   - Fondo blanco puro → transparente"
    echo "   - Colores claros → preservados"
    echo "   - Imagen completa → sin recortar"
    echo "   - Look pixel art → 16 colores, píxeles nítidos"
else
    echo "❌ Cancelado"
fi
