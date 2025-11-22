#!/bin/bash
# Test del Sistema Híbrido - Generar 1 bioma completo

echo "🧪 Test del Sistema Híbrido (Procedural + IA)"
echo "=============================================="
echo ""

source venv/bin/activate

if [ -z "$VIRTUAL_ENV" ]; then
    echo "❌ Error: No se pudo activar el entorno virtual"
    exit 1
fi

echo "✅ Entorno activado"
echo ""

# Configuración de test
BIOME="Forest"
COUNT=3  # Solo 3 variaciones para test rápido
CPU_WORKERS=10  # Menos workers para test

echo "📊 Configuración del Test:"
echo "   - Bioma: $BIOME (solo este)"
echo "   - Categorías: Todas (procedural + IA)"
echo "   - Variaciones: $COUNT"
echo "   - Workers CPU: $CPU_WORKERS"
echo ""
echo "   PROCEDURAL → Terrain, Paths (rápido)"
echo "   IA → Vegetation, Structures, Props, etc."
echo ""

read -p "¿Ejecutar test? (s/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Ss]$ ]]; then
    echo "🚀 Iniciando test híbrido..."
    echo ""
    
    python batch_generator_queue.py \
        --biome $BIOME \
        --count $COUNT \
        --cpu_workers $CPU_WORKERS \
        --min_clip_score 70.0 \
        --min_aesthetic 6.0
    
    EXIT_CODE=$?
    
    echo ""
    if [ $EXIT_CODE -eq 0 ]; then
        echo "✅ Test completado!"
        echo "📁 Revisa: output_assets/$BIOME/"
        echo ""
        echo "Verifica que:"
        echo "  - Terrain/ tenga tiles perfectamente tileables"
        echo "  - Paths/ tenga caminos seamless"
        echo "  - Vegetation/ tenga assets generados por IA"
    else
        echo "❌ Error en el test"
    fi
else
    echo "❌ Cancelado"
fi
