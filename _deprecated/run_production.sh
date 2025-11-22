#!/bin/bash
# Script de Producción Masiva - Pixel Art AI Forge
# Este script activa el entorno virtual y ejecuta la generación completa

echo "🎨 Pixel Art AI Forge - Producción Masiva con QA"
echo "================================================"
echo ""

# Activar entorno virtual
source venv/bin/activate

# Verificar que está activado
if [ -z "$VIRTUAL_ENV" ]; then
    echo "❌ Error: No se pudo activar el entorno virtual"
    exit 1
fi

echo "✅ Entorno virtual activado: $VIRTUAL_ENV"
echo ""

# Configuración
COUNT=10  # 10 variaciones por item para máxima variedad
STYLE_STRENGTH=0.6

echo "📊 Configuración:"
echo "   - Variaciones por item: $COUNT"
echo "   - Fuerza de estilo: $STYLE_STRENGTH"
echo "   - Resolución: 768x768"
echo "   - Biomas: 10"
echo "   - Categorías: Todas"
echo "   - QA con IA: ✅ ACTIVADO (CLIP en CPU)"
echo "   - Paleta: 32 colores"
echo "   - Outline: 1px negro"
echo ""
echo "⏱️  Tiempo estimado: 12-24 horas (con QA es más lento pero mejor calidad)"
echo ""

read -p "¿Continuar con la generación masiva? (s/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Ss]$ ]]; then
    echo "🚀 Iniciando producción en PRIMER PLANO..."
    echo "   (Verás todo el progreso en tiempo real)"
    echo ""
    
    # Ejecutar en FOREGROUND (sin nohup ni &) para ver progreso en tiempo real
    # Con QA activado para filtrar automáticamente imágenes de baja calidad
    python batch_generator.py --count $COUNT --style_strength $STYLE_STRENGTH --use_clip_qa
    
    echo ""
    echo "✅ Generación completada!"
    echo "📁 Revisa: output_assets/"
else
    echo "❌ Cancelado por el usuario"
    exit 0
fi
