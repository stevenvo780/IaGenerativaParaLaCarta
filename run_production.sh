#!/bin/bash
# Script de Producción Masiva - Pixel Art AI Forge
# Este script activa el entorno virtual y ejecuta la generación completa

echo "🎨 Pixel Art AI Forge - Producción Masiva"
echo "=========================================="
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
COUNT=3  # Reducido a 3 variaciones por item para evitar OOM
STYLE_STRENGTH=0.6

echo "📊 Configuración:"
echo "   - Variaciones por item: $COUNT"
echo "   - Fuerza de estilo: $STYLE_STRENGTH"
echo "   - Resolución: 768x768"
echo "   - Biomas: 10"
echo "   - Categorías: Todas"
echo ""
echo "⏱️  Tiempo estimado: Varias horas"
echo ""

read -p "¿Continuar con la generación masiva? (s/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Ss]$ ]]; then
    echo "🚀 Iniciando producción..."
    echo ""
    
    # Ejecutar con nohup para que continúe en background
    nohup python batch_generator.py --count $COUNT --style_strength $STYLE_STRENGTH > production.log 2>&1 &
    
    PID=$!
    echo "✅ Proceso iniciado en background (PID: $PID)"
    echo "📝 Log: production.log"
    echo ""
    echo "Comandos útiles:"
    echo "  - Ver progreso: tail -f production.log"
    echo "  - Ver proceso: ps aux | grep $PID"
    echo "  - Detener: kill $PID"
    echo ""
else
    echo "❌ Cancelado por el usuario"
    exit 0
fi
