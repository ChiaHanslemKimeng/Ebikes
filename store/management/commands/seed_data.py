import os
import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from store.models import Category, Subcategory, Product, ProductImage
from reviews.models import ProductReview
from blog.models import BlogCategory, BlogPost
from orders.models import Order, OrderItem, Payment
from pages.models import ContactMessage, NewsletterSubscriber
from store.image_generator import create_product_graphic, create_blog_graphic


class Command(BaseCommand):
    help = "Populates the VoltRide database with realistic categories, products, reviews, blog posts, and orders."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Starting VoltRide database seeding..."))

        # 1. Superuser & Sample Users
        admin_user, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@voltride.com",
                "first_name": "Marcus",
                "last_name": "Vance",
                "is_staff": True,
                "is_superuser": True,
            }
        )
        if created:
            admin_user.set_password("admin12345")
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("Created admin user (admin / admin12345)"))

        sample_customers = [
            ("alex_rider", "alex.rider@example.com", "Alex", "Rider"),
            ("sarah_connor", "sarah.c@example.com", "Sarah", "Connor"),
            ("david_chen", "david.chen@example.com", "David", "Chen"),
            ("elena_rostova", "elena.r@example.com", "Elena", "Rostova"),
            ("marcus_bell", "marcus.b@example.com", "Marcus", "Bell"),
            ("olivia_taylor", "olivia.t@example.com", "Olivia", "Taylor"),
            ("james_wilson", "james.w@example.com", "James", "Wilson"),
            ("maya_patel", "maya.p@example.com", "Maya", "Patel"),
        ]
        created_users = [admin_user]
        for username, email, first, last in sample_customers:
            u, _ = User.objects.get_or_create(
                username=username,
                defaults={"email": email, "first_name": first, "last_name": last}
            )
            u.set_password("customer123")
            u.save()
            created_users.append(u)

        # 2. Categories & Subcategories
        categories_data = [
            {
                "name": "Electric Bikes",
                "slug": "electric-bikes",
                "description": "High-performance electric bicycles engineered for city streets, rugged mountains, and daily commutes.",
                "icon": "fa-bicycle",
                "is_featured": True,
                "order": 1,
                "subcategories": ["City E-Bikes", "Mountain E-Bikes", "Folding E-Bikes", "Commuter E-Bikes", "Fat Tire E-Bikes", "Cargo E-Bikes"]
            },
            {
                "name": "Spare Parts",
                "slug": "spare-parts",
                "description": "OEM replacement components, upgrade kits, and high-spec mechanical parts.",
                "icon": "fa-cogs",
                "is_featured": True,
                "order": 2,
                "subcategories": ["Motors", "Controllers", "Brakes", "Tires & Wheels", "Displays", "Throttles", "Chains & Pedals", "Suspension"]
            },
            {
                "name": "Batteries & Power",
                "slug": "batteries",
                "description": "High-density lithium-ion battery packs, smart BMS systems, and fast charging docks.",
                "icon": "fa-battery-full",
                "is_featured": True,
                "order": 3,
                "subcategories": ["48V Batteries", "52V High Performance", "Replacement Cells", "Battery Mounts"]
            },
            {
                "name": "Chargers",
                "slug": "chargers",
                "description": "Smart multi-stage fast chargers with automatic cut-off and thermal monitoring.",
                "icon": "fa-bolt",
                "is_featured": True,
                "order": 4,
                "subcategories": ["Fast Chargers", "Standard Chargers", "Travel Adapters"]
            },
            {
                "name": "Lighting & Electronics",
                "slug": "lighting",
                "description": "Ultra-bright LED headlights, taillights with brake detection, and wiring harnesses.",
                "icon": "fa-lightbulb",
                "is_featured": False,
                "order": 5,
                "subcategories": ["Headlights", "Rear Brake Lights", "Horns & Alarms", "Wiring Harnesses"]
            },
            {
                "name": "Accessories & Gear",
                "slug": "accessories",
                "description": "Rider safety gear, smart helmets, heavy-duty locks, and ergonomic cargo bags.",
                "icon": "fa-shield-alt",
                "is_featured": True,
                "order": 6,
                "subcategories": ["Helmets", "Locks & Security", "Panniers & Bags", "Phone Mounts", "Pumps & Tools"]
            },
        ]

        cat_objs = {}
        subcat_objs = {}
        for cdata in categories_data:
            cat, _ = Category.objects.get_or_create(
                slug=cdata["slug"],
                defaults={
                    "name": cdata["name"],
                    "description": cdata["description"],
                    "icon": cdata["icon"],
                    "is_featured": cdata["is_featured"],
                    "order": cdata["order"]
                }
            )
            cat_objs[cdata["slug"]] = cat
            for sname in cdata["subcategories"]:
                from django.utils.text import slugify
                sub_slug = slugify(sname)
                subcat, _ = Subcategory.objects.get_or_create(
                    category=cat,
                    slug=sub_slug,
                    defaults={"name": sname, "description": f"Genuine {sname} for VoltRide e-bikes."}
                )
                subcat_objs[f"{cat.slug}:{sub_slug}"] = subcat

        # 3. Products
        products_data = [
            # E-Bikes
            {
                "name": "VoltRide City Pro Electric Bike",
                "slug": "voltride-city-pro",
                "SKU": "VR-EBIKE-001",
                "category": cat_objs["electric-bikes"],
                "subcategory": subcat_objs.get("electric-bikes:city-e-bikes"),
                "product_type": "ebike",
                "price": Decimal("1899.00"),
                "sale_price": Decimal("1699.00"),
                "cost_price": Decimal("1100.00"),
                "stock_quantity": 18,
                "brand": "VoltRide",
                "model": "City Pro V3",
                "weight": "21.5 kg",
                "dimensions": "178 x 64 x 102 cm",
                "battery_capacity": "48V 15Ah (720Wh) Samsung 21700 Cells",
                "motor_power": "500W High Torque Bafang Rear Hub (750W Peak)",
                "maximum_speed": "42 km/h (26 mph)",
                "range": "80-110 km (50-68 miles)",
                "charging_time": "4.5 Hours",
                "color": "Stealth Carbon Black",
                "material": "Hydroformed 6061 Aluminum Alloy",
                "compatibility": "Universal VoltRide Modular Rack System",
                "featured": True,
                "bestseller": True,
                "new_arrival": False,
                "short_description": "The ultimate urban commuter e-bike featuring torque sensing, hydraulic disc brakes, and integrated headlights.",
                "description": "The VoltRide City Pro is engineered for discerning urban professionals and daily commuters. Featuring an advanced torque sensor that matches your pedaling cadence instantaneously, riding uphill feels practically effortless. With an integrated 720Wh Samsung battery pack seamlessly flush inside the downtube, the City Pro delivers up to 110 km on a single charge while preserving sleek minimalist aesthetics. Equipped with dual-piston hydraulic disc brakes, puncture-resistant 27.5-inch tires, and an ultra-bright 800-lumen cockpit light, your commute has never been smoother or safer.",
            },
            {
                "name": "VoltRide Mountain X All-Terrain E-Bike",
                "slug": "voltride-mountain-x",
                "SKU": "VR-EBIKE-002",
                "category": cat_objs["electric-bikes"],
                "subcategory": subcat_objs.get("electric-bikes:mountain-e-bikes"),
                "product_type": "ebike",
                "price": Decimal("2699.00"),
                "sale_price": Decimal("2449.00"),
                "cost_price": Decimal("1650.00"),
                "stock_quantity": 12,
                "brand": "VoltRide",
                "model": "Mountain X-Trail",
                "weight": "24.8 kg",
                "dimensions": "188 x 72 x 110 cm",
                "battery_capacity": "52V 20Ah (1040Wh) LG Chem Cells",
                "motor_power": "1000W Bafang Ultra Mid-Drive (160Nm Torque)",
                "maximum_speed": "50 km/h (31 mph)",
                "range": "95-130 km (60-80 miles)",
                "charging_time": "5.5 Hours Fast Charge",
                "color": "Forest Slate & Cyber Lime",
                "material": "Aircraft-Grade 7005 Aluminum + Carbon Stays",
                "compatibility": "Compatible with all 52V VoltRide battery docks and RockShox suspension forks",
                "featured": True,
                "bestseller": True,
                "new_arrival": True,
                "short_description": "Conquer wild mountain passes and steep inclines with 160Nm mid-drive torque and dual air suspension.",
                "description": "Engineered for pure off-road exhilaration, the VoltRide Mountain X represents the pinnacle of trail electrification. Powered by a 1000W Bafang Ultra mid-drive motor generating a monstrous 160Nm of torque, no incline is too steep. Full air suspension with 150mm travel dampens rugged rocky descents, while 4-piston hydraulic brakes guarantee instantaneous stopping control in wet mud or loose gravel.",
            },
            {
                "name": "VoltRide Urban Lite Commuter",
                "slug": "voltride-urban-lite",
                "SKU": "VR-EBIKE-003",
                "category": cat_objs["electric-bikes"],
                "subcategory": subcat_objs.get("electric-bikes:commuter-e-bikes"),
                "product_type": "ebike",
                "price": Decimal("1399.00"),
                "sale_price": Decimal("1249.00"),
                "cost_price": Decimal("780.00"),
                "stock_quantity": 25,
                "brand": "VoltRide",
                "model": "Urban Lite V2",
                "weight": "16.8 kg",
                "dimensions": "172 x 60 x 98 cm",
                "battery_capacity": "36V 10.5Ah Panasonic Cells",
                "motor_power": "350W Silent Geared Hub Motor",
                "maximum_speed": "32 km/h (20 mph)",
                "range": "60-75 km (37-46 miles)",
                "charging_time": "3.5 Hours",
                "color": "Glacier White & Cyan",
                "material": "Lightweight 6061 Alloy",
                "compatibility": "VoltRide Quick-Detach Rear Bag Mount",
                "featured": True,
                "bestseller": False,
                "new_arrival": True,
                "short_description": "Weighing only 16.8kg, this featherweight city e-bike delivers agile handling and simple stair carry.",
                "description": "For riders who need to carry their bike up apartment stairs or onto metro trains, the VoltRide Urban Lite is the answer. Stripping unnecessary weight while retaining lively motor assistance, it accelerates briskly up to 32 km/h with silent, maintenance-free belt drive transmission.",
            },
            {
                "name": "VoltRide Fold Compact E-Bike",
                "slug": "voltride-fold-compact",
                "SKU": "VR-EBIKE-004",
                "category": cat_objs["electric-bikes"],
                "subcategory": subcat_objs.get("electric-bikes:folding-e-bikes"),
                "product_type": "ebike",
                "price": Decimal("1599.00"),
                "sale_price": None,
                "cost_price": Decimal("950.00"),
                "stock_quantity": 14,
                "brand": "VoltRide",
                "model": "Fold Gen 2",
                "weight": "19.5 kg",
                "dimensions": "Folded: 85 x 45 x 70 cm",
                "battery_capacity": "48V 13Ah Seatpost Hidden Battery",
                "motor_power": "500W High Torque Hub Motor",
                "maximum_speed": "38 km/h (24 mph)",
                "range": "70-85 km (43-53 miles)",
                "charging_time": "4 Hours",
                "color": "Matte Charcoal",
                "material": "Reinforced 6061 Folding Frame",
                "compatibility": "Compact trunk & RV storage",
                "featured": False,
                "bestseller": True,
                "new_arrival": False,
                "short_description": "Folds in 10 seconds into a compact footprint ideal for car trunks, yachts, and urban offices.",
                "description": "Equipped with an ingenious 10-second magnetic latch folding mechanism, the VoltRide Fold effortlessly slips into your car trunk or office closet. The battery is cleverly concealed within the seatpost, making charging as simple as carrying the seat inside.",
            },
            {
                "name": "VoltRide Cargo Max Heavy Hauler",
                "slug": "voltride-cargo-max",
                "SKU": "VR-EBIKE-005",
                "category": cat_objs["electric-bikes"],
                "subcategory": subcat_objs.get("electric-bikes:cargo-e-bikes"),
                "product_type": "ebike",
                "price": Decimal("3199.00"),
                "sale_price": Decimal("2899.00"),
                "cost_price": Decimal("1900.00"),
                "stock_quantity": 8,
                "brand": "VoltRide",
                "model": "Cargo Max Longtail",
                "weight": "32.0 kg",
                "dimensions": "210 x 68 x 115 cm",
                "battery_capacity": "Dual 48V 15Ah Batteries (1440Wh Combined)",
                "motor_power": "750W Heavy Duty Geared Motor (100Nm)",
                "maximum_speed": "35 km/h (22 mph)",
                "range": "120-160 km (75-100 miles)",
                "charging_time": "6 Hours (Dual Port)",
                "color": "Industrial Sand & Safety Orange",
                "material": "TIG-Welded Chromoly Steel Subframe + 6061 Alloy",
                "compatibility": "Seats up to 2 children or carries up to 200kg (440 lbs) payload",
                "featured": True,
                "bestseller": False,
                "new_arrival": True,
                "short_description": "Heavy-duty electric cargo bike supporting 200kg payload with dual battery system for family and logistics.",
                "description": "Replace your second car with the VoltRide Cargo Max. Designed with an extended rear tail, dual high-capacity battery system, and ultra-stiff payload rack, it easily transports groceries, gear, or two kids in comfort. Heavy-duty hydraulic quadruple-piston brakes ensure reliable stops even at maximum gross vehicle weight.",
            },
            {
                "name": "VoltRide Explorer Fat Tire All-Weather",
                "slug": "voltride-explorer-fat-tire",
                "SKU": "VR-EBIKE-006",
                "category": cat_objs["electric-bikes"],
                "subcategory": subcat_objs.get("electric-bikes:fat-tire-e-bikes"),
                "product_type": "ebike",
                "price": Decimal("2299.00"),
                "sale_price": Decimal("2099.00"),
                "cost_price": Decimal("1350.00"),
                "stock_quantity": 11,
                "brand": "VoltRide",
                "model": "Explorer 4.0",
                "weight": "28.5 kg",
                "dimensions": "192 x 74 x 112 cm",
                "battery_capacity": "48V 17.5Ah Samsung Cells (840Wh)",
                "motor_power": "750W Bafang Brushless Geared Hub (85Nm)",
                "maximum_speed": "45 km/h (28 mph)",
                "range": "80-105 km (50-65 miles)",
                "charging_time": "5 Hours",
                "color": "Desert Dune & Cyber Green",
                "material": "Reinforced 6061 Aluminum Fat Frame",
                "compatibility": "26x4.0 puncture-proof tires",
                "featured": False,
                "bestseller": True,
                "new_arrival": False,
                "short_description": "4-inch puncture-resistant fat tires conquer deep snow, soft beach sand, mud, and rocky gravel tracks.",
                "description": "Wherever traditional bikes get bogged down, the VoltRide Explorer thrives. Massive 26x4.0 all-terrain puncture-resistant tires float over snow, loose sand, and forest washouts with supreme traction.",
            },

            # Spare Parts: Motors, Batteries, Chargers, Electronics
            {
                "name": "VoltRide 750W High-Torque Brushless Rear Hub Motor",
                "slug": "750w-high-torque-hub-motor",
                "SKU": "VR-MTR-750W",
                "category": cat_objs["spare-parts"],
                "subcategory": subcat_objs.get("spare-parts:motors"),
                "product_type": "spare_part",
                "price": Decimal("389.00"),
                "sale_price": Decimal("349.00"),
                "cost_price": Decimal("190.00"),
                "stock_quantity": 30,
                "brand": "VoltRide OEM",
                "model": "VR-RM750-V2",
                "weight": "4.2 kg",
                "motor_power": "750W Rated / 1100W Peak (85Nm)",
                "maximum_speed": "45 km/h compatible",
                "compatibility": "VoltRide City Pro, Explorer, and standard 135mm rear dropouts with disc brake rotor mount.",
                "featured": True,
                "bestseller": True,
                "new_arrival": False,
                "short_description": "High-efficiency brushless geared rear hub motor delivering 85Nm torque and whisper-quiet operation.",
                "description": "Factory replacement or performance upgrade rear hub motor. Featuring hardened helical nylon-steel planetary gears and internal temperature sensors to guard against overheating on extended uphill grinds.",
            },
            {
                "name": "VoltRide 500W High Efficiency Hub Motor",
                "slug": "500w-brushless-hub-motor",
                "SKU": "VR-MTR-500W",
                "category": cat_objs["spare-parts"],
                "subcategory": subcat_objs.get("spare-parts:motors"),
                "product_type": "spare_part",
                "price": Decimal("289.00"),
                "sale_price": Decimal("249.00"),
                "cost_price": Decimal("140.00"),
                "stock_quantity": 22,
                "brand": "VoltRide OEM",
                "model": "VR-RM500-Eco",
                "weight": "3.5 kg",
                "motor_power": "500W Rated (60Nm)",
                "compatibility": "Compatible with VoltRide City Pro, Fold, and 36V/48V controllers.",
                "featured": False,
                "bestseller": False,
                "new_arrival": True,
                "short_description": "Reliable 500W motor with smooth low-drag freewheel clutch for smooth unassisted pedaling.",
                "description": "Standard OEM replacement for city commuters. Delivers smooth linear power curve and exceptional battery efficiency with zero magnetic drag when freewheeling.",
            },
            {
                "name": "VoltRide 48V 15Ah Samsung Cell Battery Pack",
                "slug": "48v-15ah-samsung-battery-pack",
                "SKU": "VR-BAT-4815",
                "category": cat_objs["batteries"],
                "subcategory": subcat_objs.get("batteries:48v-batteries"),
                "product_type": "spare_part",
                "price": Decimal("549.00"),
                "sale_price": Decimal("499.00"),
                "cost_price": Decimal("310.00"),
                "stock_quantity": 16,
                "brand": "VoltRide Power",
                "model": "VP-4815-S",
                "weight": "3.8 kg",
                "battery_capacity": "48V 15Ah (720Wh) Genuine Samsung 35E Cells",
                "range": "Up to 100 km per charge",
                "charging_time": "4.5 Hours with 3A Fast Charger",
                "compatibility": "Direct fit for VoltRide City Pro, Urban series, and universal Hailong downtube mounts.",
                "featured": True,
                "bestseller": True,
                "new_arrival": False,
                "short_description": "Grade-A Samsung 21700 cells with integrated smart BMS overcharge, short-circuit, and thermal protection.",
                "description": "Restore your e-bike to maximum range with this genuine VoltRide battery pack. Engineered with premium Samsung cells and a 30A continuous smart BMS system with LED fuel gauge and keylock security.",
            },
            {
                "name": "VoltRide 48V 20Ah Extended Range Battery Pack",
                "slug": "48v-20ah-extended-range-battery",
                "SKU": "VR-BAT-4820",
                "category": cat_objs["batteries"],
                "subcategory": subcat_objs.get("batteries:48v-batteries"),
                "product_type": "spare_part",
                "price": Decimal("699.00"),
                "sale_price": Decimal("649.00"),
                "cost_price": Decimal("420.00"),
                "stock_quantity": 10,
                "brand": "VoltRide Power",
                "model": "VP-4820-LR",
                "weight": "4.6 kg",
                "battery_capacity": "48V 20Ah (960Wh) High-Density LG Cells",
                "range": "Up to 140 km per charge",
                "charging_time": "5 Hours with 4A Fast Charger",
                "compatibility": "Compatible with all 48V VoltRide models, Cargo Max, and standard Shark slider bases.",
                "featured": True,
                "bestseller": False,
                "new_arrival": True,
                "short_description": "Massive 960Wh capacity for long-distance touring, commercial deliveries, and heavy cargo hauling.",
                "description": "Say goodbye to range anxiety. The 48V 20Ah extended battery packs nearly 1 kilowatt-hour of energy into a rugged fire-retardant aluminum casing with IP65 weatherproofing.",
            },
            {
                "name": "VoltRide 48V 3A Smart Fast Charger",
                "slug": "48v-3a-smart-fast-charger",
                "SKU": "VR-CHG-4803",
                "category": cat_objs["chargers"],
                "subcategory": subcat_objs.get("chargers:fast-chargers"),
                "product_type": "spare_part",
                "price": Decimal("99.00"),
                "sale_price": Decimal("85.00"),
                "cost_price": Decimal("45.00"),
                "stock_quantity": 45,
                "brand": "VoltRide Power",
                "model": "VPC-4803",
                "weight": "0.7 kg",
                "charging_time": "Charges 15Ah battery from empty to 80% in 3 hours",
                "compatibility": "Compatible with all VoltRide 48V lithium battery packs with XLR 3-pin / DC5.5 barrel connectors.",
                "featured": False,
                "bestseller": True,
                "new_arrival": False,
                "short_description": "Smart CC/CV charging with automatic trickle shutoff, active cooling fan, and aluminum heatsink body.",
                "description": "Cuts charging times by 40% compared to standard 2A chargers. Features intelligent microprocessor control that monitors cell voltage curve and prevents cell degradation.",
            },
            {
                "name": "VoltRide C900 Smart Color LCD Display",
                "slug": "c900-smart-color-lcd-display",
                "SKU": "VR-DSP-C900",
                "category": cat_objs["spare-parts"],
                "subcategory": subcat_objs.get("spare-parts:displays"),
                "product_type": "spare_part",
                "price": Decimal("129.00"),
                "sale_price": Decimal("115.00"),
                "cost_price": Decimal("60.00"),
                "stock_quantity": 38,
                "brand": "VoltRide Tech",
                "model": "C900-Pro",
                "weight": "0.22 kg",
                "compatibility": "UART / CAN bus protocols for Bafang and VoltRide sine-wave controllers. Handlebars 22.2mm - 31.8mm.",
                "featured": True,
                "bestseller": True,
                "new_arrival": False,
                "short_description": "High-contrast 3.5-inch color screen showing real-time watts, speed, trip meter, assist levels, and USB out.",
                "description": "Sunlight-readable color IPS display with IP67 waterproof certification. Includes an independent ergonomic 4-button thumb remote and a 5V 1A USB port to charge your smartphone while riding.",
            },
            {
                "name": "VoltRide 48V 25A Sine Wave Silent Controller",
                "slug": "48v-25a-sine-wave-controller",
                "SKU": "VR-CTL-4825",
                "category": cat_objs["spare-parts"],
                "subcategory": subcat_objs.get("spare-parts:controllers"),
                "product_type": "spare_part",
                "price": Decimal("149.00"),
                "sale_price": Decimal("135.00"),
                "cost_price": Decimal("75.00"),
                "stock_quantity": 28,
                "brand": "VoltRide OEM",
                "model": "VRC-4825-SW",
                "weight": "0.45 kg",
                "compatibility": "Compatible with 48V motors from 500W to 1000W with Hall sensors.",
                "featured": False,
                "bestseller": False,
                "new_arrival": False,
                "short_description": "Smooth sine-wave motor commutation delivering virtually silent acceleration and 15% better efficiency.",
                "description": "Upgrades harsh square-wave controllers to silky smooth sine wave acceleration. Features waterproof Julet plug-and-play connectors for throttle, brake cutoffs, display, and PAS sensor.",
            },
            {
                "name": "VoltRide Dual Hydraulic Disc Brake Set Front & Rear",
                "slug": "hydraulic-disc-brake-set",
                "SKU": "VR-BRK-HYD2",
                "category": cat_objs["spare-parts"],
                "subcategory": subcat_objs.get("spare-parts:brakes"),
                "product_type": "spare_part",
                "price": Decimal("189.00"),
                "sale_price": Decimal("159.00"),
                "cost_price": Decimal("90.00"),
                "stock_quantity": 35,
                "brand": "VoltRide Precision",
                "model": "HD-E800",
                "weight": "0.85 kg",
                "compatibility": "Pre-bled system with motor safety power-cutoff sensors. 180mm / 203mm rotor compatible.",
                "featured": True,
                "bestseller": True,
                "new_arrival": False,
                "short_description": "Mineral oil hydraulic 2-piston brake calipers with electronic motor cut-off sensors for high-speed safety.",
                "description": "Essential stopping power for fast e-bikes. Includes front and rear pre-bled levers, durable ceramic brake pads, steel-braided hydraulic lines, and integrated magnetic electronic motor cutoff switches.",
            },
            {
                "name": "VoltRide All-Terrain Puncture-Resistant Tire 26x4.0",
                "slug": "puncture-resistant-fat-tire-26x4",
                "SKU": "VR-TR-2640",
                "category": cat_objs["spare-parts"],
                "subcategory": subcat_objs.get("spare-parts:tires-wheels"),
                "product_type": "spare_part",
                "price": Decimal("75.00"),
                "sale_price": Decimal("65.00"),
                "cost_price": Decimal("32.00"),
                "stock_quantity": 50,
                "brand": "VoltRide Rubber",
                "model": "TreadMaster 4.0",
                "weight": "1.4 kg",
                "compatibility": "Fits 26-inch fat bike rims (80mm - 100mm rim width).",
                "featured": False,
                "bestseller": True,
                "new_arrival": False,
                "short_description": "5mm Kevlar anti-puncture belt with aggressive directional tread for snow, mud, and street durability.",
                "description": "Built specifically to handle the extra weight and torque of electric fat bikes. Features 60 TPI casing with reinforced sidewalls and reflective safety striping for night visibility.",
            },
            {
                "name": "VoltRide City Commuter Puncture-Proof Tire 27.5x2.2",
                "slug": "city-commuter-tire-27-5",
                "SKU": "VR-TR-27522",
                "category": cat_objs["spare-parts"],
                "subcategory": subcat_objs.get("spare-parts:tires-wheels"),
                "product_type": "spare_part",
                "price": Decimal("55.00"),
                "sale_price": Decimal("48.00"),
                "cost_price": Decimal("24.00"),
                "stock_quantity": 40,
                "brand": "VoltRide Rubber",
                "model": "CityGrip 2.2",
                "weight": "0.85 kg",
                "compatibility": "Compatible with VoltRide City Pro and any 27.5-inch / 650b standard rims.",
                "featured": False,
                "bestseller": False,
                "new_arrival": False,
                "short_description": "Smooth central rolling strip for low resistance with deep shoulder water evacuation channels.",
                "description": "High-mileage commuter tire rated for e-bikes up to 50 km/h (ECE-R75 certified). Low rolling resistance compound increases battery range by up to 8% compared to knobby tires.",
            },
            {
                "name": "VoltRide Heavy-Duty Double Wall Alloy Rear Rim 27.5",
                "slug": "heavy-duty-alloy-rear-rim-27-5",
                "SKU": "VR-WHL-275RW",
                "category": cat_objs["spare-parts"],
                "subcategory": subcat_objs.get("spare-parts:tires-wheels"),
                "product_type": "spare_part",
                "price": Decimal("110.00"),
                "sale_price": Decimal("95.00"),
                "cost_price": Decimal("50.00"),
                "stock_quantity": 19,
                "brand": "VoltRide Wheels",
                "model": "DW-36H",
                "weight": "1.1 kg",
                "compatibility": "36-hole spoke drilling for heavy-duty hub motors and disc brake rotors.",
                "featured": False,
                "bestseller": False,
                "new_arrival": False,
                "short_description": "Reinforced double-wall anodized aluminum rim built to endure high torque and rough urban potholes.",
                "description": "Engineered with eyeleted 36-hole spoke drillings to eliminate spoke pull-through under sudden motor torque and cargo loading.",
            },
            {
                "name": "VoltRide Waterproof Universal Thumb Throttle",
                "slug": "waterproof-thumb-throttle",
                "SKU": "VR-THR-01",
                "category": cat_objs["spare-parts"],
                "subcategory": subcat_objs.get("spare-parts:throttles"),
                "product_type": "spare_part",
                "price": Decimal("35.00"),
                "sale_price": Decimal("28.00"),
                "cost_price": Decimal("12.00"),
                "stock_quantity": 60,
                "brand": "VoltRide OEM",
                "model": "TT-130X",
                "weight": "0.08 kg",
                "compatibility": "Fits 22.2mm standard handlebars. 3-pin waterproof quick-release Julet connector.",
                "featured": False,
                "bestseller": True,
                "new_arrival": False,
                "short_description": "Ergonomic silicone thumb lever offering precise throttle modulation without wrist fatigue.",
                "description": "Smooth linear hall sensor thumb throttle with anti-slip rubber texture. IP66 waterproof connection ensures flawless throttle response in heavy rainstorms.",
            },
            {
                "name": "VoltRide 1200 Lumen Dual Beam LED Headlight & Horn",
                "slug": "1200-lumen-led-headlight-horn",
                "SKU": "VR-LGT-1200",
                "category": cat_objs["lighting"],
                "subcategory": subcat_objs.get("lighting:headlights"),
                "product_type": "spare_part",
                "price": Decimal("65.00"),
                "sale_price": Decimal("55.00"),
                "cost_price": Decimal("26.00"),
                "stock_quantity": 42,
                "brand": "VoltRide Vision",
                "model": "LumensMax 1200",
                "weight": "0.26 kg",
                "compatibility": "Direct wiring to 36V-60V main e-bike battery with handlebar toggle switch.",
                "featured": False,
                "bestseller": False,
                "new_arrival": True,
                "short_description": "Anti-glare automotive German StVZO standard beam with piercing 105dB integrated electric horn.",
                "description": "Illuminates up to 150 meters ahead without blinding oncoming cyclists and drivers. Features an internal step-down regulator accepting 36V to 60V directly from your main e-bike battery.",
            },

            # Accessories & Gear
            {
                "name": "VoltRide Aero Smart Commuter Helmet with Rear Brake Light",
                "slug": "aero-smart-commuter-helmet",
                "SKU": "VR-ACC-HLM1",
                "category": cat_objs["accessories"],
                "subcategory": subcat_objs.get("accessories:helmets"),
                "product_type": "accessory",
                "price": Decimal("119.00"),
                "sale_price": Decimal("95.00"),
                "cost_price": Decimal("48.00"),
                "stock_quantity": 30,
                "brand": "VoltRide Gear",
                "model": "AeroGuard Pro",
                "weight": "0.36 kg",
                "dimensions": "Sizes M (54-58cm) & L (58-62cm)",
                "compatibility": "CPSC and CE EN1078 certified for e-bike speeds up to 45 km/h.",
                "featured": True,
                "bestseller": True,
                "new_arrival": True,
                "short_description": "In-mold EPS foam shell with integrated automatic accelerometer brake light and magnetic visor.",
                "description": "The safest helmet for high-speed e-bike commuters. An internal 3-axis accelerometer detects deceleration and instantly triggers an ultra-bright red warning light on the rear of the helmet.",
            },
            {
                "name": "VoltRide Heavy-Duty Hardened Steel Folding Lock",
                "slug": "hardened-steel-folding-lock",
                "SKU": "VR-ACC-LCK1",
                "category": cat_objs["accessories"],
                "subcategory": subcat_objs.get("accessories:locks-security"),
                "product_type": "accessory",
                "price": Decimal("89.00"),
                "sale_price": Decimal("75.00"),
                "cost_price": Decimal("38.00"),
                "stock_quantity": 40,
                "brand": "VoltRide Security",
                "model": "SecureLock 85",
                "weight": "1.25 kg",
                "dimensions": "85 cm circumference unfolded",
                "compatibility": "Frame mounting bracket with anti-rattle strap included.",
                "featured": False,
                "bestseller": True,
                "new_arrival": False,
                "short_description": "Sold Secure Gold rated 5mm heat-treated hardened steel bars resist bolt cutters and drill attacks.",
                "description": "Protect your e-bike investment with Sold Secure Gold anti-theft certification. Compact folding design mounts tightly to your bike water bottle bosses with zero frame vibration.",
            },
            {
                "name": "VoltRide Waterproof Roll-Top Pannier Bag 25L",
                "slug": "waterproof-roll-top-pannier-bag-25l",
                "SKU": "VR-ACC-BAG1",
                "category": cat_objs["accessories"],
                "subcategory": subcat_objs.get("accessories:panniers-bags"),
                "product_type": "accessory",
                "price": Decimal("79.00"),
                "sale_price": Decimal("68.00"),
                "cost_price": Decimal("32.00"),
                "stock_quantity": 34,
                "brand": "VoltRide Cargo",
                "model": "DryPack 25",
                "weight": "0.95 kg",
                "dimensions": "25 Liter Capacity (42 x 32 x 18 cm)",
                "compatibility": "Quick-lock click system fits all standard 8mm-16mm rear pannier racks.",
                "featured": False,
                "bestseller": False,
                "new_arrival": False,
                "short_description": "100% waterproof TPU welded seams with padded 15-inch laptop sleeve and shoulder carry strap.",
                "description": "Submersible waterproof roll-top construction keeps your work laptop, change of clothes, and documents completely dry through torrential downpours. Snaps onto your rear rack in two seconds.",
            },
            {
                "name": "VoltRide Anti-Vibration Aluminum Phone Mount with USB-C Port",
                "slug": "aluminum-phone-mount-usb-charging",
                "SKU": "VR-ACC-PHN1",
                "category": cat_objs["accessories"],
                "subcategory": subcat_objs.get("accessories:phone-mounts"),
                "product_type": "accessory",
                "price": Decimal("49.00"),
                "sale_price": Decimal("39.00"),
                "cost_price": Decimal("18.00"),
                "stock_quantity": 55,
                "brand": "VoltRide Tech",
                "model": "ShockGrip Pro",
                "weight": "0.18 kg",
                "compatibility": "Holds smartphones 4.7\" to 6.9\". Handlebars 22mm to 31.8mm.",
                "featured": False,
                "bestseller": True,
                "new_arrival": False,
                "short_description": "CNC machined aluminum with 4 silicone vibration dampers to safeguard smartphone optical image stabilization.",
                "description": "High-frequency road vibrations can ruin optical smartphone cameras. The ShockGrip Pro utilizes automotive-grade silicone dampers to isolate your camera sensor while providing rock-solid GPS viewing.",
            },
            {
                "name": "VoltRide Portable High-Pressure Electric Tire Pump",
                "slug": "portable-electric-tire-pump",
                "SKU": "VR-ACC-PMP1",
                "category": cat_objs["accessories"],
                "subcategory": subcat_objs.get("accessories:pumps-tools"),
                "product_type": "accessory",
                "price": Decimal("69.00"),
                "sale_price": Decimal("59.00"),
                "cost_price": Decimal("28.00"),
                "stock_quantity": 38,
                "brand": "VoltRide Tools",
                "model": "AirMax 150",
                "weight": "0.48 kg",
                "compatibility": "Presta and Schrader valves. Pumps up to 150 PSI with digital auto-stop.",
                "featured": False,
                "bestseller": False,
                "new_arrival": True,
                "short_description": "Rechargeable pocket inflator fills e-bike and fat tires in under two minutes with auto-pressure shutoff.",
                "description": "Never get stranded with a soft tire again. Preset your desired tire pressure (up to 150 PSI), connect to your valve, and the digital sensor inflates accurately to the exact decimal before shutting off automatically.",
            },
            {
                "name": "VoltRide Wide-Angle HD Handlebar Rearview Mirror Set",
                "slug": "wide-angle-handlebar-mirror-set",
                "SKU": "VR-ACC-MIR1",
                "category": cat_objs["accessories"],
                "subcategory": subcat_objs.get("accessories:phone-mounts"),
                "product_type": "accessory",
                "price": Decimal("38.00"),
                "sale_price": Decimal("29.00"),
                "cost_price": Decimal("14.00"),
                "stock_quantity": 48,
                "brand": "VoltRide Vision",
                "model": "ClearSight HD",
                "weight": "0.19 kg",
                "compatibility": "Bar-end mount fits internal handlebar diameter 14.8mm to 23mm.",
                "featured": False,
                "bestseller": False,
                "new_arrival": False,
                "short_description": "Blast-resistant automotive glass lens with 360-degree ball joint adjustment for crystal clear rear vision.",
                "description": "Vital safety accessory for road commuters sharing lanes with speeding traffic. Anti-glare blue coating reduces nighttime headlight glare by 50%.",
            },
        ]

        created_products = []
        for pdata in products_data:
            # Check or create product
            p, created = Product.objects.get_or_create(
                slug=pdata["slug"],
                defaults=pdata
            )
            created_products.append(p)

            # Ensure product image exists
            img_path = os.path.join(settings.MEDIA_ROOT, 'products', f"{p.slug}.jpg")
            if not os.path.exists(img_path):
                theme = "cyan" if p.product_type == "ebike" else ("green" if p.product_type == "spare_part" else "blue")
                create_product_graphic(
                    img_path,
                    title=p.name,
                    category_name=p.category.name,
                    subtitle=p.short_description[:80] + "..." if len(p.short_description) > 80 else p.short_description,
                    color_theme=theme
                )

            # Link primary product image
            rel_media_path = f"products/{p.slug}.jpg"
            ProductImage.objects.get_or_create(
                product=p,
                is_primary=True,
                defaults={"image": rel_media_path, "alt_text": p.name}
            )

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(created_products)} realistic products with images."))

        # 4. 30 Realistic Product Reviews
        reviews_data = [
            (0, "VoltRide City Pro Electric Bike", 5, "Game changer for my daily 15-mile commute!", "I sold my second car after buying the City Pro 4 months ago. The torque sensor is exceptionally responsive—it amplifies pedaling naturally without the jerky surge of cheaper cadence sensors. Battery easily lasts 3 full days of commuting. Outstanding build quality!"),
            (1, "VoltRide City Pro Electric Bike", 5, "Best commuter bike on the market period", "Arrived in a well-padded box 90% assembled. Took only 20 minutes to adjust handlebars and pedals. Hydraulic disc brakes have serious stopping power in rain. You won't regret buying this."),
            (2, "VoltRide City Pro Electric Bike", 4, "Great bike, seat is slightly firm for long rides", "Performance and motor are 10/10. My only small critique is the stock saddle which is somewhat stiff on 30km+ rides, so I swapped for a gel seat. Otherwise motor assistance and range are exactly as claimed."),
            (3, "VoltRide Mountain X All-Terrain E-Bike", 5, "160Nm torque climbs hills like a mountain goat!", "Took the Mountain X to Colorado mountain trails last weekend. The mid-drive power is unbelievable. Sits glued to loose dirt tracks and the suspension absorbs massive drop-offs smoothly. Pure thrill."),
            (4, "VoltRide Mountain X All-Terrain E-Bike", 5, "Top tier engineering and rugged durability", "I weigh 105 kg and normally e-bikes struggle on steep switchbacks with my weight. The Mountain X didn't even drop a sweat. Battery consumption was better than expected after 45 miles of heavy climbing."),
            (5, "VoltRide Mountain X All-Terrain E-Bike", 5, "Feels like an electric motocross machine", "The build quality of the 7005 alloy frame and 4-piston brakes rival bikes that cost twice as much. Worth every penny for serious trail riders."),
            (6, "VoltRide Urban Lite Commuter", 5, "Finally an e-bike I can actually carry up stairs!", "Living in a 3rd floor walkup apartment with no elevator made normal 30kg e-bikes impossible. At under 17kg, the Urban Lite is super easy to carry over my shoulder. Elegant minimalist styling."),
            (7, "VoltRide Urban Lite Commuter", 4, "Smooth and stealthy, looks like an ordinary acoustic bike", "People on the bike lane don't even realize it's electric until I breeze past on an incline. Battery is small but charges in 3.5 hours on my desk at work."),
            (8, "VoltRide Fold Compact E-Bike", 5, "Fits in my Honda Civic trunk with room to spare", "The magnetic folding hinges are rock solid when locked. No squeaks or frame flex during acceleration. Perfect for park-and-ride commutes into downtown traffic."),
            (9, "VoltRide Fold Compact E-Bike", 5, "Clever seatpost battery design!", "Removing the seatpost to charge inside hotels while on business trips is genius. The 500W motor has plenty of punch to tackle highway overpass inclines."),
            (10, "VoltRide Cargo Max Heavy Hauler", 5, "Replaced our minivan for all local school runs", "I carry my 5-year-old and 7-year-old on the back with the cargo rail cushions. They love it! The dual battery setup gives immense peace of mind and never drops below 60% after a full day of errands."),
            (11, "VoltRide Cargo Max Heavy Hauler", 5, "Sturdy workhorse for my courier business", "Carrying 120 lbs of packages daily in Chicago. The center kickstand is super stable during loading and hydraulic brakes stop reliably on downhill gradients."),
            (12, "VoltRide Explorer Fat Tire All-Weather", 5, "Traction on wet sand and snow is unbelievable", "Rode this along the Pacific coast beach at low tide. Glides over soft sand where standard tires sink immediately. 840Wh battery has tremendous endurance."),
            (13, "VoltRide Explorer Fat Tire All-Weather", 4, "Heavy frame but rides like a tank", "You need muscle if you ever have to lift it onto a car rack, but when rolling on 4-inch tires, it feels invincible over potholes, railroad tracks, and curbs."),
            (14, "VoltRide 750W High-Torque Brushless Rear Hub Motor", 5, "Replaced my burnt out generic hub—night and day difference", "Direct drop-in replacement. Whisper quiet compared to my previous motor and pulls uphill with noticeably higher sustained torque. Thermals stayed cool after 40 minutes of continuous throttling."),
            (15, "VoltRide 750W High-Torque Brushless Rear Hub Motor", 5, "High quality internal nylon-steel gears", "Opened the casing to inspect before installation and was very impressed by the precision bearings and waterproof seals. Added 10 km/h to my top speed."),
            (16, "VoltRide 500W High Efficiency Hub Motor", 5, "Zero magnetic drag when pedaling unassisted", "Freewheel mechanism is genuinely frictionless. If the battery runs flat, pedaling feels almost identical to a normal bicycle."),
            (17, "VoltRide 48V 15Ah Samsung Cell Battery Pack", 5, "Restored my e-bike to 60 miles range!", "My old generic Chinese battery degraded after 1 year. This Samsung cell pack has been flawless after 50 charge cycles with zero noticeable capacity drop."),
            (18, "VoltRide 48V 15Ah Samsung Cell Battery Pack", 5, "Solid aluminum casing and reliable keylock", "Snaps firmly onto the base plate with zero rattle over bumpy roads. Voltage output remains steady even when climbing under full 750W motor draw."),
            (19, "VoltRide 48V 20Ah Extended Range Battery Pack", 5, "Incredible capacity—I only charge once a week now", "I commute 18 miles round trip daily. With this 960Wh beast, I literally charge every Sunday night and forget about it until the following weekend!"),
            (20, "VoltRide 48V 3A Smart Fast Charger", 5, "Cuts charging time by nearly two hours", "The built-in cooling fan keeps the aluminum brick comfortably warm rather than scorching hot like cheap silent plastic chargers. Shuts off promptly at 54.6V."),
            (21, "VoltRide 48V 3A Smart Fast Charger", 4, "Fan has a slight hum, but charging speed is worth it", "Not silent because of the cooling fan, but it prevents battery overheating and gets me back on the road in half the time."),
            (22, "VoltRide C900 Smart Color LCD Display", 5, "Crystal clear in direct midday sunlight", "The IPS screen is readable even wearing polarized sunglasses. Love having real-time wattage display to see exactly how much battery I am consuming."),
            (23, "VoltRide 48V 25A Sine Wave Silent Controller", 5, "Silenced motor noise completely!", "My old controller produced an annoying metallic buzzing buzz at low speeds. Swapped in this sine wave unit and the bike is now as quiet as a Tesla."),
            (24, "VoltRide Dual Hydraulic Disc Brake Set Front & Rear", 5, "One-finger braking with instant motor cutoff", "Pre-bled lines made installation take 15 minutes. Motor cuts out the split second you touch the lever. Exceptional safety upgrade."),
            (25, "VoltRide All-Terrain Puncture-Resistant Tire 26x4.0", 5, "Zero punctures in 1,200 miles through glass-strewn streets", "The 5mm Kevlar layer actually works. I pulled out a two-inch rusty nail that bent sideways without puncturing the inner tube. Best tire investment."),
            (26, "VoltRide City Commuter Puncture-Proof Tire 27.5x2.2", 5, "Fast rolling and grips wet asphalt tenaciously", "Noticeable increase in coasting distance. Wet painted crosswalk lines don't cause sudden front-wheel slippage anymore."),
            (27, "VoltRide Waterproof Universal Thumb Throttle", 5, "Smooth progressive response without hair-trigger jerkiness", "Comfortable thumb ergonomic paddle. Rode in two heavy thunderstorms with zero electrical glitches or throttle sticking."),
            (28, "VoltRide Aero Smart Commuter Helmet with Rear Brake Light", 5, "Motorists give me noticeable extra distance now", "The automatic deceleration brake light is brilliant. Several drivers have commented at red lights how bright and visible the rear light is."),
            (29, "VoltRide Heavy-Duty Hardened Steel Folding Lock", 5, "Survived an attempted theft outside the train station", "Someone tried cutting it with bolt cutters while I was at dinner. There were superficial scratches on the rubber coating but the steel links were completely untouched!"),
        ]

        review_objs = []
        for idx, (user_idx, prod_name, rating, title, comment) in enumerate(reviews_data):
            try:
                prod = Product.objects.get(name=prod_name)
                u = created_users[idx % len(created_users)]
                review, _ = ProductReview.objects.get_or_create(
                    user=u,
                    product=prod,
                    defaults={
                        "rating": rating,
                        "title": title,
                        "comment": comment,
                        "verified_purchase": True,
                        "approved": True,
                    }
                )
                review_objs.append(review)
            except Product.DoesNotExist:
                continue

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(review_objs)} authentic product reviews."))

        # 5. Blog Categories and 12 Required Blog Posts
        blog_cats = [
            ("Buying Guides", "buying-guides", "Expert recommendations on choosing electric bikes and matching specs to your lifestyle."),
            ("Maintenance & Care", "maintenance-care", "Practical maintenance schedules, cleaning tips, and DIY service guides."),
            ("Battery & Electrical", "battery-electrical", "Technical deep-dives into lithium battery longevity, chargers, and motor controllers."),
            ("Safety & Commuting", "safety-commuting", "Urban safety strategies, rules of the road, and defensive cycling techniques."),
        ]
        bcat_map = {}
        for bname, bslug, bdesc in blog_cats:
            bcat, _ = BlogCategory.objects.get_or_create(
                slug=bslug,
                defaults={"name": bname, "description": bdesc}
            )
            bcat_map[bslug] = bcat

        blog_posts_data = [
            {
                "title": "How to Choose the Right Electric Bike",
                "slug": "how-to-choose-the-right-electric-bike",
                "category": bcat_map["buying-guides"],
                "tags": "Buying Guide, E-Bikes, Commuting, Mountain",
                "excerpt": "A complete beginner's roadmap to choosing the ideal e-bike frame, motor configuration, and battery capacity based on your riding terrain and budget.",
                "content": """
### Finding Your Ideal Electric Ride

With dozens of e-bike configurations on the market—ranging from ultra-lightweight city commuters to dual-suspension mountain beasts—finding the right model requires matching your daily riding habits with the appropriate frame geometry, motor placement, and battery specifications.

#### 1. Define Your Primary Riding Terrain
* **Urban Commuting:** Prioritize lightweight frames, puncture-resistant road tires, integrated LED lights, and mudguards. Models like the **VoltRide City Pro** excel here.
* **Trail & Off-Road:** Demands dual suspension, high motor torque (85Nm+), and knobby tires to absorb roots, rocks, and steep climbs.
* **Multi-Modal Transit:** If you combine biking with train trips or car trunks, a folding e-bike with quick magnetic latches is essential.
* **Cargo & Family:** Longtail cargo frames with heavy payload capacity allow carrying children, weekly groceries, or delivery cargo.

#### 2. Hub Motor vs. Mid-Drive Motor
One of the most critical decisions is motor architecture:
* **Rear Hub Motors:** Positioned directly in the rear wheel hub. They provide smooth, push-like acceleration and require minimal chain maintenance. Excellent for flat to moderately hilly city riding.
* **Mid-Drive Motors:** Located near the bottom bracket pedals. They send power through your bike's gears, allowing you to downshift for monumental climbing torque on extreme mountain trails.

#### 3. Battery Capacity & Range Realities
Don't just look at advertised maximum ranges. Check the Watt-hour rating calculated as:
$$\\text{Watt-hours (Wh)} = \\text{Voltage (V)} \\times \\text{Amp-hours (Ah)}$$
A 48V 15Ah battery provides 720Wh of capacity, typically translating to 50–70 real-world miles under pedal assist.

#### Conclusion
Test riding and selecting a model engineered with reputable components (Samsung cells, Shimano drivetrains, hydraulic brakes) ensures long-lasting safety, dependable warranty support, and maximum riding joy.
                """
            },
            {
                "title": "E-Bike Battery Care Guide",
                "slug": "e-bike-battery-care-guide",
                "category": bcat_map["battery-electrical"],
                "tags": "Battery, Maintenance, Longevity, Safety",
                "excerpt": "Learn how proper charging cycles, temperature management, and storage techniques can double the lifespan of your lithium-ion battery.",
                "content": """
### Maximizing the Life and Health of Your Battery

Your lithium-ion battery pack is the single most valuable component of your electric bicycle. Following basic electrochemical care guidelines can extend its useful lifespan from 3 years to over 6 years without noticeable capacity loss.

#### 1. The 20% to 80% Sweet Spot
Modern lithium-ion cells experience the highest internal chemical stress when held at 100% full charge or drained below 15%. For daily commuting:
* Avoid leaving the charger plugged in overnight once the green light illuminates.
* Recharge when you reach approximately 20–25% battery remaining.
* Perform a 100% full balancing charge once every 6–8 weeks to re-balance individual cell banks.

#### 2. Temperature is the Enemy
Extreme temperatures degrade lithium cathode structures rapidly:
* **Charging:** Never charge a freezing battery (below 0°C / 32°F). Bring the pack inside to reach room temperature before connecting the charger.
* **Summer Sun:** Never store your battery inside a hot car trunk or in direct baking midday sunlight.

#### 3. Long-Term Storage Best Practices
If storing your e-bike over winter months:
1. Charge or discharge the pack to approximately 50% capacity (around 48V on a 48V nominal system).
2. Store in a dry room between 10°C and 20°C (50°F–68°F).
3. Check and top-up the battery for 30 minutes every 60 days to prevent sleep-mode voltage collapse.

#### Conclusion
A well-maintained battery provides thousands of miles of dependable assistance, preserving your wallet and the environment alike.
                """
            },
            {
                "title": "How Far Can an Electric Bike Travel?",
                "slug": "how-far-can-an-electric-bike-travel",
                "category": bcat_map["buying-guides"],
                "tags": "Range, Efficiency, Commuting, Tips",
                "excerpt": "Unraveling the mystery of e-bike range: how rider weight, wind resistance, tire pressure, and assist levels impact your mileage.",
                "content": """
### The Science Behind Real-World E-Bike Range

One of the most frequent customer inquiries is: *"How many miles can I actually ride on a single charge?"* While manufacturers often quote theoretical ranges of 60 to 100 miles, real-world mileage depends on dynamic physics.

#### Key Factors Influencing Energy Consumption
1. **Assist Level & Cadence:** Riding in Eco Mode (providing 50% assist) consumes approximately 8–10 Wh per mile. Riding in full Throttle or Turbo mode at 28 mph consumes 22–28 Wh per mile.
2. **Aerodynamic Drag:** Wind resistance increases exponentially with speed. Cruising at 20 mph requires nearly double the energy of cruising at 14 mph.
3. **Tire Pressure:** Soft tires dramatically increase rolling resistance. Maintaining correct PSI (e.g., 40–50 PSI for road tires, 18–25 PSI for fat tires) can increase range by 12%.
4. **Terrain Incline:** Climbing a 6% grade demands 4x more energy than cruising on flat asphalt.

#### Practical Formula for Estimating Range
To calculate realistic range:
$$\\text{Real-World Range (Miles)} \\approx \\frac{\\text{Battery Watt-Hours}}{\\text{Average Wh/mile (12 - 16)}}$$
For example, with a **720Wh VoltRide pack**:
$$\\frac{720\\text{ Wh}}{14\\text{ Wh/mile}} \\approx 51.4\\text{ miles of vigorous mixed riding.}$$

#### How to Squeeze Maximum Mileage
* Pedal in a low mechanical gear when starting from a dead stop.
* Use smooth, gradual throttle inputs instead of hammering full acceleration.
* Keep your chain clean and properly lubricated.
                """
            },
            {
                "title": "E-Bike Maintenance Checklist",
                "slug": "e-bike-maintenance-checklist",
                "category": bcat_map["maintenance-care"],
                "tags": "Maintenance, Safety, DIY, Checklist",
                "excerpt": "A weekly, monthly, and seasonal maintenance checklist to keep your e-bike running smoothly, safely, and squeak-free.",
                "content": """
### Preventive Maintenance Keeps You Rolling Safely

Because electric bikes travel at higher average speeds and weigh more than traditional bicycles, regular preventative checks are critical for safety and component longevity.

#### Weekly 5-Minute "M-Check"
* **Brakes:** Squeeze both brake levers firmly. Levers should engage crisply without touching the handlebars. Check pad thickness (replace if under 1.5mm).
* **Tire Pressure:** Check tire sidewall for recommended PSI and top up with a digital floor pump.
* **Bolt Torque:** Verify quick-release skewers or axle nuts are securely torqued.
* **Battery Mount:** Ensure battery clicks securely into its locking bracket without looseness or vibration.

#### Monthly Service Tasks
1. **Clean & Lube Drivetrain:** Wipe chain with a degreaser and apply dedicated e-bike synthetic wet or dry lubricant. Wipe away excess to prevent grit buildup.
2. **Spoke Tension:** Gently squeeze adjacent spoke pairs. Loose spokes lead to out-of-true wheels and broken spoke nipples under motor torque.
3. **Electrical Connectors:** Inspect wiring harnesses around the handlebars and bottom bracket for wear or chafing.

#### Seasonal Overhaul
* Check brake fluid for contamination (bleed hydraulic mineral oil if brake feel is spongy).
* Inspect headset bearings and bottom bracket for play or gritty rotation.
* Update controller firmware or display settings if software updates are released.
                """
            },
            {
                "title": "Understanding Motor Power",
                "slug": "understanding-motor-power",
                "category": bcat_map["battery-electrical"],
                "tags": "Motors, Watts, Torque, Technical",
                "excerpt": "Demystifying 250W vs 500W vs 750W ratings, continuous vs peak wattage, and why torque (Nm) matters more than nominal watts.",
                "content": """
### Watts vs. Newton-Meters: What Truly Powers Your E-Bike?

When browsing electric bicycles, wattage numbers are stamped prominently everywhere: 250W, 500W, 750W, 1000W. But what do these ratings actually mean on the road?

#### Continuous (Nominal) vs. Peak Power
* **Nominal / Continuous Power:** The sustained power a motor can produce indefinitely without overheating its copper stator windings.
* **Peak Power:** The short-burst power delivered during hard acceleration or steep hill climbing. A motor rated at 500W continuous often peaks at 850W–900W for 30–60 seconds!

#### Why Torque (Nm) is King for Hill Climbing
While Watts dictate your top cruising speed on flat ground, **Newton-Meters (Nm) of torque** dictate your climbing capability and off-the-line acceleration:
* **40–50 Nm:** Standard city commuter; adequate for gentle inclines and flat pavement.
* **65–85 Nm:** High-performance commuter like the **VoltRide City Pro**; handles moderate city hills with ease.
* **120–160 Nm:** Heavy-duty off-road and cargo motors like the **VoltRide Mountain X**; capable of propelling rider and gear up 30-degree gravel walls.

#### Legal Classifications Explained
* **Class 1:** Pedal-assist only, motor cuts off at 20 mph (32 km/h).
* **Class 2:** Throttle-actuated, motor cuts off at 20 mph.
* **Class 3:** Pedal-assist only (with speedometer), motor cuts off at 28 mph (45 km/h).
                """
            },
            {
                "title": "City E-Bikes vs Mountain E-Bikes",
                "slug": "city-e-bikes-vs-mountain-e-bikes",
                "category": bcat_map["buying-guides"],
                "tags": "Comparison, City, Mountain, Buying Guide",
                "excerpt": "An in-depth breakdown comparing geometry, suspension, tires, and motor placement between urban commuters and rugged trail machines.",
                "content": """
### Choosing Your Platform: Asphalt Warrior or Trail Conqueror?

Are you better off purchasing a dedicated urban commuter or an aggressive e-mountain bike? Here is how their engineering architectures differ.

#### Frame Geometry & Riding Posture
* **City E-Bikes:** Feature upright or slightly forward ergonomic geometry. This raises your eye level, allowing you to clearly see vehicle traffic, pedestrians, and road obstacles in heavy traffic.
* **Mountain E-Bikes (eMTB):** Feature slacker headtube angles and longer wheelbases for stability when plummeting down steep rock gardens and bermed corners.

#### Suspension Systems
* **City Commuters:** Typically use rigid forks or short-travel (50–80mm) front suspension forks tuned to smooth out asphalt seams and potholes.
* **Mountain Bikes:** Utilize full air-sprung suspension (130–160mm travel) with adjustable rebound and compression lockout to cushion high-impact landings.

#### Tires & Rolling Resistance
City bikes use narrower, smooth-center puncture-proof tires (such as 27.5 x 2.0) for low rolling resistance and extended battery range. Mountain bikes sport wide, knobby tires (2.4 to 2.8 inches or 4.0 fat tires) running at lower pressures to maximize mechanical grip on slippery dirt, roots, and rocks.

#### Summary Recommendation
If 85%+ of your riding is pavement, bike paths, and graded gravel, choose a **City E-Bike** for better efficiency, integrated lights, and fenders. If your heart is set on singletrack trails and backcountry exploration, invest in a dedicated **Mountain E-Bike**.
                """
            },
            {
                "title": "How to Extend Battery Life",
                "slug": "how-to-extend-battery-life",
                "category": bcat_map["battery-electrical"],
                "tags": "Battery, Tips, Longevity, Savings",
                "excerpt": "Ten actionable habits that prevent capacity fade and save you hundreds of dollars in premature replacement costs.",
                "content": """
### 10 Proven Rules to Make Your Battery Last for Years

Lithium battery degradation is not an unavoidable mystery. By understanding basic cell chemistry, you can easily preserve 85%+ of your original capacity well past year four.

1. **Avoid Zero-Percent Depletion:** Deep discharge down to 0V is the fastest way to cause permanent copper dendrite formation and cell death. Charge when you see 1-2 bars remaining.
2. **Do Not Store at 100%:** Leaving a battery fully saturated at 4.2V per cell in a warm garage during summer causes rapid electrolyte oxidation.
3. **Use the Right Charger:** Always use genuine manufacturer chargers with proper voltage tolerances. Cheap aftermarket chargers often lack precise voltage cutoffs.
4. **Pedal When Accelerating from a Stop:** Starting from zero on throttle alone draws maximum peak current (up to 25A–30A), heating up the battery pack. Giving 2-3 pedal strokes eases this thermal shock.
5. **Keep Tire Pressure Optimal:** Under-inflated tires place high drag on the motor, demanding continuous high battery discharge.
6. **Clean Battery Terminals:** Use electrical contact cleaner periodically to clean the discharge blade pins and prevent resistance heating.
7. **Store in Climate-Controlled Environments:** Never leave the battery in an uninsulated shed during freezing sub-zero winters.
                """
            },
            {
                "title": "Common E-Bike Problems and Solutions",
                "slug": "common-e-bike-problems-and-solutions",
                "category": bcat_map["maintenance-care"],
                "tags": "Troubleshooting, DIY, Repairs, Diagnostics",
                "excerpt": "A handy troubleshooting manual for error codes, power cutoffs, brake squeaks, throttle hesitations, and display issues.",
                "content": """
### DIY Troubleshooting: Diagnosing Common Issues at Home

Modern electric bicycles are remarkably reliable, but when an electrical gremlin appears, systematic diagnostics save time and repair shop fees.

#### Problem 1: Motor Cuts Out Intermittently
* **Cause A: Brake Sensor Misalignment.** Hydraulic brake levers have magnetic cutoff switches. If the lever doesn't snap back completely or the magnet has shifted, the controller thinks you are braking and cuts motor power.
* **Fix:** Inspect the brake lever return spring and ensure the brake sensor cable is firmly seated.
* **Cause B: Loose Battery Terminal.** If you hit a bump and power shuts down, check the battery key lock and cradle pins for physical play.

#### Problem 2: Display Shows Error Code 07 or Motor Hall Sensor Error
* **Cause:** The waterproof 9-pin motor connector near the rear chainstay has loosened.
* **Fix:** Firmly press the waterproof arrow-to-arrow connector together until the alignment arrows meet completely.

#### Problem 3: Throttle Doesn't Respond but Pedal Assist Works
* **Cause:** PAS sensor and throttle use independent 5V signaling wires. The throttle magnet or signal wire may be damaged.
* **Fix:** Check display settings to confirm throttle is enabled, and test the 3-pin Julet throttle plug with a multimeter.

#### Problem 4: Loud Brake Squeal
* **Cause:** Contamination of brake pads with chain oil, road grime, or improper bed-in procedure.
* **Fix:** Clean rotors with 99% isopropyl alcohol and sand the brake pads lightly with clean 220-grit sandpaper, or install fresh resin pads.
                """
            },
            {
                "title": "How to Choose the Correct Charger",
                "slug": "how-to-choose-the-correct-charger",
                "category": bcat_map["battery-electrical"],
                "tags": "Chargers, Voltage, Amperage, Safety",
                "excerpt": "Matching voltage ratings, pin configurations, amp output, and smart charging curves to keep your e-bike safe and fast.",
                "content": """
### Charger Specifications: Why Voltage Matching is Non-Negotiable

Connecting the wrong charger can permanently ruin your battery pack or create a severe fire hazard. Here is how to read charger specifications accurately.

#### Nominal Voltage vs. Maximum Charging Voltage
* A **36V Nominal Battery** (10S lithium configuration) requires a **42.0V** charger.
* A **48V Nominal Battery** (13S lithium configuration) requires a **54.6V** charger.
* A **52V Nominal Battery** (14S lithium configuration) requires a **58.8V** charger.

*Never* attempt to charge a 48V battery with a 52V charger, as this will trigger severe BMS overvoltage fault protection or cell damage.

#### Understanding Amperage (2A vs 3A vs 5A)
Amperage dictates how quickly electrical current fills the battery:
* **2-Amp Charger:** Gentle, slow charging. Ideal for smaller 10Ah batteries (5-6 hours).
* **3-Amp Charger:** The sweet spot for modern 14Ah–17.5Ah packs (4-5 hours).
* **5-Amp Fast Charger:** Recommended only for large packs (20Ah+) with cells rated for high charge currents.

#### Pin Connector Standards
Always verify your physical plug format: 3-pin XLR, DC5.5x2.1mm barrel, DC5.5x2.5mm, or ST-3 pin. VoltRide genuine chargers feature polarized connections to prevent reverse polarity accidents.
                """
            },
            {
                "title": "Essential E-Bike Spare Parts",
                "slug": "essential-e-bike-spare-parts",
                "category": bcat_map["maintenance-care"],
                "tags": "Spare Parts, Gear, Emergency, DIY",
                "excerpt": "The essential spare parts every electric bike owner should keep in their workshop or saddlebag for zero downtime.",
                "content": """
### Be Prepared: The Rider's Emergency Spare Parts Kit

Unlike traditional bicycles, waiting weeks for a specialized e-bike replacement part can leave you stranded without daily transportation. Here are the components smart owners keep on hand:

#### 1. Spare Inner Tube & Tire Levers
Because e-bike rear wheels house heavy hub motors and wiring cables, roadside repairs require specialized steel-core tire levers and heavy-duty puncture-resistant butyl tubes.

#### 2. Extra Set of Brake Pads
Electric bikes consume brake pads two to three times faster than acoustic bicycles due to their weight and average traveling velocity. Keeping a spare set of semi-metallic or ceramic pads guarantees you never ride on bare metal backing plates.

#### 3. Replacement Thumb Throttle
Throttles are vulnerable in the event of an accidental handlebar tip-over. Having a plug-and-play waterproof thumb throttle prevents being stuck without power assist.

#### 4. Backup Smart Fast Charger
Keep one charger plugged in at home and a secondary compact charger in your office desk drawer to eliminate range worries during unforeseen evening errands.

#### 5. Master Chain Link & Chain Tool
Motor torque puts substantial stress on bicycle chains. A 9-speed, 10-speed, or 11-speed master quick-link allows instant trailside chain repair in seconds.
                """
            },
            {
                "title": "Electric Bike Safety Tips",
                "slug": "electric-bike-safety-tips",
                "category": bcat_map["safety-commuting"],
                "tags": "Safety, Commuting, Tips, Helmets",
                "excerpt": "Crucial defensive cycling habits, braking techniques, and visibility rules for traveling safely at 20-28 mph.",
                "content": """
### Mastering the Road: Defensive Riding in Heavy Traffic

Traveling at 20 to 28 mph places you at motor vehicle speeds while retaining the vulnerability of a cyclist. Follow these essential safety protocols:

#### 1. Assume Motorists Do Not See You
Drivers turning right or pulling out of driveways consistently misjudge an approaching e-bike's speed. Because your bike looks like a standard bicycle, drivers assume you are traveling at 10 mph rather than 25 mph.
* Always make eye contact before passing an intersection or driveway.
* Cover your brake levers with two fingers whenever approaching intersections.

#### 2. Master Progressive Two-Handed Braking
Never slam on the front brake lever in a panic. Apply 70% braking force smoothly with the front brake and 30% with the rear brake while shifting your body weight back over the rear wheel to prevent endo-flipping.

#### 3. Day and Night Daytime Running Lights
Ride with high-lumen flashing or solid LED front and rear lights even on bright, sunny afternoons. Studies show daytime running lights reduce car-bicycle collision rates by over 30%.

#### 4. Invest in an E-Bike Rated Helmet
Standard low-speed bicycle helmets are certified only for 12 mph impacts. Opt for **NTA-8776 certified** or high-grade in-mold EPS helmets designed specifically for e-bike speeds.
                """
            },
            {
                "title": "The Future of Electric Mobility",
                "slug": "the-future-of-electric-mobility",
                "category": bcat_map["buying-guides"],
                "tags": "Future, Technology, Green Energy, Innovation",
                "excerpt": "From solid-state batteries and IoT anti-theft connectivity to automatic electronic transmissions: what the next decade holds for e-bikes.",
                "content": """
### The Next Frontier: How Technological Innovation is Transforming Micro-Mobility

Electric micro-mobility is no longer a niche hobby—it is rapidly becoming the dominant urban transit solution globally. Here are the revolutionary technologies shaping the next generation of e-bikes.

#### 1. Solid-State Battery Revolution
Current lithium-ion cells with liquid electrolytes are nearing their energy density limits. Solid-state batteries currently in development promise:
* 50% higher energy density in identical pack sizes.
* 10-minute 80% ultra-fast charging.
* Complete elimination of thermal runaway and fire risk.

#### 2. Automatic Stepless Electronic Shifting
Integrated motor-gearbox units (such as Pinion and Valeo systems) eliminate external derailleurs, greasy chains, and fragile cassettes entirely. Microprocessors analyze rider cadence and grade every 10 milliseconds, changing internal sealed gears seamlessly under full motor torque.

#### 3. Smart Connected IoT & Anti-Theft Geofencing
Future e-bikes will integrate 5G eSIM connectivity, GPS tracking, and remote motor disabling. If an unauthorized movement is detected, the bike instantly immobilizes its rear wheel, sounds a siren, and alerts the owner's smartphone with real-time GPS tracking coordinates.

#### Conclusion
As cities convert vehicle lanes into dedicated protected bike highways, the lightweight electric bike stands as the most energy-efficient, clean, and joyous form of transport ever conceived.
                """
            },
        ]

        blog_objs = []
        for bdata in blog_posts_data:
            post, created = BlogPost.objects.get_or_create(
                slug=bdata["slug"],
                defaults={
                    "title": bdata["title"],
                    "category": bdata["category"],
                    "tags": bdata["tags"],
                    "excerpt": bdata["excerpt"],
                    "content": bdata["content"],
                    "author": admin_user,
                    "published": True,
                    "published_at": timezone.now() - timedelta(days=random.randint(1, 45)),
                    "views": random.randint(120, 1850)
                }
            )
            blog_objs.append(post)

            # Generate and assign blog graphic
            blog_img_path = os.path.join(settings.MEDIA_ROOT, 'blog', f"{post.slug}.jpg")
            if not os.path.exists(blog_img_path):
                create_blog_graphic(blog_img_path, post.title, post.category.name if post.category else "E-Mobility")
            post.featured_image = f"blog/{post.slug}.jpg"
            post.save()

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(blog_objs)} rich professional blog articles with imagery."))

        # 6. Sample Orders
        sample_order_configs = [
            ("Alex", "Rider", "alex.rider@example.com", "+1 555-0192", "742 Evergreen Terrace", "Springfield", "97477", "delivered", "paid", "cod", [("voltride-city-pro", 1), ("aero-smart-commuter-helmet", 1)]),
            ("Sarah", "Connor", "sarah.c@example.com", "+1 555-0842", "1200 Techwood Drive", "Atlanta", "30318", "shipped", "paid", "online_placeholder", [("voltride-mountain-x", 1), ("hardened-steel-folding-lock", 1)]),
            ("David", "Chen", "david.chen@example.com", "+1 555-0329", "88 Market St Suite 400", "San Francisco", "94105", "processing", "paid", "bank_transfer", [("48v-15ah-samsung-battery-pack", 1), ("48v-3a-smart-fast-charger", 1)]),
            ("Elena", "Rostova", "elena.r@example.com", "+1 555-0451", "350 5th Avenue", "New York", "10118", "confirmed", "paid", "online_placeholder", [("voltride-urban-lite", 1)]),
            ("Marcus", "Bell", "marcus.b@example.com", "+1 555-0773", "200 E Randolph St", "Chicago", "60601", "pending", "unpaid", "cod", [("750w-high-torque-hub-motor", 1), ("hydraulic-disc-brake-set", 1)]),
        ]

        order_count = 0
        for first, last, email, phone, addr, city, zip_code, status, p_status, p_method, items in sample_order_configs:
            # Create user or find
            u = User.objects.filter(email=email).first()
            
            subtotal = Decimal("0.00")
            order_items_to_create = []
            for slug, qty in items:
                p = Product.objects.filter(slug=slug).first()
                if p:
                    price = p.current_price
                    item_total = price * qty
                    subtotal += item_total
                    order_items_to_create.append((p, p.name, price, qty))

            shipping = Decimal("0.00") if subtotal >= Decimal("500.00") else Decimal("25.00")
            total = subtotal + shipping

            order_num = f"VR-{random.randint(100000, 999999)}"
            order, created = Order.objects.get_or_create(
                order_number=order_num,
                defaults={
                    "user": u,
                    "first_name": first,
                    "last_name": last,
                    "email": email,
                    "phone": phone,
                    "address": addr,
                    "city": city,
                    "postal_code": zip_code,
                    "country": "United States",
                    "subtotal": subtotal,
                    "shipping_cost": shipping,
                    "total": total,
                    "status": status,
                    "payment_method": p_method,
                    "payment_status": p_status,
                }
            )
            if created:
                for prod, pname, prc, qty in order_items_to_create:
                    OrderItem.objects.create(
                        order=order,
                        product=prod,
                        product_name=pname,
                        price=prc,
                        quantity=qty
                    )
                if p_status == "paid":
                    Payment.objects.create(
                        order=order,
                        transaction_id=f"TXN-{random.randint(10000000, 99999999)}",
                        payment_method=p_method,
                        amount=total,
                        status="completed",
                        notes="Simulated payment transaction"
                    )
                order_count += 1

        self.stdout.write(self.style.SUCCESS(f"Seeded {order_count} sample customer orders with line items and payments."))

        # 7. Sample Newsletter Subscribers & Contact Messages
        subscribers = [
            ("Jordan Smith", "jordan.smith@example.com"),
            ("Taylor Morgan", "taylor.m@example.com"),
            ("Casey Green", "casey.g@example.com"),
            ("Morgan Lee", "morgan.lee@example.com"),
            ("Riley Davis", "riley.davis@example.com"),
        ]
        for name, email in subscribers:
            NewsletterSubscriber.objects.get_or_create(email=email, defaults={"name": name})

        contact_samples = [
            ("Mark Stevens", "mark.s@example.com", "+1 555-4421", "Wholesale inquiries for bike rental shop", "Hello VoltRide team, I operate a coastal bike rental shop and would like to inquire about purchasing 12 VoltRide Explorer models for our upcoming summer season. Do you offer fleet commercial pricing?"),
            ("Linda Garcia", "linda.g@example.com", "+1 555-9011", "Battery replacement compatibility question", "Hi, I have an older 48V e-bike and would like to confirm if your 48V 15Ah Samsung battery pack cradle has identical pin placement. Could you please share the cradle dimensions drawing?"),
            ("Kevin Brooks", "kevin.b@example.com", "+1 555-3211", "Great customer support experience!", "Just wanted to send a quick note thanking Jason from technical support who walked me through installing the C900 display. Excellent service and support!"),
        ]
        for name, email, phone, subj, msg in contact_samples:
            ContactMessage.objects.get_or_create(
                email=email,
                subject=subj,
                defaults={"name": name, "phone": phone, "message": msg}
            )

        self.stdout.write(self.style.SUCCESS("All VoltRide seed data created successfully!"))
