#!/bin/bash

echo "==========================================="
echo "   MARINA SAMOS - START (Linux)"
echo "==========================================="

# Verzeichnis wechseln zum Skript-Ort
cd "$(dirname "$0")"

# Venv aktivieren
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "[FEHLER] venv nicht gefunden. Bitte zuerst Setup ausführen."
    exit 1
fi

# Server im Hintergrund starten und Browser öffnen (optional)
echo "[+] Starte Server auf Port 8003..."
xdg-open http://127.0.0.1:8003 2>/dev/null || echo "Bitte http://127.0.0.1:8003 manuell öffnen."
python manage.py runserver 8003
