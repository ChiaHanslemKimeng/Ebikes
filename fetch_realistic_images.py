import os
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEDIA_DIR = os.path.join(BASE_DIR, 'media')
STATIC_DIR = os.path.join(BASE_DIR, 'static', 'images')

os.makedirs(os.path.join(MEDIA_DIR, 'products'), exist_ok=True)
os.makedirs(os.path.join(MEDIA_DIR, 'blog'), exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

# Image mapping dictionary
images = {
    # Hero slides
    os.path.join(STATIC_DIR, 'hero-slide-1.jpg'): 'https://images.unsplash.com/photo-1509099836639-18ba1795216d?auto=format&fit=crop&w=1600&q=85',
    os.path.join(STATIC_DIR, 'hero-slide-2.jpg'): 'https://images.unsplash.com/photo-1544197150-b99a580bb7a8?auto=format&fit=crop&w=1600&q=85',
    os.path.join(STATIC_DIR, 'hero-slide-3.jpg'): 'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=1600&q=85',

    # Products
    os.path.join(MEDIA_DIR, 'products', 'voltride-city-pro.jpg'): 'https://images.unsplash.com/photo-1571068316344-75bc76f77890?auto=format&fit=crop&w=900&q=80',
    os.path.join(MEDIA_DIR, 'products', 'voltride-mountain-x.jpg'): 'https://images.unsplash.com/photo-1532298229144-0ec0c57515c7?auto=format&fit=crop&w=900&q=80',
    os.path.join(MEDIA_DIR, 'products', 'voltride-urban-lite.jpg'): 'https://images.unsplash.com/photo-1485965120184-e220f721d03e?auto=format&fit=crop&w=900&q=80',
    os.path.join(MEDIA_DIR, 'products', 'voltride-fold-compact.jpg'): 'https://images.unsplash.com/photo-1507035895480-2b3156c31fc8?auto=format&fit=crop&w=900&q=80',
    os.path.join(MEDIA_DIR, 'products', 'voltride-cargo-max.jpg'): 'https://images.unsplash.com/photo-1502744688674-c619d1586c9e?auto=format&fit=crop&w=900&q=80',
    os.path.join(MEDIA_DIR, 'products', 'voltride-explorer-fat-tire.jpg'): 'https://images.unsplash.com/photo-1511994298241-608e28f14fde?auto=format&fit=crop&w=900&q=80',
    
    # Spare parts & electronics
    os.path.join(MEDIA_DIR, 'products', '750w-high-torque-hub-motor.jpg'): 'https://images.unsplash.com/photo-1558981806-ec527fa84c39?auto=format&fit=crop&w=900&q=80',
    os.path.join(MEDIA_DIR, 'products', '500w-brushless-hub-motor.jpg'): 'https://images.unsplash.com/photo-1558981854-350711fa357c?auto=format&fit=crop&w=900&q=80',
    os.path.join(MEDIA_DIR, 'products', '48v-15ah-samsung-battery-pack.jpg'): 'https://images.unsplash.com/photo-1617788138017-80ad40651399?auto=format&fit=crop&w=900&q=80',
    os.path.join(MEDIA_DIR, 'products', '48v-20ah-extended-range-battery.jpg'): 'https://images.unsplash.com/photo-1580910051074-3eb694886505?auto=format&fit=crop&w=900&q=80',
    os.path.join(MEDIA_DIR, 'products', '48v-3a-smart-fast-charger.jpg'): 'https://images.unsplash.com/photo-1583863788434-e58a36330cf0?auto=format&fit=crop&w=900&q=80',
    os.path.join(MEDIA_DIR, 'products', 'c900-smart-color-lcd-display.jpg'): 'https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&w=900&q=80',
    os.path.join(MEDIA_DIR, 'products', '48v-25a-sine-wave-controller.jpg'): 'https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=900&q=80',
    os.path.join(MEDIA_DIR, 'products', 'hydraulic-disc-brake-set.jpg'): 'https://images.unsplash.com/photo-1505705694340-019e1e335916?auto=format&fit=crop&w=900&q=80',
    os.path.join(MEDIA_DIR, 'products', 'puncture-resistant-fat-tire-26x4.jpg'): 'https://images.unsplash.com/photo-1576435728678-68d0fbf94e91?auto=format&fit=crop&w=900&q=80',
    os.path.join(MEDIA_DIR, 'products', 'city-commuter-tire-27-5.jpg'): 'https://images.unsplash.com/photo-1576435728678-68d0fbf94e91?auto=format&fit=crop&w=900&q=80',
    os.path.join(MEDIA_DIR, 'products', 'heavy-duty-alloy-rear-rim-27-5.jpg'): 'https://images.unsplash.com/photo-1528629297340-d1d461b55f91?auto=format&fit=crop&w=900&q=80',
    os.path.join(MEDIA_DIR, 'products', 'waterproof-thumb-throttle.jpg'): 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=900&q=80',
    os.path.join(MEDIA_DIR, 'products', '1200-lumen-led-headlight-horn.jpg'): 'https://images.unsplash.com/photo-1517649763962-0c623266ddc0?auto=format&fit=crop&w=900&q=80',
    
    # Accessories
    os.path.join(MEDIA_DIR, 'products', 'aero-smart-commuter-helmet.jpg'): 'https://images.unsplash.com/photo-1557804506-669a67965ba0?auto=format&fit=crop&w=900&q=80',
    os.path.join(MEDIA_DIR, 'products', 'hardened-steel-folding-lock.jpg'): 'https://images.unsplash.com/photo-1584438784894-089d6a62b8fa?auto=format&fit=crop&w=900&q=80',
    os.path.join(MEDIA_DIR, 'products', 'waterproof-roll-top-pannier-bag-25l.jpg'): 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=900&q=80',
    os.path.join(MEDIA_DIR, 'products', 'aluminum-phone-mount-usb-charging.jpg'): 'https://images.unsplash.com/photo-1580910051074-3eb694886505?auto=format&fit=crop&w=900&q=80',
    os.path.join(MEDIA_DIR, 'products', 'portable-electric-tire-pump.jpg'): 'https://images.unsplash.com/photo-1581783342308-f792dbdd27c5?auto=format&fit=crop&w=900&q=80',
    os.path.join(MEDIA_DIR, 'products', 'wide-angle-handlebar-mirror-set.jpg'): 'https://images.unsplash.com/photo-1506157786151-b8491531f063?auto=format&fit=crop&w=900&q=80',

    # Blog Post Images
    os.path.join(MEDIA_DIR, 'blog', 'how-to-choose-the-right-electric-bike.jpg'): 'https://images.unsplash.com/photo-1571068316344-75bc76f77890?auto=format&fit=crop&w=1000&q=80',
    os.path.join(MEDIA_DIR, 'blog', 'e-bike-battery-care-guide.jpg'): 'https://images.unsplash.com/photo-1617788138017-80ad40651399?auto=format&fit=crop&w=1000&q=80',
    os.path.join(MEDIA_DIR, 'blog', 'how-far-can-an-electric-bike-travel.jpg'): 'https://images.unsplash.com/photo-1509099836639-18ba1795216d?auto=format&fit=crop&w=1000&q=80',
    os.path.join(MEDIA_DIR, 'blog', 'e-bike-maintenance-checklist.jpg'): 'https://images.unsplash.com/photo-1581783342308-f792dbdd27c5?auto=format&fit=crop&w=1000&q=80',
    os.path.join(MEDIA_DIR, 'blog', 'understanding-motor-power.jpg'): 'https://images.unsplash.com/photo-1558981806-ec527fa84c39?auto=format&fit=crop&w=1000&q=80',
    os.path.join(MEDIA_DIR, 'blog', 'city-e-bikes-vs-mountain-e-bikes.jpg'): 'https://images.unsplash.com/photo-1532298229144-0ec0c57515c7?auto=format&fit=crop&w=1000&q=80',
    os.path.join(MEDIA_DIR, 'blog', 'how-to-extend-battery-life.jpg'): 'https://images.unsplash.com/photo-1580910051074-3eb694886505?auto=format&fit=crop&w=1000&q=80',
    os.path.join(MEDIA_DIR, 'blog', 'common-e-bike-problems-and-solutions.jpg'): 'https://images.unsplash.com/photo-1505705694340-019e1e335916?auto=format&fit=crop&w=1000&q=80',
    os.path.join(MEDIA_DIR, 'blog', 'how-to-choose-the-correct-charger.jpg'): 'https://images.unsplash.com/photo-1583863788434-e58a36330cf0?auto=format&fit=crop&w=1000&q=80',
    os.path.join(MEDIA_DIR, 'blog', 'essential-e-bike-spare-parts.jpg'): 'https://images.unsplash.com/photo-1528629297340-d1d461b55f91?auto=format&fit=crop&w=1000&q=80',
    os.path.join(MEDIA_DIR, 'blog', 'electric-bike-safety-tips.jpg'): 'https://images.unsplash.com/photo-1557804506-669a67965ba0?auto=format&fit=crop&w=1000&q=80',
    os.path.join(MEDIA_DIR, 'blog', 'the-future-of-electric-mobility.jpg'): 'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=1000&q=80',
}

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

for target_path, url in images.items():
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response, open(target_path, 'wb') as out_file:
            out_file.write(response.read())
        print(f"Downloaded: {os.path.basename(target_path)}")
    except Exception as e:
        print(f"Skipping {os.path.basename(target_path)}: {e}")
