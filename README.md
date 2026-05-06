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

## ⚡ Quick Start (The Easy Way)

If you just want to get started quickly without manual setup, use our automated scripts:

### 🪟 Windows Users (Portable)
1.  Download or copy the **`Beispiel-Mobil.bat`** file.
2.  Double-click it.
3.  The script will automatically download the code, create a local Python environment, and set everything up.
4.  Follow the prompt to create **Desktop Icons** for easy access.

### 🐧 Linux Users
1.  Open your terminal in the project folder.
2.  Run **`./start-marina.sh`** to start the application.
3.  Run **`./update-marina.sh`** at any time to pull updates and refresh the system.

---

## 🛠 Manual Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/bzaiser/Marina-Administration-and-Booking.git
   cd Marina-Administration-and-Booking
   ```

2. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize Database**:
   ```bash
   python manage.py migrate
   python manage.py seed_berths
   python manage.py seed_countries
   python manage.py seed_demo  # Optional: Seed demo data
   ```

5. **Create Admin**:
   ```bash
   python manage.py createsuperuser
   ```

5. **Download Vendor Libraries (Offline Support)**:
   ```bash
   python manage.py update_vendor
   ```

6. **Run Server**:
   ```bash
   python manage.py runserver
   ```

## 📶 Offline Support & Vendor Management
The system is designed to be fully operational without an internet connection (e.g., in a harbor environment). All major libraries are hosted locally in `static/vendor/`.

To update the local libraries from the internet, run:
```bash
python manage.py update_vendor
```
This command fetches the latest stable versions of Bootstrap, HTMX, Alpine.js, AG-Grid, Vis.js, and Chart.js.

## 🚩 Country & Flag Management
Flags are managed dynamically through the database.

1. **Add a new Country**: Go to the Django Admin -> Countries and add the ISO code (e.g., `be`) and Name (e.g., `Belgium`).
2. **Download the Flag**: Run `python manage.py update_vendor`. The system will automatically detect new countries and download their SVG flags to the local storage.
3. **Usage**: The new country will immediately appear as a choice in the Boat Edit/Create masks.

## 🔄 Automatic Updates
- **Berths Grid**: Automatically refreshes its data every 30 seconds via HTMX to ensure the occupancy status is always up-to-date.
- **Modals**: HTMX-driven modals allow updating boat and booking data without a full page reload.

## 📂 Project Structure
- `marina/`: Main application logic, models, and views.
- `marina_project/`: Django project configuration.
- `templates/`: HTML templates (Base, Dashboard, Calendar, Grids, Partials).
- `static/`: Custom CSS (HSL-based design system) and JS.

## 📜 License
Open Source - Managed by Bernd Zaiser.
