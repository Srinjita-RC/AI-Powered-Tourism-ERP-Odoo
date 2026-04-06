# 🌍 SRK Tourism ERP — Odoo Custom Module

> A production-ready, full-featured ERP solution for the travel industry, built on the Odoo framework. Manages tourist profiles, automates AI-powered itinerary generation, handles bookings, monitors safety alerts, and delivers real-time analytics — all in one platform.

---

## 🚀 Features

| Feature | Description |
|---|---|
| 👤 Tourist Profile Management | Complete tourist records with validation, interests & preferences |
| 📅 AI Itinerary Generation | Auto-generate day-by-day travel plans using custom AI logic |
| 🔄 Status Workflow | Draft → Planned → Optimized → Done |
| 📋 Booking Management | Full booking lifecycle with country & city support |
| 📊 Analytics Dashboard | Real-time stats, charts, and insights on tourist data |
| ⚠️ Safety Alerts | Destination safety monitoring and alert system |
| 📄 PDF Export | Branded itinerary PDF with multi-language support |
| ✅ Input Validation | Email, phone, and field-level validation built-in |
| 🌐 Public Booking Page | Standalone HTML booking page with live crowd heatmap |
| 🧭 Tab Navigation | Smooth multi-tab UI (Profile → Trip → Interests → Itinerary → Map) |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.x (Odoo ORM & Business Logic) |
| **Frontend** | XML (Odoo QWeb Views) + CSS + JavaScript |
| **Styling** | Custom CSS (`tourism.css`) |
| **Tab Navigation** | Custom JS (`tab_navigator.js`) |
| **Map** | Leaflet.js + OpenStreetMap |
| **PDF Generation** | ReportLab + NotoSans (multi-language) |
| **Database** | PostgreSQL |
| **Platform** | Odoo ERP (Community Edition) |

---

## 📂 Project Structure

```
custom_addons/srk_tourism_erp/
│
├── __init__.py                        # Module initializer
├── __manifest__.py                    # Module metadata & dependencies
│
├── models/
│   ├── __init__.py                    # Models initializer
│   ├── tourist.py                     # Core tourist model, AI plan, PDF export
│   ├── booking.py                     # Booking management model
│   ├── analytics.py                   # Analytics & dashboard logic
│   └── safety_alert.py                # Safety alert model
│
├── views/
│   ├── tourist_view.xml               # Tourist form, tree & action views
│   ├── booking_view.xml               # Booking form & list views
│   ├── analytics_view.xml             # Analytics dashboard views
│   ├── safety_view.xml                # Safety alerts views
│   └── menu.xml                       # App menu & navigation
│
├── security/
│   └── ir.model.access.csv            # Access control rules for all models
│
├── data/
│   └── sequences.xml                  # Auto-sequence configuration
│
└── static/
    ├── description/
    │   └── travel_bg.jpg              # App icon / description image
    └── src/
        ├── css/
        │   └── tourism.css            # Custom styling for Odoo views
        └── js/
            └── tab_navigator.js       # Custom tab navigation logic
```

---

## ⚙️ Installation

### Prerequisites
- Odoo Community Edition installed and running
- PostgreSQL database configured
- Python 3.8+
- ReportLab (`pip install reportlab`) for PDF export
- NotoSans fonts in `static/fonts/` for multi-language PDF support

### Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/srk-tourism-erp.git
   ```

2. **Copy the module to your Odoo custom addons path:**
   ```bash
   cp -r srk_tourism_erp/ /odoo/custom_addons/
   ```

3. **Install required Python packages:**
   ```bash
   pip install reportlab
   pip install arabic-reshaper python-bidi   # for Arabic/RTL language support
   ```

4. **Restart the Odoo server:**
   ```bash
   python odoo-bin -c odoo.conf
   ```

5. **Activate Developer Mode:**
   Settings → General Settings → Activate Developer Mode

6. **Install the module:**
   Apps → Update Apps List → Search **"SRK Tourism ERP"** → Click **Install**

---

## 🔄 Status Workflow

```
[Draft] ──► [Planned] ──► [Optimized] ──► [Done]
               │                              │
         Email sent to                  Email sent to
           tourist                        tourist
               │
         AI Plan Generated
         PDF Available
         Crowd Map Active
```

---

## 📱 Module Screens

| Screen | Description |
|---|---|
| Tourist Form | Multi-tab form: Profile, Trip, Interests, Itinerary, Map |
| Booking View | Booking list & form with country + city fields |
| Analytics Dashboard | Charts, KPIs, tourist trends |
| Safety Alerts | Destination-wise safety status |
| PDF Itinerary | Auto-generated branded PDF (multi-language) |
| Public Booking Page | Standalone page with live crowd heatmap |

---

## 🧪 Models Overview

| Model | File | Purpose |
|---|---|---|
| `tourist.profile` | `tourist.py` | Core tourist data, itinerary, PDF, notifications |
| `srk.booking` | `booking.py` | Trip bookings and reservations |
| `srk.analytics` | `analytics.py` | Dashboard stats and reporting |
| `srk.safety.alert` | `safety_alert.py` | Destination safety alerts |

---

## 🎯 Use Cases

- **Travel Agencies** — Manage client profiles, auto-generate itineraries, track status
- **Tour Operators** — Monitor bookings, send automated updates, export PDFs
- **Safety Teams** — Issue destination alerts visible to all agents
- **Management** — View analytics dashboard for business insights

---

## 📌 Roadmap & Future Enhancements

- [x] AI-based itinerary generation
- [x] PDF export with multi-language support
- [x] Analytics dashboard
- [x] Safety alert system
- [x] Automated email notifications
- [x] Public booking page with crowd heatmap
- [x] Custom CSS & JS for enhanced UI
- [ ] WhatsApp notifications via Twilio
- [ ] Tourist self-service portal
- [ ] Payment gateway integration
- [ ] Mobile-responsive interface
- [ ] BestTime API for real-time crowd data

---

## 🧑‍💻 Development Notes

- All models follow Odoo ORM conventions
- PDF generation uses ReportLab with NotoSans for Unicode/multi-language support
- Custom JavaScript (`tab_navigator.js`) handles smooth tab navigation
- Custom CSS (`tourism.css`) provides consistent branding across all views
- Security access rules defined per model in `ir.model.access.csv`
- Sequences auto-configured via `data/sequences.xml`
- Static assets follow Odoo's standard `static/src/` convention

---

## 👨‍💻 Author

**Rakshit Maheshwari**
- 🎓 BITS Pilani, Dubai Campus
