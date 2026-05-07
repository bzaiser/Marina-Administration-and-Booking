# Marina Administration and Booking System (Samos)

A professional management and booking tool for a Marina on the Greek island of Samos. Built with a modern, reactive Open Source stack.

## 🚀 Tech Stack
- **Backend**: Python / Django 4.2
- **Database**: SQLite
- **Frontend**: Bootstrap 5, HTMX, Alpine.js
- **Specialized Components**: 
  - **DayPilot Lite**: For visual scheduling and booking calendar.
  - **AG Grid Community**: For high-performance data management.
  - **xhtml2pdf**: For professional PDF invoice generation.
  - **Chart.js**: For analytics and reporting.

## ✨ Key Features
- **Berth Management**: 75 berths organized in Blocks A-E. Interactive status overview (Occupied, Vacant, At Sea).
- **Booking Calendar**: Visual timeline for planning arrivals and departures.
- **Sub-Leasing Logic**: Track long-term tenants "at sea" and temporarily reassign berths.
- **Invoicing**: Automatic price calculation based on boat length and duration. Export to PDF.
- **Planning Grid**: Massive denormalized view for daily occupancy tracking across the entire year.
- **Analytics**: Revenue charts, occupancy rates, and top customer statistics.
- **Offline Ready**: No CDN dependencies, all libraries and flags are hosted locally.

## 🖥️ Installation & Betrieb

---

### 🪟 Windows — Erstinstallation (setup-marina.bat)

> **Keine Voraussetzungen nötig** — kein Python installieren, kein Setup von Hand.

1. Repository herunterladen:
   - Als ZIP von GitHub → entpacken, **oder**
   - `git clone https://github.com/bzaiser/Marina-Administration-and-Booking.git`

2. **`setup-marina.bat`** per Doppelklick starten — fertig.

Das Script erledigt automatisch:
- ✅ Portables Python 3.11 herunterladen (lokal im Projektordner, keine Installation)
- ✅ Alle Abhängigkeiten installieren
- ✅ Datenbank einrichten (`migrate`)
- ✅ Lokale Bibliotheken laden (`update_vendor`)
- ✅ Optional: Desktop-Verknüpfungen erstellen
- ✅ Optional: App direkt starten

---

### 🪟 Windows — App starten (start-marina.bat)

Doppelklick auf **`start-marina.bat`** (oder Desktop-Verknüpfung).

- Aktiviert die virtuelle Umgebung
- Öffnet automatisch den Browser auf `http://127.0.0.1:8003`
- Startet den Django-Server

---

### 🪟 Windows — Updates einspielen (update-marina.bat)

Doppelklick auf **`update-marina.bat`** (oder Desktop-Verknüpfung).

- Holt aktuelle Version von GitHub (`git pull`)
- Aktualisiert Abhängigkeiten
- Führt Datenbankmigrationen aus
- Aktualisiert lokale Bibliotheken

> **Hinweis:** [Git für Windows](https://git-scm.com/download/win) muss installiert sein, wenn das Repo per `git clone` bezogen wurde. Bei ZIP-Download stattdessen manuell neu herunterladen und `setup-marina.bat` erneut ausführen.

---

### 🐧 Linux — Erstinstallation

```bash
git clone https://github.com/bzaiser/Marina-Administration-and-Booking.git
cd Marina-Administration-and-Booking
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py update_vendor
```

---

### 🐧 Linux — App starten (start-marina.sh)

```bash
./start-marina.sh
```

- Aktiviert die virtuelle Umgebung
- Öffnet den Browser auf `http://127.0.0.1:8003`
- Startet den Django-Server

---

### 🐧 Linux — Updates einspielen (update-marina.sh)

```bash
./update-marina.sh
```

- `git pull` → neueste Version
- `pip install -r requirements.txt`
- `python manage.py migrate`
- `python manage.py update_vendor`

---

## 🔧 Skript-Übersicht

| Datei | System | Funktion |
|---|---|---|
| `setup-marina.bat` | Windows | **Erstinstallation** — alles einmalig einrichten |
| `start-marina.bat` | Windows | App starten |
| `update-marina.bat` | Windows | Updates einspielen |
| `start-marina.sh` | Linux | App starten |
| `update-marina.sh` | Linux | Updates einspielen |

---

## 📶 Offline-Betrieb & Vendor-Bibliotheken

Das System funktioniert vollständig ohne Internetverbindung (z. B. im Hafen). Alle Bibliotheken (Bootstrap, HTMX, Alpine.js, AG-Grid, Vis.js, Chart.js) und Landesflaggen werden lokal in `static/vendor/` gespeichert.

Manuell aktualisieren:
```bash
python manage.py update_vendor
```

## 🚩 Länder & Flaggen

1. Im Django-Admin → Countries → ISO-Code (z. B. `gr`) und Name (z. B. `Greece`) eintragen.
2. `python manage.py update_vendor` ausführen → Flagge wird automatisch heruntergeladen.
3. Das neue Land erscheint sofort in den Boot-Formularen.

## 🔄 Automatische Aktualisierungen

- **Liegeplatz-Grid**: Aktualisiert alle 30 Sekunden automatisch via HTMX.
- **Modals**: HTMX-gesteuert — Daten bearbeiten ohne Seitenneuladen.

## 📂 Projektstruktur

- `marina/` — Anwendungslogik, Models, Views
- `marina_project/` — Django-Projektkonfiguration
- `templates/` — HTML-Templates (Dashboard, Kalender, Grids)
- `static/` — CSS (HSL Design-System), JS, Vendor-Bibliotheken

## 📜 Lizenz

Open Source — Verwaltet von Bernd Zaiser.
