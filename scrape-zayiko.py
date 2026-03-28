# -*- coding: utf-8 -*-
import urllib.request
import urllib.parse
import re
import sys
import io
import json
import os
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).parent
IMG_DIR = BASE_DIR / "img" / "zayiko"
IMG_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

OLEIO_BASE = "https://www.oleio.de"

# Serien die wir scrapen (Messertaschen weglassen)
SERIEN_SLUGS = [
    ("profi-serie",              "Profi Serie"),
    ("black-magma",              "Black Magma"),
    ("kurumi-nussbaum-serie",    "Kurumi Nussbaum"),
    ("black-edition",            "Black Edition"),
    ("kinone-serie",             "Kinone Serie"),
    ("mysticmagma-serie",        "MysticMagma Serie"),
    ("minami-oliven-serie",      "Minami Oliven-Serie"),
    ("limited-edition",          "Limited Edition"),
    ("kasshoku-serie-i-top-deal","Kasshoku Serie"),
    ("kuro-serie-i-top-deal",    "Kuro Serie"),
    ("steakmesser-set",          "Steakmesser-Set"),
    ("izumi-edelstahl-serie",    "Izumi Edelstahl-Serie"),
    ("nami-edelstahl-serie",     "Nami Edelstahl-Serie"),
]

# Texte für die Serien (SEO-Beschreibungen)
SERIEN_INFO = {
    "profi-serie": {
        "headline": "Zayiko Profi Serie – Damastzahl auf höchstem Niveau",
        "beschreibung": "Die Profi Serie vereint 67 Lagen Damaststahl mit einem handgearbeiteten Ahornholzgriff. Jede Klinge ist von Hand geschliffen und poliert – für Köche, die beim Schneidverhalten keine Kompromisse machen.",
        "merkmale": ["67 Lagen Damaststahl", "VG10-Kern", "Ahornholzgriff", "Handgeschliffen", "HRC 60±2"],
    },
    "black-magma": {
        "headline": "Zayiko Black Magma – Dunkel. Scharf. Unerbittlich.",
        "beschreibung": "Die Black Magma Serie besticht durch ihre schwarze, säuregeätzte Damaststahl-Klinge mit Kupfer-Bronze-Akzent am Griff. Sechs Klingenformen – von Chefmesser bis Kiritsuke – für den modernen Profi.",
        "merkmale": ["67 Lagen Damaststahl", "Schwarze Säureätzung", "Kupfer-Bronze-Detail", "Ahornholzgriff", "HRC 60±2"],
    },
    "kurumi-nussbaum-serie": {
        "headline": "Zayiko Kurumi – Nussbaum trifft Damaststahl",
        "beschreibung": "Die Kurumi Serie kombiniert 67 Lagen Damaststahl mit einem edlen Nussbaumholz-Griff. Die warme Maserung des Walnussholzes macht jedes Messer zum Einzelstück – perfekt für ambitionierte Hobbyköche.",
        "merkmale": ["67 Lagen Damaststahl", "Nussbaumholz-Griff", "VG10-Kern", "Handgeschliffen", "HRC 60±2"],
    },
    "black-edition": {
        "headline": "Zayiko Black Edition – Eleganz in Schwarz",
        "beschreibung": "Die Black Edition kombiniert eine klassische Damaststahl-Klinge mit einem durchgehend schwarzen Pakkaholz-Griff. Zeitlose Optik trifft auf bewährte Schnitthaltigkeit – für die moderne Küche.",
        "merkmale": ["67 Lagen Damaststahl", "Schwarzer Pakkaholz-Griff", "VG10-Kern", "Langlebige Schärfe", "HRC 60±2"],
    },
    "kinone-serie": {
        "headline": "Zayiko Kinone – Japanisches Handwerk in Reinform",
        "beschreibung": "Die Kinone Serie steht für reduzierten japanischen Stil. Die helle Holzmaserung des Ahorngriffs setzt einen bewussten Kontrast zur dunklen Damaststruktur – Ästhetik und Funktion in Balance.",
        "merkmale": ["67 Lagen Damaststahl", "Ahornholz-Griff", "VG10-Kern", "Handfinish", "HRC 60±2"],
    },
    "mysticmagma-serie": {
        "headline": "Zayiko MysticMagma – Mystisch scharf",
        "beschreibung": "Die MysticMagma Serie verbindet die Intensität des Black Magma Designs mit einem Hauch Farbe. Eine außergewöhnliche Klingenästhetik für Köche, die nicht nur mit Schärfe überzeugen wollen.",
        "merkmale": ["67 Lagen Damaststahl", "Säuregeätzte Klinge", "Farbiger Griffakzent", "VG10-Kern", "HRC 60±2"],
    },
    "minami-oliven-serie": {
        "headline": "Zayiko Minami – Olivenholz trifft Japan",
        "beschreibung": "Die Minami Oliven-Serie bringt mediterranes Flair in die japanische Messerkunst. Der Olivenholzgriff mit seiner einzigartigen Maserung gibt jedem Messer einen unverwechselbaren Charakter.",
        "merkmale": ["67 Lagen Damaststahl", "Olivenholz-Griff", "VG10-Kern", "Natürliche Maserung", "HRC 60±2"],
    },
    "limited-edition": {
        "headline": "Zayiko Limited Edition – Selten und begehrt",
        "beschreibung": "Die Limited Edition vereint außergewöhnliche Materialien mit handwerklicher Meisterschaft. Diese Messer sind auf geringe Stückzahlen limitiert – für Sammler und anspruchsvolle Köche.",
        "merkmale": ["67 Lagen Damaststahl", "Edles Griffmaterial", "Limitierte Auflage", "Handgefertigt", "HRC 60±2"],
    },
    "kasshoku-serie-i-top-deal": {
        "headline": "Zayiko Kasshoku – Damaststahl zum Top-Preis",
        "beschreibung": "Die Kasshoku Serie bietet echten japanischen Damaststahl zu einem unschlagbaren Preis-Leistungs-Verhältnis. Perfekter Einstieg in die Welt der Damastmesser ohne Kompromisse bei der Qualität.",
        "merkmale": ["Damaststahl", "Ergonomischer Griff", "Vielseitige Klingenformen", "Top-Preis-Leistung", "Für Einsteiger"],
    },
    "kuro-serie-i-top-deal": {
        "headline": "Zayiko Kuro – Schwarz. Scharf. Erschwinglich.",
        "beschreibung": "Die Kuro Serie überzeugt mit schwarzer Klingenoptik und solidem Damaststahl zu einem attraktiven Einstiegspreis. Für alle, die den Black Magma Look ohne großes Budget möchten.",
        "merkmale": ["Damaststahl", "Schwarze Klinge", "Ergonomischer Griff", "Top-Preis-Leistung", "Für Einsteiger"],
    },
    "steakmesser-set": {
        "headline": "Zayiko Steakmesser-Sets – Das perfekte Grillbesteck",
        "beschreibung": "Zayiko Steakmesser-Sets verbinden scharfe Damastklingen mit hochwertigen Griffen. Ob zum Grillen oder am Tisch – diese Sets hinterlassen einen bleibenden Eindruck.",
        "merkmale": ["Damaststahl-Klingen", "Scharfe Schneidkante", "Elegante Sets", "Spülmaschinengeeignet", "Perfekt zum Grillen"],
    },
    "izumi-edelstahl-serie": {
        "headline": "Zayiko Izumi – Edelstahl für den Alltag",
        "beschreibung": "Die Izumi Edelstahl-Serie bietet robuste Messer für den täglichen Einsatz. Korrosionsbeständiger Stahl und ergonomische Griffe machen sie zur zuverlässigen Wahl für die Alltagsküche.",
        "merkmale": ["Rostfreier Edelstahl", "Ergonomischer Griff", "Pflegeleicht", "Korrosionsbeständig", "Alltagstauglich"],
    },
    "nami-edelstahl-serie": {
        "headline": "Zayiko Nami – Wellenschliff für anspruchsvolle Schnitte",
        "beschreibung": "Die Nami Edelstahl-Serie kombiniert robusten Edelstahl mit feinem Wellenschliff. Ideal für Brot, Tomaten und andere Lebensmittel, die eine gezahnte Klinge erfordern.",
        "merkmale": ["Rostfreier Edelstahl", "Wellenschliff", "Ergonomischer Griff", "Pflegeleicht", "Vielseitig einsetzbar"],
    },
}


def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    return urllib.request.urlopen(req, timeout=20).read().decode("utf-8", errors="replace")


import time


def get_fullsize_from_detail(detail_url):
    """Holt die Vollbild-URL von der Produktdetailseite."""
    try:
        html = fetch(detail_url)
        # Hauptbild auf Detailseite: img ohne Größensuffix
        imgs = re.findall(r'https://www\.oleio\.de/media/image/[^\s"\'<>]+', html)
        for img in imgs:
            # Vollbild hat kein _WxH Suffix
            if not re.search(r'_\d+x\d+', img) and not img.endswith('.gif') and 'Category' not in img and 'logo' not in img:
                return img.rstrip(',')
    except Exception as e:
        pass
    return None


def scrape_serie(slug):
    url = f"{OLEIO_BASE}/zayiko/{slug}"
    print(f"  Lade Listing: {url}")
    html = fetch(url)

    products = []
    # Produkt-Blöcke: div mit data-ordernumber
    blocks = re.split(r'(?=<div[^>]+class="product--box[^"]*"[^>]*data-ordernumber)', html)

    for block in blocks[1:]:  # erstes Element ist Seiten-Header
        # Ordernumber / SKU
        sku_m = re.search(r'data-ordernumber="([^"]+)"', block)
        if not sku_m:
            continue

        # Name aus product--title
        name_m = re.search(r'class="product--title"[^>]*>(.*?)</a>', block, re.DOTALL)
        if not name_m:
            continue
        name = re.sub(r'<[^>]+>', '', name_m.group(1)).strip()
        name = re.sub(r'\s+', ' ', name)

        # Preis
        price_m = re.search(r'class="price--default[^"]*"[^>]*>\s*([0-9]+[,\.][0-9]+)', block)
        price = price_m.group(1).strip().replace(',', '.') if price_m else ""

        # Detailseiten-Link
        detail_m = re.search(r'href="(https://www\.oleio\.de/[^"]+)"', block)
        detail_url = detail_m.group(1) if detail_m else None

        products.append({
            "name": name,
            "price": price,
            "detail_url": detail_url,
            "img_url": None,  # wird unten befüllt
        })

    # Vollbilder von Detailseiten holen
    print(f"  Lade {len(products)} Detailseiten...")
    for p in products:
        if p["detail_url"]:
            img_url = get_fullsize_from_detail(p["detail_url"])
            p["img_url"] = img_url
            time.sleep(0.3)  # höfliche Pause

    return products


def download_image(url, dest_path):
    if dest_path.exists():
        return False, dest_path.stat().st_size
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        data = urllib.request.urlopen(req, timeout=20).read()
        dest_path.write_bytes(data)
        return True, len(data)
    except Exception as e:
        print(f"    FEHLER beim Download: {e}")
        return False, 0


def local_filename(serie_slug, img_url):
    if not img_url:
        return None
    fname = Path(img_url.split("?")[0]).name
    return f"zayiko-{serie_slug}-{fname}"


# ─── HTML Generator ───────────────────────────────────────────────────────────

NAV_HTML = """    <nav class="breadcrumb" aria-label="Breadcrumb">
      <ol itemscope itemtype="https://schema.org/BreadcrumbList">
        <li itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem">
          <a itemprop="item" href="/"><span itemprop="name">Start</span></a>
          <meta itemprop="position" content="1">
        </li>
        <li itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem">
          <a itemprop="item" href="/hersteller/"><span itemprop="name">Hersteller</span></a>
          <meta itemprop="position" content="2">
        </li>
        <li itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem">
          <a itemprop="item" href="/hersteller/zayiko/"><span itemprop="name">Zayiko</span></a>
          <meta itemprop="position" content="3">
        </li>
      </ol>
    </nav>"""


def generate_serie_page(serie_slug, serie_name, produkte, info):
    headline = info.get("headline", f"Zayiko {serie_name}")
    beschreibung = info.get("beschreibung", "")
    merkmale = info.get("merkmale", [])

    merkmale_html = "\n".join(
        f'            <li><span class="check">✓</span> {m}</li>'
        for m in merkmale
    )

    produkte_html = ""
    for p in produkte:
        local_fname = local_filename(serie_slug, p["img_url"])
        if local_fname:
            img_src = f"/img/zayiko/{local_fname}"
        else:
            img_src = "/img/ui/placeholder.png"
        price_str = f"ab €{p['price']}" if p['price'] else ""
        produkte_html += f"""
          <article class="product-card">
            <div class="product-img-wrap">
              <img data-src="{img_src}" src="/img/ui/placeholder.png" alt="{p['name']}" class="lazy" loading="lazy">
            </div>
            <div class="product-info">
              <h3>{p['name']}</h3>
              {"<p class='product-price'>" + price_str + "</p>" if price_str else ""}
            </div>
          </article>"""

    return f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{headline} | Feuerhaus Kalina Würzburg</title>
  <meta name="description" content="{beschreibung[:155]}">
  <link rel="canonical" href="https://grills.feuerhaus-kalina.de/hersteller/zayiko/{serie_slug}/">
  <link rel="icon" href="/img/ui/favicon.ico">
  <link rel="stylesheet" href="/css/style.css">
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      {{"@type":"ListItem","position":1,"name":"Start","item":"https://grills.feuerhaus-kalina.de/"}},
      {{"@type":"ListItem","position":2,"name":"Hersteller","item":"https://grills.feuerhaus-kalina.de/hersteller/"}},
      {{"@type":"ListItem","position":3,"name":"Zayiko","item":"https://grills.feuerhaus-kalina.de/hersteller/zayiko/"}},
      {{"@type":"ListItem","position":4,"name":"{serie_name}","item":"https://grills.feuerhaus-kalina.de/hersteller/zayiko/{serie_slug}/"}}
    ]
  }}
  </script>
</head>
<body>
  <header class="site-header">
    <div class="container header-inner">
      <a href="/" class="logo"><img src="/img/ui/logo.svg" alt="Feuerhaus Kalina" width="180" height="48"></a>
      <nav class="main-nav" aria-label="Hauptnavigation">
        <ul>
          <li><a href="/outdoor-kuechen/">Outdoor-Küchen</a></li>
          <li><a href="/keramikgrills-kamado/">Keramikgrills</a></li>
          <li><a href="/plancha-feuerplatten/">Plancha</a></li>
          <li><a href="/hersteller/" class="active">Hersteller</a></li>
          <li><a href="/ratgeber/">Ratgeber</a></li>
          <li><a href="/kontakt/">Kontakt</a></li>
        </ul>
      </nav>
    </div>
  </header>

  <main>
    <section class="page-hero">
      <div class="container">
{NAV_HTML}
        <h1>{headline}</h1>
        <p class="hero-lead">{beschreibung}</p>
      </div>
    </section>

    <section class="serie-content container">
      <div class="serie-layout">
        <div class="product-grid">
{produkte_html}
        </div>

        <aside class="serie-sidebar sticky-sidebar">
          <div class="sidebar-box">
            <h3>Merkmale</h3>
            <ul class="merkmale-list">
{merkmale_html}
            </ul>
          </div>
          <div class="sidebar-box cta-box">
            <h3>Persönliche Beratung</h3>
            <p>Unsicher welches Messer zu Ihnen passt? Wir helfen Ihnen gerne in unserer Ausstellung in Würzburg.</p>
            <a href="/ausstellung-beratung/" class="btn btn-primary">Zur Ausstellung</a>
            <a href="/kontakt/" class="btn btn-outline">Kontakt aufnehmen</a>
          </div>
        </aside>
      </div>
    </section>
  </main>

  <footer class="site-footer">
    <div class="container footer-inner">
      <p>&copy; 2025 Feuerhaus Kalina GmbH &middot; <a href="/impressum/">Impressum</a> &middot; <a href="/datenschutz/">Datenschutz</a></p>
    </div>
  </footer>

  <div id="cookie-banner" class="cookie-banner" role="dialog" aria-label="Cookie-Hinweis">
    <p>Wir nutzen Cookies für eine optimale Nutzererfahrung. <a href="/datenschutz/">Mehr erfahren</a></p>
    <button onclick="document.getElementById('cookie-banner').style.display='none';localStorage.setItem('cookies','1')" class="btn btn-primary btn-sm">Akzeptieren</button>
  </div>
  <script>if(localStorage.getItem('cookies'))document.getElementById('cookie-banner').style.display='none';</script>
  <script>
    document.addEventListener('DOMContentLoaded',function(){{
      var lazy=document.querySelectorAll('img.lazy');
      if('IntersectionObserver' in window){{
        var obs=new IntersectionObserver(function(entries){{entries.forEach(function(e){{if(e.isIntersecting){{e.target.src=e.target.dataset.src;obs.unobserve(e.target);}}}});}});
        lazy.forEach(function(img){{obs.observe(img);}});
      }} else {{
        lazy.forEach(function(img){{img.src=img.dataset.src;}});
      }}
    }});
  </script>
</body>
</html>
"""


def generate_index_page(alle_serien):
    cards_html = ""
    for slug, name, produkte in alle_serien:
        count = len(produkte)
        info = SERIEN_INFO.get(slug, {})
        hero_fname = None
        if produkte and produkte[0]["img_url"]:
            hero_fname = local_filename(slug, produkte[0]["img_url"])
        hero_img = f"/img/zayiko/{hero_fname}" if hero_fname else "/img/ui/placeholder.png"
        desc = info.get("beschreibung", "")[:120] + "…" if info.get("beschreibung") else ""

        cards_html += f"""
      <article class="serie-card">
        <a href="/hersteller/zayiko/{slug}/">
          <div class="serie-card-img">
            <img data-src="{hero_img}" src="/img/ui/placeholder.png" alt="Zayiko {name}" class="lazy" loading="lazy">
          </div>
          <div class="serie-card-body">
            <span class="eyebrow">{count} Produkte</span>
            <h2>{name}</h2>
            <p>{desc}</p>
            <span class="btn-link">Zur Serie &rarr;</span>
          </div>
        </a>
      </article>"""

    return f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Zayiko Damastmesser – Alle Serien | Feuerhaus Kalina Würzburg</title>
  <meta name="description" content="Entdecken Sie alle Zayiko Damastmesser-Serien: von der Profi Serie bis zur Black Magma Edition. Erhältlich in unserer Ausstellung in Würzburg.">
  <link rel="canonical" href="https://grills.feuerhaus-kalina.de/hersteller/zayiko/">
  <link rel="icon" href="/img/ui/favicon.ico">
  <link rel="stylesheet" href="/css/style.css">
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      {{"@type":"ListItem","position":1,"name":"Start","item":"https://grills.feuerhaus-kalina.de/"}},
      {{"@type":"ListItem","position":2,"name":"Hersteller","item":"https://grills.feuerhaus-kalina.de/hersteller/"}},
      {{"@type":"ListItem","position":3,"name":"Zayiko","item":"https://grills.feuerhaus-kalina.de/hersteller/zayiko/"}}
    ]
  }}
  </script>
</head>
<body>
  <header class="site-header">
    <div class="container header-inner">
      <a href="/" class="logo"><img src="/img/ui/logo.svg" alt="Feuerhaus Kalina" width="180" height="48"></a>
      <nav class="main-nav" aria-label="Hauptnavigation">
        <ul>
          <li><a href="/outdoor-kuechen/">Outdoor-Küchen</a></li>
          <li><a href="/keramikgrills-kamado/">Keramikgrills</a></li>
          <li><a href="/plancha-feuerplatten/">Plancha</a></li>
          <li><a href="/hersteller/" class="active">Hersteller</a></li>
          <li><a href="/ratgeber/">Ratgeber</a></li>
          <li><a href="/kontakt/">Kontakt</a></li>
        </ul>
      </nav>
    </div>
  </header>

  <main>
    <section class="page-hero">
      <div class="container">
        <nav class="breadcrumb" aria-label="Breadcrumb">
          <ol itemscope itemtype="https://schema.org/BreadcrumbList">
            <li itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem">
              <a itemprop="item" href="/"><span itemprop="name">Start</span></a>
              <meta itemprop="position" content="1">
            </li>
            <li itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem">
              <a itemprop="item" href="/hersteller/"><span itemprop="name">Hersteller</span></a>
              <meta itemprop="position" content="2">
            </li>
            <li itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem">
              <span itemprop="name">Zayiko</span>
              <meta itemprop="position" content="3">
            </li>
          </ol>
        </nav>
        <h1>Zayiko Damastmesser – Alle Serien</h1>
        <p class="hero-lead">Von der klassischen Profi Serie bis zur mystischen Black Magma Edition: Zayiko vereint japanische Klingenkunst mit modernem Design. Alle Serien zum Anfassen in unserer Ausstellung in Würzburg.</p>
      </div>
    </section>

    <section class="serien-uebersicht container">
      <div class="serien-grid">
{cards_html}
      </div>
    </section>

    <section class="info-block container">
      <div class="info-cols">
        <div>
          <h2>Was macht Zayiko besonders?</h2>
          <p>Zayiko steht für handgefertigte Damastmesser, die sich durch außergewöhnliche Schärfe, langanhaltende Schnitthaltigkeit und eine unverwechselbare Klingenästhetik auszeichnen. Der VG10-Stahlkern mit 67 Damaststahl-Lagen ist das Herzstück jedes Messers.</p>
        </div>
        <div>
          <h2>Beratung in Würzburg</h2>
          <p>In unserer Ausstellung können Sie alle Zayiko-Serien persönlich in Augenschein nehmen. Unsere Experten helfen Ihnen, das passende Messer für Ihren Kochstil zu finden.</p>
          <a href="/ausstellung-beratung/" class="btn btn-primary">Ausstellung besuchen</a>
        </div>
      </div>
    </section>
  </main>

  <footer class="site-footer">
    <div class="container footer-inner">
      <p>&copy; 2025 Feuerhaus Kalina GmbH &middot; <a href="/impressum/">Impressum</a> &middot; <a href="/datenschutz/">Datenschutz</a></p>
    </div>
  </footer>

  <div id="cookie-banner" class="cookie-banner" role="dialog" aria-label="Cookie-Hinweis">
    <p>Wir nutzen Cookies für eine optimale Nutzererfahrung. <a href="/datenschutz/">Mehr erfahren</a></p>
    <button onclick="document.getElementById('cookie-banner').style.display='none';localStorage.setItem('cookies','1')" class="btn btn-primary btn-sm">Akzeptieren</button>
  </div>
  <script>if(localStorage.getItem('cookies'))document.getElementById('cookie-banner').style.display='none';</script>
  <script>
    document.addEventListener('DOMContentLoaded',function(){{
      var lazy=document.querySelectorAll('img.lazy');
      if('IntersectionObserver' in window){{
        var obs=new IntersectionObserver(function(entries){{entries.forEach(function(e){{if(e.isIntersecting){{e.target.src=e.target.dataset.src;obs.unobserve(e.target);}}}});}});
        lazy.forEach(function(img){{obs.observe(img);}});
      }} else {{
        lazy.forEach(function(img){{img.src=img.dataset.src;}});
      }}
    }});
  </script>
</body>
</html>
"""


# ─── MAIN ─────────────────────────────────────────────────────────────────────

print("Zayiko Produkt-Scraper & HTML-Generator")
print("=" * 60)
print(f"Bilder → {IMG_DIR}")
print()

alle_serien = []
gesamt_produkte = 0
gesamt_geladen = 0

for slug, name in SERIEN_SLUGS:
    print(f"── {name} ──")
    try:
        produkte = scrape_serie(slug)
    except Exception as e:
        print(f"  FEHLER: {e}")
        produkte = []

    print(f"  {len(produkte)} Produkte gefunden")

    for p in produkte:
        if not p["img_url"]:
            print(f"  Kein Bild: {p['name'][:50]}")
            continue
        local_fname = local_filename(slug, p["img_url"])
        dest = IMG_DIR / local_fname
        new, size = download_image(p["img_url"], dest)
        status = "↓" if new else "✓"
        print(f"  {status} {local_fname} → {size//1024} KB")
        if new:
            gesamt_geladen += 1

    gesamt_produkte += len(produkte)
    alle_serien.append((slug, name, produkte))
    print()

# HTML-Seiten generieren
print("Generiere HTML-Seiten...")

# Index-Seite (bestehende hersteller/zayiko/index.html überschreiben)
out_dir = BASE_DIR / "hersteller" / "zayiko"
out_dir.mkdir(parents=True, exist_ok=True)
(out_dir / "index.html").write_text(generate_index_page(alle_serien), encoding="utf-8")
print("  ✓ hersteller/zayiko/index.html")

# Serie-Unterseiten
for slug, name, produkte in alle_serien:
    info = SERIEN_INFO.get(slug, {})
    serie_dir = out_dir / slug
    serie_dir.mkdir(parents=True, exist_ok=True)
    html = generate_serie_page(slug, name, produkte, info)
    (serie_dir / "index.html").write_text(html, encoding="utf-8")
    print(f"  ✓ hersteller/zayiko/{slug}/index.html")

# JSON
data_dir = BASE_DIR / "data"
data_dir.mkdir(exist_ok=True)
data = [{"serie": name, "slug": slug, "produkte": produkte} for slug, name, produkte in alle_serien]
(data_dir / "zayiko-produkte.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("  ✓ data/zayiko-produkte.json")

print()
print("=" * 60)
print("FERTIG")
print("=" * 60)
print(f"  Serien:        {len(alle_serien)}")
print(f"  Produkte:      {gesamt_produkte}")
print(f"  Neu geladen:   {gesamt_geladen}")
print(f"  HTML-Seiten:   {len(alle_serien) + 1}")
print("=" * 60)
