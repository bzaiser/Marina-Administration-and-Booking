#!/bin/bash

echo "=========================================="
echo "   MARINA SAMOS - UPDATE (Linux)"
echo "=========================================="

# Verzeichnis wechseln
cd "$(dirname "$0")"

# Git Pull
echo "[+] Hole Updates von GitHub..."
git pull

# Venv Updates
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "[+] Installiere Requirements..."
    pip install -r requirements.txt
    echo "[+] Führe Migrationen aus..."
    python manage.py migrate
    echo "[+] Aktualisiere lokale Bibliotheken (Flaggen etc.)..."
    python manage.py update_vendor
else
    echo "[WARNUNG] venv nicht gefunden."
fi

echo "=========================================="
echo "   UPDATE ABGESCHLOSSEN!"
echo "=========================================="
