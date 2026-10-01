import os
from PIL import Image, ImageDraw, ImageFont


def create_product_graphic(filename, title, category_name, subtitle="", color_theme="cyan"):
    """
    Generates a crisp modern 800x600 PNG banner/graphic for products
    with dark charcoal aesthetic, tech glow, and VoltRide branding.
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    width, height = 800, 600

    # Background gradient simulation
    img = Image.new("RGBA", (width, height), (15, 23, 42, 255))
    draw = ImageDraw.Draw(img)

    # Accent color based on theme
    if color_theme == "cyan":
        accent = (6, 182, 212, 255) # #06b6d4
        accent_light = (56, 189, 248, 255)
    elif color_theme == "green":
        accent = (16, 185, 129, 255) # #10b981
        accent_light = (52, 211, 153, 255)
    else:
        accent = (14, 165, 233, 255)
        accent_light = (125, 211, 252, 255)

    # Draw grid/tech lines
    for x in range(40, width, 60):
        draw.line([(x, 0), (x, height)], fill=(30, 41, 59, 120), width=1)
    for y in range(40, height, 60):
        draw.line([(0, y), (width, y)], fill=(30, 41, 59, 120), width=1)

    # Tech circles / rings in center
    cx, cy = width // 2, height // 2 - 20
    for r in [180, 140, 100, 60]:
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(30, 41, 59, 255), width=2)
    draw.ellipse([cx - 120, cy - 120, cx + 120, cy + 120], outline=accent, width=3)

    # Modern badge header
    badge_text = f"VOLTRIDE // {category_name.upper()}"
    draw.rounded_rectangle([cx - 160, 45, cx + 160, 80], radius=8, fill=(30, 41, 59, 255), outline=accent, width=1)
    draw.text((cx, 62), badge_text, fill=accent_light, anchor="mm")

    # Center icon / graphic representation
    draw.rectangle([cx - 70, cy - 35, cx + 70, cy + 35], fill=(30, 41, 59, 230), outline=accent, width=2)
    draw.text((cx, cy), "⚡ VOLTRIDE", fill=(255, 255, 255, 255), anchor="mm")

    # Main Product Title
    # Draw dark backing card for text
    draw.rounded_rectangle([50, 460, width - 50, 560], radius=12, fill=(15, 23, 42, 235), outline=(51, 65, 85, 255), width=2)
    draw.text((cx, 492), title, fill=(255, 255, 255, 255), anchor="mm")
    
    sub = subtitle if subtitle else "High Performance • Engineered for Durability • Genuine Quality"
    draw.text((cx, 528), sub, fill=(148, 163, 184, 255), anchor="mm")

    # Save image
    img = img.convert("RGB")
    img.save(filename, "JPEG", quality=90)
    return filename


def create_blog_graphic(filename, title, category_name):
    """
    Generates a crisp 1000x560 JPEG graphic for blog articles.
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    width, height = 1000, 560
    img = Image.new("RGBA", (width, height), (17, 24, 39, 255))
    draw = ImageDraw.Draw(img)

    accent = (16, 185, 129, 255) # VoltRide green

    # Subtle tech diagonals
    for i in range(-500, width + 500, 80):
        draw.line([(i, 0), (i + 300, height)], fill=(31, 41, 55, 150), width=1)

    # Header category pill
    draw.rounded_rectangle([60, 50, 320, 85], radius=6, fill=accent)
    draw.text((190, 67), f"VOLTRIDE INSIGHTS // {category_name.upper()}", fill=(15, 23, 42, 255), anchor="mm")

    # Central graphic box
    draw.rounded_rectangle([60, 110, width - 60, height - 60], radius=16, fill=(31, 41, 55, 220), outline=(55, 65, 81, 255), width=2)

    # Article title
    # Split title if long
    words = title.split()
    line1 = " ".join(words[:len(words)//2 + 1])
    line2 = " ".join(words[len(words)//2 + 1:])

    draw.text((width // 2, 230), line1, fill=(255, 255, 255, 255), anchor="mm")
    if line2:
        draw.text((width // 2, 275), line2, fill=(255, 255, 255, 255), anchor="mm")

    draw.line([(width // 2 - 80, 320), (width // 2 + 80, 320)], fill=accent, width=3)
    draw.text((width // 2, 360), "Official VoltRide Technical & Riding Guide", fill=(156, 163, 175, 255), anchor="mm")
    draw.text((width // 2, 410), "VOLTRIDE E-MOBILITY KNOWLEDGE BASE", fill=accent, anchor="mm")

    img = img.convert("RGB")
    img.save(filename, "JPEG", quality=90)
    return filename
