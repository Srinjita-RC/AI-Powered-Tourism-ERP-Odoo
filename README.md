# 🌍 Tourism ERP — Odoo Custom Module
> A production-ready ERP solution for the travel industry, built on the Odoo framework to streamline tourist management, automate itinerary generation, and track travel planning workflows end-to-end.

---

## 🚀 Features

| Feature | Description |
|---|---|
| 👤 Tourist Profile Management | Store and manage complete tourist records with validation |
| 📅 Itinerary Generation | Auto-generate travel plans using custom business logic |
| 🔄 Status Workflow | Draft → Planned → Optimized → Done |
| ✅ Input Validation | Email, phone, and field-level validation built-in |
| 📋 Form & Tree Views | Clean, intuitive Odoo UI for all records |
| 🧠 Smart Plan Logic | Custom Python logic for intelligent itinerary creation |

---

## 🛠️ Tech Stack

- **Backend:** Python 3.x (Odoo ORM & Business Logic)
- **Frontend:** XML (Odoo QWeb Views)
- **Database:** PostgreSQL
- **Platform:** Odoo ERP (Community Edition)

---

## 📂 Project Structure

```
srk_tourism_erp/
│
├── __init__.py                  # Module initializer
├── __manifest__.py              # Module metadata & dependencies
│
├── models/
│   └── tourist.py               # Core tourist model & business logic
│
├── views/
│   └── tourist_view.xml         # Form, tree, and action views
│
└── security/
    └── ir.model.access.csv      # Access control rules
```

---

## ⚙️ Installation

### Prerequisites
- Odoo (Community or Enterprise) installed and running
- PostgreSQL database configured
- Python 3.8+


## 🔄 Workflow

```
[Draft] ──► [Planned] ──► [Optimized] ──► [Done]
  │
  └── Tourist info entered
            │
            └── Plan generated
                      │
                      └── Itinerary reviewed & finalized
```

---

## 🎯 Use Cases

This system is designed for:
- **Travel Agencies** — Manage client profiles and generate itineraries automatically
- **Tour Operators** — Track planning stages from enquiry to completion
- **ERP Customizers** — Reference implementation for custom Odoo module development

---

## 👨‍💻 Author

**Rakshit Maheshwari**
- 🎓 BITS Pilani, Dubai Campus
- 💡 Aspiring Software Developer & ML Engineer
- 🔗 [GitHub](https://github.com/YOUR_USERNAME)

---

## 📌 Roadmap & Future Enhancements

- [ ] AI-based itinerary generation using LLMs
- [ ] Dashboard analytics & reporting
- [ ] Online booking & payment gateway integration
- [ ] Customer self-service portal
- [ ] Multi-language support
- [ ] Mobile-responsive interface

---

## 🧪 Development Notes

- All models follow Odoo ORM conventions
- Security access rules are defined per model in `ir.model.access.csv`
- Views use standard Odoo XML structure with `<form>`, `<tree>`, and `<search>` views
- Business logic is decoupled from views for maintainability

---

## ⭐ Acknowledgement

Developed as part of an academic project at **BITS Pilani, Dubai Campus** to demonstrate enterprise-grade ERP customization using the Odoo framework.

---
