# VoltRide | Ultra-Modern E-Bike & Spare Parts E-Commerce Platform

![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)
![Django Version](https://img.shields.io/badge/django-6.0.7-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/build-passing-brightgreen.svg)

**VoltRide** is an ultra-modern, production-ready full-stack e-commerce web application engineered with Django for selling high-performance electric bicycles, genuine OEM spare parts, certified lithium battery packs, smart fast chargers, brushless motors, and precision cycling accessories.

Designed with an electric mobility automotive aesthetic (deep charcoal `#0b0f19`, electric neon cyan `#00d2ff`, cyber lime `#00e599`), VoltRide offers a commercial-grade shopping experience across desktop, tablet, and mobile devices.

---

## ⚡ Main Features

### 1. Global Header & Navigation
* **Promotional Marquee Bar:** Continuously horizontally scrolling marquee displaying free shipping thresholds, warranty notices, and product alerts.
* **Sticky Navbar:** Responsive navigation with multi-level dropdowns for E-Bikes, Spare Parts, Accessories, Company pages, and Knowledge Base.
* **Live Search Bar:** Instant AJAX autocomplete suggestions with thumbnail previews and direct links.
* **Badged Action Icons:** Real-time quantity counters for the Shopping Cart and saved Wishlist items.
* **Mobile Offcanvas Drawer:** App-like slide-in drawer with navigation, search, and account controls for mobile screens.

### 2. High-Performance Storefront & Catalog
* **Dynamic Multi-Faceted Filters:** Filter by category, subcategory, product type (`ebike`, `spare_part`, `accessory`), brand, price range, and in-stock status.
* **Advanced Sorting:** Sort by Newest First, Price (Low to High / High to Low), Popularity, Highest Rated, and Alphabetical.
* **Quick View Modal:** AJAX-powered preview modal rendering specs, prices, stock statuses, and instantaneous cart addition.
* **Rich Product Detail Pages:** 
  * High-resolution image galleries with thumbnail switching.
  * Technical specification sheets (Motor output, battery cells, range, speed, torque).
  * OEM Spare Parts Compatibility sections.
  * Tabbed layout for Descriptions, Specs, Verified Reviews, and Warranty terms.
  * Dynamically calculated discount badges and stock status indicators.

### 3. Shopping Cart & Checkout
* **Session & Database Cart:** Seamlessly supports guest shoppers and authenticated accounts.
* **Stock Limit Enforcement:** Prevents adding more units than available inventory.
* **Free Shipping Engine:** Dynamic progress bar indicating distance to free freight shipping ($500 threshold).
* **Express Checkout:** Validates customer contact, billing, and shipping destination addresses.
* **Flexible Payment Gateways:**
  * Cash on Delivery (COD)
  * Direct Bank Wire Transfer
  * Online Credit/Debit Card Gateway Architecture (with Stripe / PayPal integration points)
* **Automated Stock Decrement:** Product quantities automatically deduct upon order confirmation.

### 4. Customer Accounts & Order Management
* **Account Dashboard:** Real-time customer overview showing lifetime order count, saved wishlist items, and published reviews.
* **Order History & Invoices:** View status timeline (`Pending` → `Confirmed` → `Processing` → `Shipped` → `Delivered`) and printable tax invoices.
* **Wishlist System:** One-click wishlist toggling from cards and product detail pages with "Move to Cart" action.
* **Security & Auth:** Secure Django password hashing, profile editor, and password reset email flows.

### 5. Verified Product Reviews
* **Authentic Reviews:** 5-star rating system with title and detailed text comments.
* **Verified Purchase Badging:** Automatically checks order history to badge buyers as *Verified Owners*.
* **Duplicate Prevention:** Prevents repeated reviews for the same product by the same user.
* **Admin Moderation:** Staff approval and rejection controls inside the admin dashboard.

### 6. Engineering Knowledge Hub (Blog)
* **12 Comprehensive Technical Guides:** Complete articles covering battery chemistry, winter maintenance, motor power differences, chargers, and commuting safety.
* **Categorized Articles & Tags:** Filter guides by Buying Guides, Maintenance & Care, Battery & Electrical, and Safety.
* **Real-Time Read Counter:** Automatically tracks article views.

### 7. Administrative Control & Analytics
* **Executive Analytics Dashboard (`/admin/orders/order/analytics-dashboard/`):**
  * Total Gross Revenue
  * Order Count and Fulfillment Status Bars
  * Low Stock Threshold Alerts
  * Recent Customer Orders & Product Reviews
* **Full Django Admin CRUD:** Management interfaces for Products, Categories, Orders, Reviews, Blog Posts, Contact Messages, and Newsletter Subscribers.

---

## 🛠 Technology Stack

* **Backend:** Python 3.12+, Django 6.0+, Django ORM
* **Frontend:** HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Font Awesome 6
* **Database:** SQLite (Development) / PostgreSQL or MySQL compatible (Production)
* **Media Processing:** Pillow (Python Imaging Library)
* **Environment Configuration:** Python-Dotenv

---

## 📁 Project Directory Structure

```text
Bikes/
│
├── manage.py
├── requirements.txt
├── .env.example
├── .env
├── .gitignore
├── README.md
│
├── config/                  # Project Configuration
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── store/                   # Products, Categories, Cart & Wishlist
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── cart.py
│   ├── context_processors.py
│   ├── image_generator.py
│   ├── admin.py
│   ├── tests.py
│   └── management/commands/seed_data.py
│
├── orders/                  # Checkout, Orders & Order Items
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── tests.py
│
├── accounts/                # Authentication, Profiles & Dashboards
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── tests.py
│
├── reviews/                 # Product Ratings & Feedback
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── tests.py
│
├── blog/                    # Knowledge Articles & Technical Guides
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── tests.py
│
├── pages/                   # Static Pages, Contact, Search, FAQ, Policies
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   ├── sitemaps.py
│   ├── context_processors.py
│   ├── admin.py
│   └── tests.py
│
├── static/
│   ├── css/style.css
│   ├── js/main.js
│   └── images/
│
├── media/
│   ├── products/
│   ├── blog/
│   └── categories/
│
└── templates/
    ├── base.html
    ├── pages/
    ├── shop/
    ├── products/
    ├── orders/
    ├── accounts/
    ├── blog/
    ├── admin/
    └── errors/
```

---

## 🚀 Quickstart Installation Guide

### 1. Clone or Open the Repository
```bash
cd c:\Users\HANSLEM_KIMENG\Desktop\WEB\Bikes
```

### 2. Create and Activate Virtual Environment
On Windows PowerShell:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

On Linux / macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Ensure your secret key and database credentials are set appropriately.

### 5. Apply Database Migrations
```bash
python manage.py migrate
```

### 6. Populate Database with Realistic Seed Data
Run the idempotent seed command to generate 25 products with graphics, 30 authentic reviews, 12 complete blog guides, sample orders, and an administrator account:
```bash
python manage.py seed_data
```

Default Admin Credentials:
* **Username:** `admin`
* **Password:** `admin12345`

### 7. Run Automated Tests
Execute the full test suite across all 6 applications:
```bash
python manage.py test
```
*(All 17 tests will run and pass).*

### 8. Start the Local Development Server
```bash
python manage.py runserver
```

Open your browser and navigate to:
* **Storefront:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
* **Admin Portal:** [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
* **Admin Analytics:** [http://127.0.0.1:8000/admin/orders/order/analytics-dashboard/](http://127.0.0.1:8000/admin/orders/order/analytics-dashboard/)

---

## 🔒 Security & Production Checklist

1. **Production Secret Key:** Generate a unique secret key and set `DEBUG=False` in `.env`.
2. **Allowed Hosts:** Add your domain name (e.g., `ALLOWED_HOSTS=voltride.com,www.voltride.com`).
3. **Database:** In production on cPanel, AWS, or PythonAnywhere, configure PostgreSQL or MySQL via `DATABASE_URL`.
4. **Static Collection:** Run `python manage.py collectstatic --noinput` to assemble all assets into `staticfiles/`.
5. **HTTPS / SSL:** Ensure your reverse proxy (Nginx / Apache / Caddy) enforces HTTP to HTTPS redirection.
6. **Payment Gateways:** To connect live Stripe or PayPal processing, add your API keys to `.env` and plug them into `orders/views.py`.

---

## 📄 License
This project is open-source and released under the **MIT License**.
Built with precision by the VoltRide engineering team.
