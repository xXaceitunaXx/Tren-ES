#!/bin/bash

# Script para generar el PDF unificando los markdowns con Pandoc
# Ejecutar desde la raíz del proyecto o desde scripts/

# Determinamos la ruta base del proyecto (un nivel arriba de scripts/)
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Generando PDF en $BASE_DIR..."

pandoc \
    "$BASE_DIR/etc/InformeCompleto.md" \
    "$BASE_DIR/docs/EsquemaMediador.md" \
    "$BASE_DIR/docs/FormulacionSQL.md" \
    "$BASE_DIR/docs/EsquemasOrigen.md" \
    "$BASE_DIR/docs/EsquemasGAV.md" \
    "$BASE_DIR/docs/EsquemasLAV.md" \
    "$BASE_DIR/docs/ReformulacionConsultas.md" \
        -o "$BASE_DIR/etc/InformeHito1.pdf" \
        --pdf-engine=xelatex \
        --toc \
        --number-sections \
        -V colorlinks=true \
        -V urlcolor=blue \
        -V geometry:margin=2.5cm

echo "¡Hecho! El archivo se ha generado en $BASE_DIR/informe.pdf"
