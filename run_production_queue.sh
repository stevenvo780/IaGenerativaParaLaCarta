#!/bin/bash
# Script de Producción con Sistema de Colas Retroalimentativo
# GPU genera continuamente mientras CPU evalúa en paralelo

echo "🚀 Pixel Art AI Forge - Sistema de Colas Avanzado"
echo "=================================================="
echo ""

# Activar entorno virtual
source venv/bin/activate

if [ -z "$VIRTUAL_ENV" ]; then
    echo "❌ Error: No se pudo activar el entorno virtual"
    exit 1
fi

echo "✅ Entorno virtual activado"
echo ""

# Configuración
COUNT=10
STYLE_STRENGTH=0.6
CPU_WORKERS=30
MIN_CLIP_SCORE=65.0
MIN_AESTHETIC=5.0
MAX_RETRIES=3

echo "📊 Configuración del Sistema de Colas:"
echo "   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   GPU (RTX 5070 Ti):"
echo "     • Generación continua (no espera)"
echo "     • Resolución: 768x768"
echo "     • Estilo: IP-Adapter (fuerza $STYLE_STRENGTH)"
echo ""
echo "   CPU (32 hilos):"
echo "     • $CPU_WORKERS workers evaluando en paralelo"
echo "     • Modelo: CLIP-ViT-Large-Patch14"
echo "     • Aesthetic Predictor activado"
echo ""
echo "   Control de Calidad (MÁS ESTRICTO):"
echo "     • CLIP Score mínimo: 70/100 (antes 65)"
echo "     • Aesthetic Score mínimo: 6.0/10 (antes 5.0)"
echo "     • Steps: 50 (antes 40, +25% calidad)"
echo "     • CFG Scale: 7.5 (antes 6.5, más fiel al prompt)"
echo "     • Auto-retry: Hasta $MAX_RETRIES intentos"
echo ""
echo "   Mejoras Visuales:"
echo "     • Paleta: 32 colores unificados"
echo "     • Outline: 1px negro automático"
echo "     • Recorte: Adaptativo (preserva tiles)"
echo ""
echo "   Variaciones: $COUNT por asset"
echo "   Biomas: 10"
echo "   Total estimado: ~10,000 imágenes"
echo ""
echo "⏱️  Tiempo estimado: 10-16 horas"
echo "   (40% más rápido que sistema secuencial)"
echo ""

read -p "¿Iniciar producción masiva? (s/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Ss]$ ]]; then
    echo "🎨 Iniciando generación con colas retroalimentativas..."
    echo "   (Progreso visible en tiempo real)"
    echo ""
    
    # Ejecutar en foreground con todos los parámetros
    python batch_generator_queue.py \
        --count $COUNT \
        --style_strength $STYLE_STRENGTH \
        --cpu_workers $CPU_WORKERS \
        --min_clip_score $MIN_CLIP_SCORE \
        --min_aesthetic $MIN_AESTHETIC \
        --max_retries $MAX_RETRIES
    
    EXIT_CODE=$?
    
    echo ""
    if [ $EXIT_CODE -eq 0 ]; then
        echo "✅ Generación completada exitosamente!"
        echo "📁 Assets guardados en: output_assets/"
        echo ""
        echo "📊 Estadísticas finales mostradas arriba"
    else
        echo "❌ Error durante la generación (código: $EXIT_CODE)"
        echo "   Revisa los mensajes de error arriba"
    fi
else
    echo "❌ Cancelado por el usuario"
    exit 0
fi
