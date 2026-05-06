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

## 🛠 Installation & Setup

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
   python manage.py seed_demo  # Optional: Seed demo data
   ```

5. **Create Admin**:
   ```bash
   python manage.py createsuperuser
   ```

6. **Run Server**:
   ```bash
   python manage.py runserver
   ```

## 📂 Project Structure
- `marina/`: Main application logic, models, and views.
- `marina_project/`: Django project configuration.
- `templates/`: HTML templates (Base, Dashboard, Calendar, Grids, Partials).
- `static/`: Custom CSS (HSL-based design system) and JS.

## 📜 License
Open Source - Managed by Bernd Zaiser.
