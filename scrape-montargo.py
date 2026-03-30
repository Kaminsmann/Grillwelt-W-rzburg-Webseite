#!/usr/bin/env python3
# scrape-montargo.py – scrapes Montargo brand pages and generates hersteller pages
# Brands: The MeatStick, Everdure by Heston, Everdure, Yakiniku, Witt, Mr. Barrel BBQ

import sys, os, re, time, struct, zlib
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

BASE_DIR = Path(__file__).parent
IMG_BASE  = BASE_DIR / "img"
HERSTELLER_BASE = BASE_DIR / "hersteller"
MONTARGO_BASE = "https://www.montargo.de"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36",
    "Accept-Language": "de-DE,de;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

def fetch_html(url):
    try:
        req = Request(url, headers=HEADERS)
        with urlopen(req, timeout=20) as r:
            raw = r.read()
        for enc in ("utf-8", "latin-1"):
            try:
                return raw.decode(enc)
            except UnicodeDecodeError:
                continue
    except Exception as e:
        print(f"  FEHLER fetch {url}: {e}")
    return ""

def is_valid_image(data):
    if data[:8] == b'\x89PNG\r\n\x1a\n':
        return True
    if data[:3] == b'\xff\xd8\xff':
        return True
    if data[:4] == b'RIFF' and data[8:12] == b'WEBP':
        return True
    return False

def download_image(img_url, dest_path):
    if dest_path.exists():
        return True
    try:
        req = Request(img_url, headers=HEADERS)
        with urlopen(req, timeout=15) as r:
            data = r.read()
        if not is_valid_image(data):
            print(f"  UNGÜLTIG {img_url}")
            return False
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_bytes(data)
        print(f"  OK  {dest_path.name}")
        return True
    except Exception as e:
        print(f"  FEHLER {img_url}: {e}")
        return False

def slugify(name):
    s = name.lower()
    for a, b in [('ä','ae'),('ö','oe'),('ü','ue'),('ß','ss'),(' ','-'),("'",'-'),('/','-')]:
        s = s.replace(a, b)
    s = re.sub(r'[^a-z0-9-]', '', s)
    s = re.sub(r'-+', '-', s).strip('-')
    return s

def extract_products_from_html(html):
    """Extract product name, price, image from dcshop product listing HTML."""
    products = []
    # Find product blocks - dcshop uses article.dc-product-item or div.product-item
    # Try to find blocks with thumb_2 images + product names
    # Pattern: find each product card block
    blocks = re.findall(
        r'<(?:article|div)[^>]+class="[^"]*(?:product[_-]item|dc-product[_-]item)[^"]*"[^>]*>(.*?)</(?:article|div)>',
        html, re.DOTALL | re.IGNORECASE
    )
    if not blocks:
        # Fallback: look for thumb_2 images near product names
        blocks = re.findall(
            r'<(?:figure|div)[^>]*>[^<]*<img[^>]+/userdata/dcshop/images/thumb_2/[^>]+>.*?</(?:figure|div)>',
            html, re.DOTALL | re.IGNORECASE
        )
    for block in blocks:
        img_m = re.search(r'src="(/userdata/dcshop/images/thumb_2/[^"]+)"', block)
        name_m = re.search(r'<(?:h[1-4]|a)[^>]*class="[^"]*(?:product[_-]name|title)[^"]*"[^>]*>([^<]+)<', block)
        if not name_m:
            name_m = re.search(r'<a[^>]+href="[^"]*product[^"]*"[^>]*>([^<]+)</a>', block)
        price_m = re.search(r'(\d[\d.,]+)\s*€|€\s*(\d[\d.,]+)', block)
        if img_m:
            products.append({
                'img': img_m.group(1),
                'name': name_m.group(1).strip() if name_m else '',
                'price': (price_m.group(1) or price_m.group(2)) if price_m else '',
            })
    return products

def extract_thumb2_images(html):
    """Extract all unique thumb_2 image paths from page HTML."""
    return list(dict.fromkeys(re.findall(r'/userdata/dcshop/images/thumb_2/[^"\'>\s]+', html)))

# ─── NAV TEMPLATE ─────────────────────────────────────────────────────────────

NAV = """  <header class="site-header">
    <div class="container header-inner">
      <a href="/" class="logo"><img src="/img/ui/logo.svg" alt="Feuerhaus Kalina" width="180" height="48"></a>
      <nav class="main-nav" aria-label="Hauptnavigation">
        <ul>
          <li><a href="/outdoor-kuechen/">Outdoor-Küchen</a></li>
          <li><a href="/keramikgrills-kamado/">Keramikgrills</a></li>
          <li><a href="/plancha-feuerplatten/">Plancha</a></li>
          <li><a href="/schuerzen/">Schürzen</a></li>
          <li><a href="/hersteller/" class="active">Hersteller</a></li>
          <li><a href="/ratgeber/">Ratgeber</a></li>
          <li><a href="/kontakt/">Kontakt</a></li>
        </ul>
      </nav>
      <button class="nav-menu-toggle" aria-label="Menü öffnen" aria-expanded="false">
        <span></span><span></span><span></span>
      </button>
    </div>
  </header>"""

FOOTER = """  <footer class="site-footer">
    <div class="container footer-inner">
      <div class="footer-col">
        <strong>Feuerhaus Kalina</strong>
        <p>Würzburger Str. 2<br>97222 Rimpar</p>
        <p><a href="tel:+499365884030">09365 884030</a></p>
      </div>
      <div class="footer-col">
        <strong>Sortiment</strong>
        <ul>
          <li><a href="/outdoor-kuechen/">Outdoor-Küchen</a></li>
          <li><a href="/keramikgrills-kamado/">Keramikgrills</a></li>
          <li><a href="/plancha-feuerplatten/">Plancha</a></li>
          <li><a href="/zubehoer/">Zubehör</a></li>
          <li><a href="/hersteller/">Hersteller</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <strong>Service</strong>
        <ul>
          <li><a href="/ratgeber/">Ratgeber</a></li>
          <li><a href="/kontakt/">Kontakt</a></li>
          <li><a href="/impressum/">Impressum</a></li>
          <li><a href="/datenschutz/">Datenschutz</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-copy">
      <div class="container">© 2025 Feuerhaus Kalina – Grillwelt Würzburg</div>
    </div>
  </footer>
  <script src="/js/main.js"></script>"""

def html_page(title, meta_desc, canonical, breadcrumbs, h1, hero_text, content, ld_json):
    bc_json = ",\n      ".join(
        f'{{"@type":"ListItem","position":{i+1},"name":"{n}","item":"https://grills.feuerhaus-kalina.de{u}"}}'
        if u else f'{{"@type":"ListItem","position":{i+1},"name":"{n}"}}'
        for i, (n, u) in enumerate(breadcrumbs)
    )
    bc_nav = " ".join(
        f'<li><a href="{u}">{n}</a></li>' if u else f'<li>{n}</li>'
        for n, u in breadcrumbs
    )
    extra_ld = f'\n  <script type="application/ld+json">\n  {ld_json}\n  </script>' if ld_json else ''
    return f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <meta name="description" content="{meta_desc}">
  <link rel="canonical" href="{canonical}">
  <link rel="icon" href="/img/ui/favicon.ico">
  <link rel="apple-touch-icon" href="/img/ui/apple-touch-icon.png">
  <link rel="stylesheet" href="/css/style.css">
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      {bc_json}
    ]
  }}
  </script>{extra_ld}
</head>
<body>
{NAV}

  <main>
    <section class="page-hero">
      <div class="container">
        <nav class="breadcrumb" aria-label="Breadcrumb">
          <ol>{bc_nav}</ol>
        </nav>
        <h1>{h1}</h1>
        <p class="hero-lead">{hero_text}</p>
      </div>
    </section>

{content}
  </main>

{FOOTER}
</body>
</html>
"""

def product_card(name, price, img_path, desc=""):
    price_html = f'<p class="product-price">ab {price} €</p>' if price else ''
    desc_html  = f'<p class="product-desc">{desc}</p>' if desc else ''
    return f"""          <div class="product-card">
            <div class="product-img-wrap">
              <img data-src="{img_path}" src="/img/ui/placeholder.png" alt="{name}" class="lazy" loading="lazy">
            </div>
            <div class="product-info">
              <h3>{name}</h3>
              {desc_html}{price_html}
              <a href="/kontakt/" class="product-anfragen">Anfragen →</a>
            </div>
          </div>"""

def sidebar_box(brand_name, brand_url):
    return f"""      <aside class="sticky-sidebar">
        <div class="sidebar-box">
          <h3>Interesse an {brand_name}?</h3>
          <p>Besuchen Sie uns in Rimpar bei Würzburg – wir beraten Sie persönlich zu allen Modellen.</p>
          <a href="/kontakt/" class="btn-primary">Jetzt anfragen</a>
        </div>
        <div class="sidebar-box">
          <h3>Händler vor Ort</h3>
          <p>Feuerhaus Kalina<br>Würzburger Str. 2<br>97222 Rimpar</p>
          <p><a href="tel:+499365884030">09365 884030</a></p>
        </div>
      </aside>"""

def info_section(text):
    return f"""    <section class="info-block">
      <div class="container">
        <div class="info-cols">
          <div>{text}</div>
        </div>
      </div>
    </section>"""

# ─── BRAND DEFINITIONS ────────────────────────────────────────────────────────

BRANDS = [
    {
        'slug': 'the-meatstick',
        'dir': HERSTELLER_BASE / 'the-meatstick',
        'img_dir': IMG_BASE / 'the-meatstick',
        'source_url': 'https://www.montargo.de/de/tms/',
        'name': 'The MeatStick',
        'title': 'The MeatStick – Kabelloses Fleischthermometer | Feuerhaus Kalina Würzburg',
        'meta_desc': 'The MeatStick kabelloses Präzisions-Fleischthermometer kaufen in Würzburg. V, CHEF X und 4X Set bei Feuerhaus Kalina in Rimpar – autorisierter Händler.',
        'canonical': 'https://grills.feuerhaus-kalina.de/hersteller/the-meatstick/',
        'breadcrumbs': [('Start', '/'), ('Hersteller', '/hersteller/'), ('The MeatStick', None)],
        'h1': 'The MeatStick – Präzision ohne Kabel',
        'hero_text': 'The MeatStick ist das vielseitigste kabellose Fleischthermometer der Welt. Von Bluetooth bis WiFi, vom Grill bis zum Smoker – perfekte Kerntemperatur auf jedem Gerät, jederzeit.',
        'info': '<p>Mit dem <strong>The MeatStick V</strong> erreichen Sie Temperaturen bis 650 °C dank FireForge™-Technologie. WiFi mit unbegrenzter Reichweite und Bluetooth 5.4 bis 275 m im Freien. IPX9K-zertifiziert – spülmaschinenfest und wasserdicht.</p>',
        'products': [
            {'name': 'The MeatStick V SET', 'price': '109,20', 'img_path': '/userdata/dcshop/images/thumb_2/', 'desc': 'Neuestes Modell, FireForge™ bis 650 °C, WiFi & Bluetooth 5.4'},
            {'name': 'The MeatStick V Dual SET', 'price': '168,03', 'img_path': '/userdata/dcshop/images/thumb_2/', 'desc': 'Zwei V-Sensoren im Set'},
            {'name': 'The MeatStick CHEF X SET', 'price': '100,80', 'img_path': '/userdata/dcshop/images/thumb_2/', 'desc': 'Erweiterter CHEF-Sensor mit Ladegerät'},
            {'name': 'The MeatStick 4X SET', 'price': '100,80', 'img_path': '/userdata/dcshop/images/thumb_2/', 'desc': 'Vier-Sensor-Konfiguration'},
            {'name': 'The MeatStick X SET', 'price': '75,59', 'img_path': '/userdata/dcshop/images/thumb_2/', 'desc': 'X-Sensor mit Ladegerät'},
            {'name': 'The MeatStick CHEF SET', 'price': '83,99', 'img_path': '/userdata/dcshop/images/thumb_2/', 'desc': 'CHEF-Sensor mit Ladegerät'},
            {'name': 'The MeatStick 4 SET', 'price': '83,99', 'img_path': '/userdata/dcshop/images/thumb_2/', 'desc': 'Standard Vier-Sensor-Set'},
        ],
        'fetch_images': True,  # fetch from page HTML
    },
    {
        'slug': 'everdure-by-heston',
        'dir': HERSTELLER_BASE / 'everdure-by-heston',
        'img_dir': IMG_BASE / 'everdure-by-heston',
        'source_url': 'https://www.montargo.de/de/ehb/',
        'name': 'Everdure by Heston Blumenthal',
        'title': 'Everdure by Heston Blumenthal – Grills & Kamado | Feuerhaus Kalina Würzburg',
        'meta_desc': 'Everdure by Heston Blumenthal kaufen in Würzburg: HUB, 4K Kamado, FORCE & FURNACE Gasgrill. Autorisierter Händler bei Feuerhaus Kalina in Rimpar.',
        'canonical': 'https://grills.feuerhaus-kalina.de/hersteller/everdure-by-heston/',
        'breadcrumbs': [('Start', '/'), ('Hersteller', '/hersteller/'), ('Everdure by Heston', None)],
        'h1': 'Everdure by Heston Blumenthal – australisches Design trifft Drei-Sterne-Küche',
        'hero_text': 'Die Kollaboration zwischen dem australischen Grillhersteller Everdure und dem Drei-Sterne-Michelin-Koch Heston Blumenthal vereint Designanspruch mit präziser Grilltechnik. Fast Flame-Technologie, elektrische Zündung und ikonisches Design.',
        'info': '<p>Die <strong>ehb-Linie</strong> steht für Grills, die nicht nur auf dem Teller überzeugen, sondern auch als Designobjekte im Garten wirken. Der <strong>HUB</strong> vereint Holzkohleglut mit elektrischer Zündung in unter zwei Minuten – der <strong>4K</strong> ist der Kamado-Ofen für den Vollprofi.</p>',
        'products': [
            {'name': 'Everdure HUB II Holzkohlegrill', 'price': '1.679,83', 'img_path': '/userdata/dcshop/images/thumb_2/', 'desc': 'Holzkohlegrill mit elektrischer Zündung, Fast Flame'},
            {'name': 'Everdure 4K Outdoor Ofen graphite', 'price': '1.201,00', 'img_path': '/userdata/dcshop/images/thumb_2/', 'desc': 'Outdoor-Ofen mit elektrischer Zündung, Gusseisen-Grillrost'},
            {'name': 'Everdure HUB Holzkohlegrill', 'price': '764,12', 'img_path': '/userdata/dcshop/images/thumb_2/', 'desc': 'Holzkohlegrill mit elektrischer Zündung'},
            {'name': 'Everdure FURNACE Gasgrill', 'price': '839,50', 'img_path': '/userdata/dcshop/images/thumb_2/', 'desc': 'Gasgrill graphit mit Doppelgestell'},
            {'name': 'FUSION mit elektr. Anzünder', 'price': '671,43', 'img_path': '/userdata/dcshop/images/thumb_2/', 'desc': 'Holzkohlegrill mit elektrischer Zündung und Gestell'},
            {'name': 'Everdure FORCE Gasgrill', 'price': '671,43', 'img_path': '/userdata/dcshop/images/thumb_2/', 'desc': 'Gasgrill graphit mit Doppelgestell'},
            {'name': 'Everdure K1 Kamado Ofen', 'price': '983,00', 'img_path': '/userdata/dcshop/images/thumb_2/', 'desc': 'Kamado-Ofen schwarz, keramisch'},
            {'name': 'CUBE 360 Tragbarer Holzkohlegrill', 'price': '176,43', 'img_path': '/userdata/dcshop/images/thumb_2/', 'desc': 'Tragbarer Holzkohlegrill mit Haube und Thermometer'},
            {'name': 'CUBE Tragbarer Holzkohlegrill', 'price': '126,01', 'img_path': '/userdata/dcshop/images/thumb_2/', 'desc': 'Tragbarer Holzkohlegrill, graphit'},
            {'name': 'Everdure CUBE ProFlame 360 Gasgrill', 'price': '152,91', 'img_path': '/userdata/dcshop/images/thumb_2/', 'desc': 'Tragbarer Gasgrill mit Haube, schwarz'},
        ],
        'fetch_images': True,
    },
    {
        'slug': 'everdure',
        'dir': HERSTELLER_BASE / 'everdure',
        'img_dir': IMG_BASE / 'everdure',
        'source_url': 'https://www.montargo.de/de/everdure/',
        'name': 'Everdure',
        'title': 'Everdure Outdoor-Küchen & Premium Grills | Feuerhaus Kalina Würzburg',
        'meta_desc': 'Everdure Outdoor-Küchen (NEO, SeaBreeze), Pizzaöfen (KILN) und Blaze Grills kaufen in Würzburg. Feuerhaus Kalina – autorisierter Everdure Händler.',
        'canonical': 'https://grills.feuerhaus-kalina.de/hersteller/everdure/',
        'breadcrumbs': [('Start', '/'), ('Hersteller', '/hersteller/'), ('Everdure', None)],
        'h1': 'Everdure – Modulare Outdoor-Küchen & Premium-Grills',
        'hero_text': 'Everdure steht für ganzheitliche Outdoor-Küchen-Systeme aus Australien. Von der modularen NEO Outdoor-Küche über das SeaBreeze-System bis zu Pizzaöfen der KILN-Linie – kompromisslose Qualität aus Edelstahl und Keramik.',
        'info': '<p>Die <strong>Everdure NEO Outdoor-Küche</strong> kombiniert Gasgrillmodul, Spüle, Kühlschrank und Arbeitsplatten zu einem vollständigen Outdoor-Kochplatz. Das <strong>SeaBreeze</strong>-Modulsystem bietet maximale Flexibilität für individuelle Konfigurationen.</p>',
        'products': [
            {'name': 'Everdure NEO Outdoorküche Black Steel', 'price': '3.899,00', 'img_path': '/userdata/dcshop/images/thumb_2/627567_275082_everdure_bbq_silver_front_grade.png', 'desc': 'Premium Outdoor-Küche, Edelstahl & Marmor-Arbeitsplatte'},
            {'name': 'Everdure NEO Outdoor Küche Stone', 'price': '2.899,00', 'img_path': '/userdata/dcshop/images/thumb_2/28877_neo.jpg', 'desc': 'Outdoor-Küche mit Sprühstein-Verkleidung, Keramikoberfläche'},
            {'name': 'Gasgrillmodul EBLPCBI-22', 'price': '2.419,56', 'img_path': '/userdata/dcshop/images/thumb_2/125794_303232_everdure_grill_main_frei_001.png', 'desc': '6 Edelstahlbrenner, 25 kW, XXL-Grillfläche'},
            {'name': 'Einbaumodul Getränkekühlschrank', 'price': '846,45', 'img_path': '/userdata/dcshop/images/thumb_2/934735_361048_everdure_bbq_kuehlschrank.png', 'desc': '208 L, LED, Temperatur 0–10 °C'},
            {'name': 'Spülenmodul mit Spüle und Wasserhahn', 'price': '1.027,97', 'img_path': '/userdata/dcshop/images/thumb_2/523982_368045_neo_black_spuele_retuschiert.png', 'desc': 'Spülenmodul für NEO Black Steel Serie'},
            {'name': 'Everdure SeaBreeze Einbau-Gasgrill', 'price': '780,67', 'img_path': '/userdata/dcshop/images/thumb_2/381489_furnace-built-in-2.jpg', 'desc': 'Einbau-Gasgrill für modulare Outdoor-Küche'},
            {'name': 'Everdure SeaBreeze 4K/K1 BBQ Modul', 'price': '1.091,60', 'img_path': '/userdata/dcshop/images/thumb_2/499312_everdure-seabreeze-outdoor-kueche-kamado-modul.jpg', 'desc': 'Kamado BBQ-Modul für SeaBreeze Outdoor-Küche'},
            {'name': 'SeaBreeze Schrankmodul Doppelschublade', 'price': '797,48', 'img_path': '/userdata/dcshop/images/thumb_2/832425_ekmstdwrbp_p_001.png', 'desc': 'Schrank mit Doppelschublade, schwarz'},
            {'name': 'SeaBreeze Schrankmodul Doppeltüren', 'price': '755,46', 'img_path': '/userdata/dcshop/images/thumb_2/411004_ekmstrgbp_p_001.png', 'desc': 'Schrank mit Doppeltüren, schwarz'},
            {'name': 'Everdure Blaze 20" Kamado Aluminiumguss', 'price': '1.411,18', 'img_path': '/userdata/dcshop/images/thumb_2/714968_blaze_kamado-01.jpg', 'desc': 'Aluminiumguss-Kamado 20 Zoll'},
            {'name': 'Everdure Blaze LTE+ 30" Gas Griddle', 'price': '1.931,93', 'img_path': '/userdata/dcshop/images/thumb_2/159530_ebs4g2-lteplus_01.jpg', 'desc': 'Gas-Grillplatte 30 Zoll für Outdoor'},
            {'name': 'Everdure KILN P Pizzaofen', 'price': '419,33', 'img_path': '/userdata/dcshop/images/thumb_2/471042_kiln-p-black.jpg', 'desc': 'Pizzaofen mit Digitaldisplay und Infrarotbrenner'},
        ],
        'fetch_images': False,
    },
    {
        'slug': 'yakiniku',
        'dir': HERSTELLER_BASE / 'yakiniku',
        'img_dir': IMG_BASE / 'yakiniku',
        'source_url': 'https://www.montargo.de/de/yakiniku/',
        'name': 'Yakiniku',
        'title': 'Yakiniku Kamado & Shichirin Keramikgrills | Feuerhaus Kalina Würzburg',
        'meta_desc': 'Yakiniku Keramik-Kamado und Shichirin-Tischgrills kaufen in Würzburg. XLARGE, LARGE, MEDIUM, MINI und Shichirin-Konro bei Feuerhaus Kalina in Rimpar.',
        'canonical': 'https://grills.feuerhaus-kalina.de/hersteller/yakiniku/',
        'breadcrumbs': [('Start', '/'), ('Hersteller', '/hersteller/'), ('Yakiniku', None)],
        'h1': 'Yakiniku – Japanische Grillkultur in Keramik',
        'hero_text': 'Yakiniku verbindet die Jahrtausende alte japanische Grilltradition mit europäischem Designanspruch. Keramische Kamado-Grills und authentische Shichirin-Tischgrills – für Temperaturen bis 1.000 °C mit Binchotan-Kohle.',
        'info': '<p>Die <strong>Yakiniku Kamado-Grills</strong> (MINI 11", MEDIUM 16", LARGE 19", XLARGE 22") sind aus hochwertigem Keramik gefertigt und halten Temperaturen von 80 °C bis über 350 °C. Die <strong>Shichirin-Konro</strong>-Grills sind ideal für Yakitori und japanisches Tischgrillen.</p>',
        'products': [
            {'name': 'Yakiniku XLARGE Set 22"', 'price': '1.931,93', 'img_path': '/userdata/dcshop/images/thumb_2/28864_22_xlarge_met_onderstelDEU.jpg', 'desc': 'Großer Kamado mit Gestell, 22 Zoll'},
            {'name': 'Yakiniku XLARGE 22" Keramischer Grill', 'price': '1.595,80', 'img_path': '/userdata/dcshop/images/thumb_2/650806_yakiniku-xlarge-kamado-solo-compleet.jpg', 'desc': 'XLARGE Kamado komplett, 22 Zoll'},
            {'name': 'Yakiniku XLARGE Set 22" (Classic)', 'price': '1.721,85', 'img_path': '/userdata/dcshop/images/thumb_2/28864_22_xlarge_met_onderstel.jpg', 'desc': 'XLARGE mit Gestell, Classic Edition'},
            {'name': 'Yakiniku LARGE Set 19"', 'price': '1.091,60', 'img_path': '/userdata/dcshop/images/thumb_2/28880_19_large_met_onderstel.jpg', 'desc': 'LARGE Kamado mit Gestell, 19 Zoll'},
            {'name': 'Yakiniku LARGE 19" Keramischer Grill', 'price': '1.049,58', 'img_path': '/userdata/dcshop/images/thumb_2/28882_19_largeDEU.jpg', 'desc': 'LARGE Kamado, 19 Zoll'},
            {'name': 'Yakiniku Large 19" Basic Black Edition', 'price': '755,46', 'img_path': '/userdata/dcshop/images/thumb_2/614586_yakiniku-large-kamado-basic-black-edition_9.jpg', 'desc': 'LARGE Basic Black, 19 Zoll'},
            {'name': 'Yakiniku MEDIUM 16" Keramischer Grill', 'price': '839,50', 'img_path': '/userdata/dcshop/images/thumb_2/28885_16_medium.jpg', 'desc': 'MEDIUM Kamado, 16 Zoll'},
            {'name': 'Shichirin Pro Keramik Grill Medium Eckig', 'price': '335,29', 'img_path': '/userdata/dcshop/images/thumb_2/827117_yakiniku-medium-rechthoekige-shichirin-pro-konro-yakitori-grill.jpg', 'desc': 'Shichirin Pro für Yakitori & Tischgrillen'},
            {'name': 'Shichirin Keramik Grill Rund 300mm', 'price': '117,06', 'img_path': '/userdata/dcshop/images/thumb_2/28890_shichirin_rond.jpg', 'desc': 'Shichirin rund, Ø 300 mm'},
            {'name': 'Shichirin Keramik Grill Eckig 400×200mm', 'price': '117,06', 'img_path': '/userdata/dcshop/images/thumb_2/28891_shichirin_langwerpig.jpg', 'desc': 'Shichirin rechteckig, 400 × 200 mm'},
            {'name': 'Shichirin Keramik Grill Mini Rund 270mm', 'price': '93,53', 'img_path': '/userdata/dcshop/images/thumb_2/571833_800720_-_8720364496029_-_yakiniku_shichirin_mini_round_01.jpg', 'desc': 'Shichirin Mini rund, Ø 270 mm'},
        ],
        'fetch_images': False,
    },
    {
        'slug': 'witt',
        'dir': HERSTELLER_BASE / 'witt',
        'img_dir': IMG_BASE / 'witt',
        'source_url': 'https://www.montargo.de/de/witt/',
        'name': 'Witt',
        'title': 'Witt Pizzaofen – Etna Rotante & PICCOLO | Feuerhaus Kalina Würzburg',
        'meta_desc': 'Witt Pizzaöfen kaufen in Würzburg: Etna Rotante, Etna Fermo und PICCOLO mit rotierendem Pizzastein. Feuerhaus Kalina – autorisierter Witt Händler in Rimpar.',
        'canonical': 'https://grills.feuerhaus-kalina.de/hersteller/witt/',
        'breadcrumbs': [('Start', '/'), ('Hersteller', '/hersteller/'), ('Witt', None)],
        'h1': 'Witt Pizzaöfen – Neapolitanische Pizza im eigenen Garten',
        'hero_text': 'Witt aus Dänemark hat den Outdoor-Pizzaofen revolutioniert. Mit rotierendem Pizzastein sorgt die Etna Rotante-Linie für gleichmäßige Hitze und perfekte neapolitanische Pizza in unter 60 Sekunden – direkt im Garten.',
        'info': '<p>Die <strong>Witt Etna Rotante</strong> erreicht über 500 °C Innentemperatur. Der rotierende Pizzastein dreht sich automatisch und sorgt für gleichmäßige Hitzeverteilung ohne manuelles Drehen. Erhältlich in Graphit, Black, Stone und Orange.</p>',
        'products': [
            {'name': 'Witt Etna Rotante 16" Control', 'price': '797,48', 'img_path': '/userdata/dcshop/images/thumb_2/198969_100000376-03_03_witt_pizza_black-02.0_005.png', 'desc': 'Rotierender Pizzastein, Temperaturkontrolle, 16 Zoll'},
            {'name': 'Witt Etna Rotante 2 Brenner Black', 'price': '671,43', 'img_path': '/userdata/dcshop/images/thumb_2/34547_witt_pizza_rotante_8379_black.jpg', 'desc': 'Rotierender Pizzaofen, 2 Brenner, schwarz'},
            {'name': 'Witt Etna Rotante 2 Brenner Graphite', 'price': '671,43', 'img_path': '/userdata/dcshop/images/thumb_2/34548_witt_pizza_rotante_8379_graphite.jpg', 'desc': 'Rotierender Pizzaofen, 2 Brenner, graphit'},
            {'name': 'Witt Etna Rotante 2 Brenner Orange', 'price': '671,43', 'img_path': '/userdata/dcshop/images/thumb_2/743244_witt_pizza_rotante_8379_orange.png', 'desc': 'Rotierender Pizzaofen, 2 Brenner, orange'},
            {'name': 'Witt Etna Rotante Control 13"', 'price': '629,41', 'img_path': '/userdata/dcshop/images/thumb_2/891021_witt-rotante13-control-matte_black-front-low-left-trsp.png', 'desc': 'Rotierend, Digitalkontrolle, 13 Zoll'},
            {'name': 'Witt eGNITE Control 13"', 'price': '629,41', 'img_path': '/userdata/dcshop/images/thumb_2/672183_witt-egnite-matt-black-003.png', 'desc': 'Elektrische Zündung, Digitalkontrolle, 13 Zoll'},
            {'name': 'Witt PICCOLO Rotante 16"', 'price': '545,38', 'img_path': '/userdata/dcshop/images/thumb_2/232750_witt-piccolo_16in-black-01_front-04_tr.jpg', 'desc': 'Kompakter rotierender Pizzaofen, 16 Zoll'},
            {'name': 'Witt PICCOLO Rotante 13"', 'price': '461,34', 'img_path': '/userdata/dcshop/images/thumb_2/819927_witt-piccolo-front-matte_black.jpg', 'desc': 'Kompakter rotierender Pizzaofen, 13 Zoll'},
            {'name': 'Witt Etna Fermo 1 Brenner Black', 'price': '352,35', 'img_path': '/userdata/dcshop/images/thumb_2/34551_witt_etna_fermo_mat-black_01.jpg', 'desc': 'Feststehender Pizzaofen, 1 Brenner, schwarz'},
            {'name': 'Witt Etna Fermo 1 Brenner Graphite', 'price': '352,35', 'img_path': '/userdata/dcshop/images/thumb_2/34552_witt_etna_fermo_mat-graphite_01.jpg', 'desc': 'Feststehender Pizzaofen, 1 Brenner, graphit'},
            {'name': 'Witt PICCOLO Fermo 14"', 'price': '217,06', 'img_path': '/userdata/dcshop/images/thumb_2/463551_witt_pizzaovn_fermo_8379_black.jpg', 'desc': 'Kompakter Festofen, 14 Zoll, mattschwarz'},
        ],
        'fetch_images': False,
    },
    {
        'slug': 'mrbarrel',
        'dir': HERSTELLER_BASE / 'mrbarrel',
        'img_dir': IMG_BASE / 'mrbarrel',
        'source_url': 'https://www.montargo.de/de/mrbarrel/',
        'name': 'Mr. Barrel BBQ',
        'title': 'Mr. Barrel BBQ – Räucherholz aus Weinfässern | Feuerhaus Kalina Würzburg',
        'meta_desc': 'Mr. Barrel BBQ Räucherchunks, Pellets und Planks aus recycelten Eichenfässern kaufen in Würzburg. Whisky, Cognac, Rotwein – natürliches Raucharoma bei Feuerhaus Kalina.',
        'canonical': 'https://grills.feuerhaus-kalina.de/hersteller/mrbarrel/',
        'breadcrumbs': [('Start', '/'), ('Hersteller', '/hersteller/'), ('Mr. Barrel BBQ', None)],
        'h1': 'Mr. Barrel BBQ – Räucheraromen aus dem Weinfass',
        'hero_text': 'Mr. Barrel BBQ aus Spanien fertigt Räucherholz aus recycelten Eichenfässern – für Whisky, Cognac, Rotwein und Weißwein. 100 % natürliche Rohstoffe, ohne künstliche Aromazusätze. Authentischer BBQ-Geschmack direkt aus dem Fass.',
        'info': '<p><strong>Mr. Barrel BBQ</strong> verwendet ausschließlich gebrauchte Eichenfässer aus der Spirits- und Weinproduktion. Die Chunks, Pellets, Planks und Räuchermehl geben dem Grillgut ein unverwechselbares Aroma – von rauchig-süß bis würzig-torfig.</p>',
        'products': [
            {'name': 'Räucherchunks Whisky 3 kg', 'price': '15,35', 'img_path': '/userdata/dcshop/images/thumb_2/30706_chunks_whiskey.jpg', 'desc': '3 kg Räucherchunks aus Whisky-Eichenfässern'},
            {'name': 'Räucherchunks Rotwein 3 kg', 'price': '15,35', 'img_path': '/userdata/dcshop/images/thumb_2/30702_chunks_redwine.jpg', 'desc': '3 kg Räucherchunks aus Rotwein-Eichenfässern'},
            {'name': 'Räucherchunks Weißwein süß 3 kg', 'price': '15,35', 'img_path': '/userdata/dcshop/images/thumb_2/30708_chunks_whitewine.jpg', 'desc': '3 kg Räucherchunks aus Süßwein-Fässern'},
            {'name': 'Räucherchunks Cognac 1350 g', 'price': '7,66', 'img_path': '/userdata/dcshop/images/thumb_2/31420_delantera.png', 'desc': '1350 g Räucherchunks aus Cognac-Fässern'},
            {'name': 'Räucherchunks Whisky 1350 g', 'price': '7,66', 'img_path': '/userdata/dcshop/images/thumb_2/30697_delantera.png', 'desc': '1350 g Räucherchunks aus Whisky-Fässern'},
            {'name': 'Foodie Power Blocks Rotwein 5 kg', 'price': '26,78', 'img_path': '/userdata/dcshop/images/thumb_2/30822_rw_front.png', 'desc': '5 kg Räucherblöcke, Rotwein-Aroma'},
            {'name': 'Foodie Power Blocks Whisky 5 kg', 'price': '26,78', 'img_path': '/userdata/dcshop/images/thumb_2/30824_wh_front.png', 'desc': '5 kg Räucherblöcke, Whisky-Aroma'},
            {'name': 'Foodie Power Blocks Cognac 5 kg', 'price': '26,78', 'img_path': '/userdata/dcshop/images/thumb_2/33421_cog_front.png', 'desc': '5 kg Räucherblöcke, Cognac-Aroma'},
            {'name': 'Räucherpellets Mandel 2 kg (3er-Pack)', 'price': '6,75', 'img_path': '/userdata/dcshop/images/thumb_2/31313_delante.png', 'desc': '3 × 2 kg Räucherpellets Mandel'},
            {'name': 'Räucherpellets Cognac 2 kg (3er-Pack)', 'price': '6,75', 'img_path': '/userdata/dcshop/images/thumb_2/31315_delante.png', 'desc': '3 × 2 kg Räucherpellets Cognac'},
            {'name': 'Räucherpellets Citrus 2 kg (3er-Pack)', 'price': '6,75', 'img_path': '/userdata/dcshop/images/thumb_2/31314_delante.png', 'desc': '3 × 2 kg Räucherpellets Citrus'},
            {'name': 'Planks Sherry Wine', 'price': '6,28', 'img_path': '/userdata/dcshop/images/thumb_2/31378_planks_sherry.jpg', 'desc': '3 Räucherbretter aus Sherry-Fässern'},
            {'name': 'Planks Whiskey', 'price': '6,28', 'img_path': '/userdata/dcshop/images/thumb_2/31376_planks_whiskey.jpg', 'desc': '3 Räucherbretter aus Whiskey-Fässern'},
            {'name': 'Räuchermehl Whisky 450 g', 'price': '4,01', 'img_path': '/userdata/dcshop/images/thumb_2/31350_cold_smoking_dust_whisky.jpg', 'desc': '450 g Räuchermehl für Kaltrauch'},
            {'name': 'Räuchermehl Weißwein süß 450 g', 'price': '4,01', 'img_path': '/userdata/dcshop/images/thumb_2/31351_cold_smoking_dust_sweet_white_wine.jpg', 'desc': '450 g Räuchermehl, Süßwein'},
            {'name': 'Premium Smoke Generator', 'price': '15,10', 'img_path': '/userdata/dcshop/images/thumb_2/564559_chipsmoker.png', 'desc': 'Edelstahl 304, für Kaltrauch'},
            {'name': 'Pellet Smoke Tube', 'price': '12,07', 'img_path': '/userdata/dcshop/images/thumb_2/31369_pellet_smoker.png', 'desc': 'Edelstahl 304, für Pellets'},
            {'name': 'Foodie Power Blocks Cognac 4×200 g', 'price': '6,13', 'img_path': '/userdata/dcshop/images/thumb_2/30815_delantera.png', 'desc': '4 × 200 g Räucherblöcke, Cognac'},
            {'name': 'Foodie Power Blocks Whisky 4×200 g', 'price': '6,13', 'img_path': '/userdata/dcshop/images/thumb_2/30818_delantera.png', 'desc': '4 × 200 g Räucherblöcke, Whisky'},
        ],
        'fetch_images': False,
    },
]

# ─── FETCH IMAGES FOR TMS AND EHB ────────────────────────────────────────────

def fetch_brand_images(brand):
    """For brands with fetch_images=True, fetch page HTML and extract thumb_2 URLs."""
    print(f"\n  Lade {brand['name']} Seite für Bilder...")
    html = fetch_html(brand['source_url'])
    if not html:
        print(f"  WARNUNG: Konnte {brand['source_url']} nicht laden")
        return
    imgs = extract_thumb2_images(html)
    print(f"  Gefunden: {len(imgs)} Bilder auf der Seite")
    # Map images to products by position or name matching
    # Assign images sequentially to products that have empty img_path
    img_idx = 0
    for p in brand['products']:
        if p['img_path'].endswith('/'):
            if img_idx < len(imgs):
                p['img_path'] = imgs[img_idx]
                img_idx += 1

# ─── IMAGE DOWNLOAD ────────────────────────────────────────────────────────────

def process_brand_images(brand):
    """Download all images for a brand and update img_path to local paths."""
    brand['img_dir'].mkdir(parents=True, exist_ok=True)
    slug = brand['slug']

    for i, p in enumerate(brand['products']):
        src = p['img_path']
        if not src or src.endswith('/'):
            p['local_img'] = '/img/ui/placeholder.png'
            continue

        # Full URL
        if src.startswith('/'):
            full_url = MONTARGO_BASE + src
        else:
            full_url = src

        # Local filename
        orig_name = src.split('/')[-1]
        ext = Path(orig_name).suffix or '.jpg'
        local_name = f"montargo-{slug}-{i+1:02d}{ext}"
        local_path = brand['img_dir'] / local_name

        ok = download_image(full_url, local_path)
        if ok:
            p['local_img'] = f"/img/{slug}/{local_name}"
        else:
            # Try to use already downloaded file
            existing = list(brand['img_dir'].glob(f"montargo-{slug}-{i+1:02d}.*"))
            if existing:
                p['local_img'] = f"/img/{slug}/{existing[0].name}"
            else:
                p['local_img'] = '/img/ui/placeholder.png'

# ─── HTML GENERATION ─────────────────────────────────────────────────────────

def generate_brand_page(brand):
    """Generate hersteller page HTML for a brand."""
    cards = "\n".join(product_card(p['name'], p['price'], p['local_img'], p.get('desc',''))
                      for p in brand['products'])

    content = f"""    <section class="serie-layout">
      <div class="container">
        <div class="serie-main">
          <section class="product-section">
            <h2>{brand['name']} Produkte</h2>
            <div class="product-grid product-grid--wide">
{cards}
            </div>
          </section>
        </div>
{sidebar_box(brand['name'], brand['canonical'])}
      </div>
    </section>
{info_section(brand['info'])}"""

    page = html_page(
        brand['title'],
        brand['meta_desc'],
        brand['canonical'],
        brand['breadcrumbs'],
        brand['h1'],
        brand['hero_text'],
        content,
        None,
    )

    brand['dir'].mkdir(parents=True, exist_ok=True)
    out_path = brand['dir'] / 'index.html'
    out_path.write_text(page, encoding='utf-8')
    print(f"  ERSTELLT: {out_path.relative_to(BASE_DIR)}")

# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("scrape-montargo.py – Montargo Markenseiten")
    print("=" * 60)

    for brand in BRANDS:
        print(f"\n{'─'*50}")
        print(f"Marke: {brand['name']}")

        # Fetch images from page for brands that need it
        if brand.get('fetch_images'):
            fetch_brand_images(brand)

        # Download images
        print(f"  Lade Bilder herunter → img/{brand['slug']}/")
        process_brand_images(brand)

        # Generate HTML page
        generate_brand_page(brand)

        time.sleep(0.5)

    print(f"\n{'='*60}")
    print("FERTIG. Alle Markenseiten erstellt.")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
