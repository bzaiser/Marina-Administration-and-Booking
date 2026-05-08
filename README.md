# Marina Administration and Booking System (Samos)

A professional management and booking tool for a Marina on the Greek island of Samos. Built with a modern, reactive Open Source stack.

## 🚀 Tech Stack
- **Backend**: Python / Django 4.2
- **Database**: SQLite (Locally stored or network path)
- **Frontend**: Bootstrap 5, HTMX, Alpine.js
- **Specialized Components**: 
  - **DayPilot Lite**: For visual scheduling and booking calendar.
  - **AG Grid Community**: For high-performance data management.
  - **xhtml2pdf**: For professional PDF invoice generation.
  - **Chart.js**: For analytics and reporting.
  - **svg-pan-zoom**: For the interactive Marina Live View.

## ✨ Key Features
- **Berth Management**: 75 berths organized in Blocks A-E. Interactive status overview.
- **Marina Live View**: Interactive SVG map with real-time occupancy tracking and boat info tooltips.
- **Booking Calendar**: Visual timeline for planning arrivals and departures.
- **Invoicing**: Automatic price calculation based on boat length and duration. Export to PDF.
- **Business Analytics**: Comprehensive reports on revenue trends, boat types, and nationalities.
- **Offline Ready**: No CDN dependencies, all libraries and assets (flags, icons) are hosted locally.

## 🖥️ Installation & Operation

### 🪟 Windows (Batch Scripts)
1. **`setup-marina.bat`**: First-time installation. Downloads portable Python, sets up VENV, and initializes the DB.
2. **`start-marina.bat`**: Launches the application and opens your browser.
3. **`update-marina.bat`**: Fetches the latest changes from Git and updates dependencies.

### 🍎 macOS / 🐧 Linux (Shell Scripts)
1. **`setup-marina.sh`**: Initializes the environment and installs requirements.
2. **`run.sh`**: Activates the environment and starts the server.
3. **`update-marina.sh`**: Pulls updates and migrates the database.

### 🧪 Initial Seed Data
To populate the system with 75 berths, sample customers, boats, and historical reports data:
```bash
python manage.py seed_all
```

## 📶 Offline-Betrieb & Vendor-Bibliotheken
Das System funktioniert vollständig ohne Internetverbindung. Alle Bibliotheken (Bootstrap, HTMX, Alpine.js, AG-Grid, Chart.js) sind lokal in `static/vendor/` gespeichert.

## 📂 Projektstruktur
- `marina/` — Anwendungslogik, Models, Views
- `marina_project/` — Django-Projektkonfiguration
- `templates/` — HTML-Templates (Dashboard, Kalender, Grids)
- `static/` — CSS (HSL Design-System), JS, Vendor-Bibliotheken
- `media/` — Boat photos, Logo, and dynamic assets

## 📜 About
Created and managed by Bernd Zaiser. Professional Marina Management Solution for Samos.
