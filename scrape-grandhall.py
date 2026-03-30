# -*- coding: utf-8 -*-
"""
Grandhall Scraper & HTML-Generator
Fetches product images from grandhall.eu and generates pages for hersteller/grandhall/
"""
import urllib.request
import urllib.parse
import re
import sys
import io
import time
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).parent
IMG_DIR = BASE_DIR / "img" / "grandhall"
IMG_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
}

BASE_URL = "https://grandhall.eu"

# ─── Modell-Familien ────────────────────────────────────────────────────────────
FAMILIEN = [
    {
        "slug": "xenon",
        "name": "Xenon Serie",
        "headline": "Grandhall Xenon Serie – Modern & Vielseitig",
        "beschreibung": "Die Xenon-Serie von Grandhall verbindet modernes Design mit einem kontrastierenden schwarzen Rahmen. Mit bis zu 4 Edelstahl-Brennern, Seitenbrenner und gusseisernem Grillrost bieten die Xenon-Grills alles für perfekte Grillabende – auch als Holzkohlevariante erhältlich.",
        "merkmale": ["Kontrastierender schwarzer Rahmen", "Edelstahl-Brenner (403)", "Gusseiserner Grillrost", "Seitenbrenner 3,4 kW", "Stabiles Fahrgestell mit Rädern"],
        "produkte": [
            {"slug": "grandhall-xenon-3", "name": "Xenon 3 Gasgrill", "typ": "Gasgrill"},
            {"slug": "grandhall-xenon-4", "name": "Xenon 4 Gasgrill", "typ": "Gasgrill"},
            {"slug": "grandhall-xenon-houtskool", "name": "Xenon Holzkohlegrill", "typ": "Holzkohlegrill"},
        ],
    },
    {
        "slug": "classic",
        "name": "Classic G2 Serie",
        "headline": "Grandhall Classic G2 – Der bewährte Klassiker",
        "beschreibung": "Der Classic G2 ist Grandhalls bewährter Einstiegsklassiker mit 2 leistungsstarken Edelstahl-Brennern. Erhältlich als freistehender Gasgrill und als Einbauversion für Outdoor-Küchen.",
        "merkmale": ["2 Edelstahl-Brenner", "Gusseiserner Grillrost", "Piezo-Zündung", "Erhältlich als Einbauversion", "Robuste Verarbeitung"],
        "produkte": [
            {"slug": "grandhall-classic-g2", "name": "Classic G2 Gasgrill", "typ": "Gasgrill"},
            {"slug": "grandhall-classic-g2-inbouw", "name": "Classic G2 Einbaugrill", "typ": "Einbaugrill"},
        ],
    },
    {
        "slug": "premium",
        "name": "Premium Serie",
        "headline": "Grandhall Premium Serie – Mehr Leistung, mehr Genuss",
        "beschreibung": "Die Premium-Serie bietet herausragende Grillleistung mit 3–4 Edelstahl-Brennern, optionalem Sear-Brenner und hochwertiger gusseiserner Rostfläche. Ideal für ambitionierte Grillmeister.",
        "merkmale": ["3–4 Edelstahl-Brenner", "Optionaler Sear-Brenner", "Gusseiserner Grillrost", "Erhältlich als Einbauversion", "Robustes Edelstahl-Gehäuse"],
        "produkte": [
            {"slug": "grandhall-premium-g3", "name": "Premium G3 Gasgrill", "typ": "Gasgrill"},
            {"slug": "grandhall-premium-g4", "name": "Premium G4 Gasgrill", "typ": "Gasgrill"},
            {"slug": "grandhall-premium-g3-inbouw", "name": "Premium G3 Einbaugrill", "typ": "Einbaugrill"},
            {"slug": "grandhall-premium-plus-g3-inbouw", "name": "Premium Plus G3 Einbaugrill", "typ": "Einbaugrill"},
            {"slug": "grandhall-premium-g4-inbouw", "name": "Premium G4 Einbaugrill", "typ": "Einbaugrill"},
        ],
    },
    {
        "slug": "maxim",
        "name": "Maxim Serie",
        "headline": "Grandhall Maxim Serie – Profi-Grillen auf höchstem Niveau",
        "beschreibung": "Die Maxim-Serie steht für professionelles Grillen mit 4–5 Hochleistungsbrennern, integriertem Sear-Brenner und großzügiger Grillfläche. Für alle, die kompromisslos grillen wollen.",
        "merkmale": ["4–5 Edelstahl-Brenner", "Integrierter Sear-Brenner", "Große Grillfläche", "Erhältlich als Einbauversion", "Für Outdoor-Küchen geeignet"],
        "produkte": [
            {"slug": "grandhall-maxim-g4", "name": "Maxim G4 Gasgrill", "typ": "Gasgrill"},
            {"slug": "grandhall-maxim-g5", "name": "Maxim G5 Gasgrill", "typ": "Gasgrill"},
            {"slug": "grandhall-maxim-g4-inbouw", "name": "Maxim G4 Einbaugrill", "typ": "Einbaugrill"},
            {"slug": "grandhall-maxim-g5-inbouw", "name": "Maxim G5 Einbaugrill", "typ": "Einbaugrill"},
        ],
    },
    {
        "slug": "elite",
        "name": "Elite Serie",
        "headline": "Grandhall Elite Serie – Das Flaggschiff der Gasgrill-Welt",
        "beschreibung": "Die Elite-Serie repräsentiert das Beste, was Grandhall zu bieten hat. Mit bis zu 5 Brennern, Infrarot-Sear-Brenner, Rotisserie-Vorbereitung und eleganter Edelstahl-Optik setzt die Elite-Serie neue Maßstäbe.",
        "merkmale": ["4–5 Brenner + Infrarot Sear-Brenner", "Rotisserie-Vorbereitung", "Edles Edelstahl-Design", "Erhältlich als Einbauversion", "Maximale Grillperformance"],
        "produkte": [
            {"slug": "grandhall-elite-g4", "name": "Elite G4 Gasgrill", "typ": "Gasgrill"},
            {"slug": "grandhall-elite-g5", "name": "Elite G5 Gasgrill", "typ": "Gasgrill"},
            {"slug": "grandhall-elite-g4-inbouw", "name": "Elite G4 Einbaugrill", "typ": "Einbaugrill"},
            {"slug": "grandhall-elite-g5-inbouw", "name": "Elite G5 Einbaugrill", "typ": "Einbaugrill"},
            {"slug": "grandhall-elite-pro-inbouw", "name": "Elite Pro Einbaugrill", "typ": "Einbaugrill"},
        ],
    },
    {
        "slug": "e-grill",
        "name": "E-Grill",
        "headline": "Grandhall E-Grill – Elektrisch grillen ohne Kompromisse",
        "beschreibung": "Der Grandhall E-Grill ermöglicht Genuss auf dem Balkon oder der Terrasse – ohne Gas, ohne Kohle. Mit gusseisernen Rost- und Backplattenoptionen und einem kompakten Design für überall.",
        "merkmale": ["Elektrischer Betrieb", "Gusseiserner Grillrost", "Ideal für Balkon & Terrasse", "Kompaktes Design", "Optionale Gusseisenplatten"],
        "produkte": [
            {"slug": "grandhall-e-grill", "name": "E-Grill", "typ": "Elektrogrill"},
        ],
    },
]


# ─── Hilfsfunktionen ─────────────────────────────────────────────────────────────

def fetch_html(url):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        return urllib.request.urlopen(req, timeout=25).read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"    FETCH-FEHLER {url}: {e}")
        return ""


def extract_images_from_html(html):
    """Findet alle wp-content/uploads Bild-URLs, bereinigt Thumbnail-Suffixe."""
    # Finde alle wp-content/uploads URLs
    raw = re.findall(r'https://grandhall\.eu/wp-content/uploads/[^\s"\'<>]+\.(?:png|jpg|jpeg|webp)', html, re.IGNORECASE)
    seen = set()
    result = []
    for url in raw:
        # Entferne Thumbnail-Suffix wie -300x300, -150x150, -scaled etc.
        clean = re.sub(r'-\d+x\d+(?=\.(png|jpg|jpeg|webp))', '', url)
        clean = re.sub(r'-scaled(?=\.(png|jpg|jpeg|webp))', '', clean)
        if clean not in seen:
            seen.add(clean)
            result.append(clean)
    return result


def extract_title(html):
    m = re.search(r'<h1[^>]*class="[^"]*product_title[^"]*"[^>]*>(.*?)</h1>', html, re.DOTALL)
    if m:
        return re.sub(r'<[^>]+>', '', m.group(1)).strip()
    m = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL)
    if m:
        return re.sub(r'<[^>]+>', '', m.group(1)).strip()
    m = re.search(r'<title>(.*?)[\|\-]', html)
    if m:
        return m.group(1).strip()
    return ""


def extract_description(html):
    """Versucht die kurze Produktbeschreibung zu extrahieren."""
    # WooCommerce short description
    m = re.search(r'class="woocommerce-product-details__short-description"[^>]*>(.*?)</div>', html, re.DOTALL)
    if m:
        text = re.sub(r'<[^>]+>', ' ', m.group(1)).strip()
        text = re.sub(r'\s+', ' ', text)
        return text[:400]
    # Tab description
    m = re.search(r'id="tab-description"[^>]*>(.*?)</div>', html, re.DOTALL)
    if m:
        text = re.sub(r'<[^>]+>', ' ', m.group(1)).strip()
        text = re.sub(r'\s+', ' ', text)
        return text[:400]
    return ""


def download_image(url, dest_path):
    if dest_path.exists():
        return False, dest_path.stat().st_size
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        data = urllib.request.urlopen(req, timeout=20).read()
        dest_path.write_bytes(data)
        return True, len(data)
    except Exception as e:
        print(f"    BILD-FEHLER {url}: {e}")
        return False, 0


def img_filename(produkt_slug, img_url, index):
    ext = Path(img_url.split("?")[0]).suffix or ".jpg"
    return f"grandhall-{produkt_slug}-{index:02d}{ext}"


# ─── Daten sammeln ─────────────────────────────────────────────────────────────

print("Grandhall Scraper & HTML-Generator")
print("=" * 60)
print(f"Bilder → {IMG_DIR}")
print()

# Sammle für jedes Produkt: gefundene Bilder + optionaler Titel aus HTML
alle_produkt_daten = {}  # slug -> {"imgs": [local_filenames], "title": str, "desc": str}

total_downloaded = 0
total_skipped = 0
total_errors = 0

for familie in FAMILIEN:
    print(f"── {familie['name']} ──")
    for produkt in familie["produkte"]:
        slug = produkt["slug"]
        name = produkt["name"]
        url = f"{BASE_URL}/product/{slug}/"

        print(f"  Fetche: {slug}")
        html = fetch_html(url)
        time.sleep(0.5)

        imgs_from_page = extract_images_from_html(html) if html else []

        # Filtere nur sinnvolle Produkt-Bilder (keine Logos, Icons, Social-Media)
        logo_patterns = ["Australian-bbq", "WHITE_outline", "facebook", "instagram", "youtube",
                         "twitter", "linkedin", "grandhall-logo", "favicon", "arrow", "icon"]
        product_imgs = [u for u in imgs_from_page
                        if not any(p.lower() in u.lower() for p in logo_patterns)]

        # Lade Bilder herunter
        local_imgs = []
        for i, img_url in enumerate(product_imgs[:6]):  # max 6 Bilder pro Produkt
            fname = img_filename(slug, img_url, i + 1)
            dest = IMG_DIR / fname
            downloaded, size = download_image(img_url, dest)
            if size > 0:
                local_imgs.append(fname)
                if downloaded:
                    print(f"    ↓ {fname} → {size // 1024} KB")
                    total_downloaded += 1
                else:
                    print(f"    ✓ {fname} (bereits vorhanden)")
                    total_skipped += 1
            else:
                total_errors += 1

        html_title = extract_title(html) if html else ""
        desc = extract_description(html) if html else ""

        # Fallback: Benutze bereits heruntergeladene Bilder aus img/grandhall/
        if not local_imgs:
            # Match exactly: grandhall-{slug}-NN.ext (slug ends before -NN)
            local_imgs = sorted(
                f.name for f in IMG_DIR.glob(f"grandhall-{slug}-*")
                if re.match(rf"grandhall-{re.escape(slug)}-\d+\.", f.name)
            )

        alle_produkt_daten[slug] = {
            "imgs": local_imgs,
            "name": html_title or name,
            "desc": desc,
        }

        if not local_imgs:
            print(f"    ⚠ Keine Bilder gefunden für {slug}")
        elif not html or not extract_images_from_html(html):
            print(f"    ✓ {len(local_imgs)} vorhandene Bilder genutzt")

print()
print(f"Bilder: {total_downloaded} heruntergeladen, {total_skipped} vorhanden, {total_errors} Fehler")
print()


# ─── HTML-Generierung ─────────────────────────────────────────────────────────

def produkt_card_html(produkt_info, local_imgs, familie_slug):
    name = produkt_info["name"]
    anfragen_url = f"/kontakt/?produkt={urllib.parse.quote(name)}"

    if local_imgs:
        main_img = f"/img/grandhall/{local_imgs[0]}"
        img_tag = f'<img data-src="{main_img}" src="/img/ui/placeholder.png" alt="{name}" class="lazy" loading="lazy">'
    else:
        img_tag = f'<img src="/img/ui/placeholder.png" alt="{name}">'

    return f"""          <div class="product-card">
            <div class="product-img-wrap">
              {img_tag}
            </div>
            <div class="product-info">
              <h3>{name}</h3>
              <a href="{anfragen_url}" class="product-anfragen">Anfragen</a>
            </div>
          </div>"""


def generate_familie_page(familie):
    slug = familie["slug"]
    name = familie["name"]
    headline = familie["headline"]
    beschreibung = familie["beschreibung"]

    merkmale_html = "\n".join(
        f'            <li><span class="check">✓</span> {m}</li>'
        for m in familie["merkmale"]
    )

    produkt_cards = ""
    for produkt in familie["produkte"]:
        p_slug = produkt["slug"]
        p_data = alle_produkt_daten.get(p_slug, {"imgs": [], "name": produkt["name"], "desc": ""})
        p_data["name"] = p_data["name"] or produkt["name"]
        produkt_cards += produkt_card_html(p_data, p_data["imgs"], slug) + "\n"

    breadcrumb_pos4 = f'{{"@type":"ListItem","position":4,"name":"{name}","item":"https://grills.feuerhaus-kalina.de/hersteller/grandhall/{slug}/"}}'

    return f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{headline} | Feuerhaus Kalina Würzburg</title>
  <meta name="description" content="{beschreibung[:155]}">
  <link rel="canonical" href="https://grills.feuerhaus-kalina.de/hersteller/grandhall/{slug}/">
  <link rel="icon" href="/img/ui/favicon.ico">
  <link rel="apple-touch-icon" href="/img/ui/apple-touch-icon.png">
  <link rel="stylesheet" href="/css/style.css">
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      {{"@type":"ListItem","position":1,"name":"Start","item":"https://grills.feuerhaus-kalina.de/"}},
      {{"@type":"ListItem","position":2,"name":"Hersteller","item":"https://grills.feuerhaus-kalina.de/hersteller/"}},
      {{"@type":"ListItem","position":3,"name":"Grandhall","item":"https://grills.feuerhaus-kalina.de/hersteller/grandhall/"}},
      {breadcrumb_pos4}
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
      <button class="nav-menu-toggle" aria-label="Menü öffnen" aria-expanded="false">
        <span></span><span></span><span></span>
      </button>
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
              <a itemprop="item" href="/hersteller/grandhall/"><span itemprop="name">Grandhall</span></a>
              <meta itemprop="position" content="3">
            </li>
            <li itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem">
              <span itemprop="name">{name}</span>
              <meta itemprop="position" content="4">
            </li>
          </ol>
        </nav>
        <h1>{headline}</h1>
        <p class="hero-lead">{beschreibung}</p>
      </div>
    </section>

    <section class="serie-section">
      <div class="container serie-layout">
        <div class="serie-content">
          <h2>Modelle der {name}</h2>
          <div class="product-grid">
{produkt_cards}          </div>
        </div>

        <aside class="sticky-sidebar">
          <div class="sidebar-box">
            <h3>Produktmerkmale</h3>
            <ul class="merkmale-list">
{merkmale_html}
            </ul>
          </div>
          <div class="sidebar-box cta-box">
            <h3>Persönliche Beratung</h3>
            <p>Sie möchten einen Grandhall Grill in Aktion erleben? Besuchen Sie unsere Ausstellung in Würzburg.</p>
            <a href="/ausstellung-beratung/" class="btn-outline">Zur Ausstellung</a>
            <a href="/kontakt/" class="btn-outline" style="margin-top:0.5rem;">Jetzt anfragen</a>
          </div>
        </aside>
      </div>
    </section>
  </main>

  <footer class="site-footer">
    <div class="container footer-inner">
      <div class="footer-col">
        <strong>Feuerhaus Kalina</strong>
        <p>Grillwelt Würzburg<br>Rottendorfer Str. 12<br>97074 Würzburg</p>
      </div>
      <div class="footer-col">
        <strong>Kontakt</strong>
        <p>Tel: <a href="tel:+499317607950">0931 760 79 50</a><br>
        <a href="mailto:info@feuerhaus-kalina.de">info@feuerhaus-kalina.de</a></p>
      </div>
      <div class="footer-col">
        <strong>Navigation</strong>
        <ul>
          <li><a href="/hersteller/grandhall/">Grandhall Übersicht</a></li>
          <li><a href="/hersteller/">Alle Hersteller</a></li>
          <li><a href="/ausstellung-beratung/">Ausstellung</a></li>
          <li><a href="/kontakt/">Kontakt</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <strong>Rechtliches</strong>
        <ul>
          <li><a href="/impressum/">Impressum</a></li>
          <li><a href="/datenschutz/">Datenschutz</a></li>
        </ul>
      </div>
    </div>
    <p class="footer-copy">© 2025 Feuerhaus Kalina GmbH &amp; Co. KG</p>
  </footer>

  <div id="cookie-banner" class="cookie-banner" role="dialog" aria-label="Cookie-Hinweis">
    <p>Diese Website verwendet Cookies für eine optimale Nutzererfahrung.
      <a href="/datenschutz/">Mehr erfahren</a></p>
    <div class="cookie-actions">
      <button id="cookie-accept" class="btn-cookie-accept">Akzeptieren</button>
      <button id="cookie-decline" class="btn-cookie-decline">Ablehnen</button>
    </div>
  </div>

  <script src="/js/main.js" defer></script>
</body>
</html>"""


def generate_overview_page():
    serien_cards = ""
    for familie in FAMILIEN:
        slug = familie["slug"]
        name = familie["name"]
        # Suche erstes verfügbares Bild in dieser Familie
        first_img = "/img/ui/placeholder.png"
        for produkt in familie["produkte"]:
            p_data = alle_produkt_daten.get(produkt["slug"], {})
            if p_data.get("imgs"):
                first_img = f"/img/grandhall/{p_data['imgs'][0]}"
                break

        serien_cards += f"""        <a href="/hersteller/grandhall/{slug}/" class="serie-card">
          <div class="serie-card-img">
            <img data-src="{first_img}" src="/img/ui/placeholder.png" alt="{name}" class="lazy" loading="lazy">
          </div>
          <div class="serie-card-body">
            <h3>{name}</h3>
            <span class="btn-link">Zur Serie →</span>
          </div>
        </a>
"""

    anzahl_produkte = sum(len(f["produkte"]) for f in FAMILIEN)

    return f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Grandhall Grills – Alle Serien | Feuerhaus Kalina Würzburg</title>
  <meta name="description" content="Grandhall Gasgrills, Einbaugrills & Holzkohlegrills bei Feuerhaus Kalina in Würzburg. Alle Serien von Xenon bis Elite – {anzahl_produkte} Modelle in der Ausstellung.">
  <link rel="canonical" href="https://grills.feuerhaus-kalina.de/hersteller/grandhall/">
  <link rel="icon" href="/img/ui/favicon.ico">
  <link rel="apple-touch-icon" href="/img/ui/apple-touch-icon.png">
  <link rel="stylesheet" href="/css/style.css">
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      {{"@type":"ListItem","position":1,"name":"Start","item":"https://grills.feuerhaus-kalina.de/"}},
      {{"@type":"ListItem","position":2,"name":"Hersteller","item":"https://grills.feuerhaus-kalina.de/hersteller/"}},
      {{"@type":"ListItem","position":3,"name":"Grandhall","item":"https://grills.feuerhaus-kalina.de/hersteller/grandhall/"}}
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
      <button class="nav-menu-toggle" aria-label="Menü öffnen" aria-expanded="false">
        <span></span><span></span><span></span>
      </button>
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
              <span itemprop="name">Grandhall</span>
              <meta itemprop="position" content="3">
            </li>
          </ol>
        </nav>
        <h1>Grandhall Grills – Alle Serien</h1>
        <p class="hero-lead">Grandhall steht seit Jahrzehnten für hochwertige Gasgrills, Einbaugrills und Outdoor-Küchen aus den Niederlanden. Bei Feuerhaus Kalina in Würzburg finden Sie ausgewählte Modelle aller Serien – von kompakten Gasgrills bis zu professionellen Einbaulösungen.</p>
      </div>
    </section>

    <section class="serien-uebersicht">
      <div class="container">
        <h2>Grandhall Serien im Überblick</h2>
        <div class="serien-grid">
{serien_cards}        </div>
      </div>
    </section>

    <section class="info-block">
      <div class="container info-cols">
        <div>
          <h2>Grandhall – Qualität aus den Niederlanden</h2>
          <p>Grandhall Barbecues ist ein renommierter niederländischer Hersteller von Premium-Gasgrills und Outdoor-Küchenkomponenten. Das Unternehmen verbindet europäisches Design mit robusten Materialien und langlebiger Verarbeitung.</p>
          <p>Von der kompakten Xenon-Serie über die vielseitige Premium-Linie bis hin zur exklusiven Elite-Serie bietet Grandhall für jeden Anspruch die passende Lösung – ob freistehend oder als Einbaugrill für die Outdoor-Küche.</p>
        </div>
        <div>
          <h2>Grandhall in Ihrer Ausstellung erleben</h2>
          <p>Im Feuerhaus Kalina in Würzburg können Sie ausgewählte Grandhall-Modelle live besichtigen und sich von unseren Grillexperten beraten lassen. Wir führen alle wichtigen Serien und helfen Ihnen, den perfekten Grill für Ihre Bedürfnisse zu finden.</p>
          <p><a href="/ausstellung-beratung/" class="btn-outline">Ausstellung &amp; Öffnungszeiten</a></p>
        </div>
      </div>
    </section>
  </main>

  <footer class="site-footer">
    <div class="container footer-inner">
      <div class="footer-col">
        <strong>Feuerhaus Kalina</strong>
        <p>Grillwelt Würzburg<br>Rottendorfer Str. 12<br>97074 Würzburg</p>
      </div>
      <div class="footer-col">
        <strong>Kontakt</strong>
        <p>Tel: <a href="tel:+499317607950">0931 760 79 50</a><br>
        <a href="mailto:info@feuerhaus-kalina.de">info@feuerhaus-kalina.de</a></p>
      </div>
      <div class="footer-col">
        <strong>Navigation</strong>
        <ul>
          <li><a href="/hersteller/">Alle Hersteller</a></li>
          <li><a href="/keramikgrills-kamado/">Keramikgrills</a></li>
          <li><a href="/ausstellung-beratung/">Ausstellung</a></li>
          <li><a href="/kontakt/">Kontakt</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <strong>Rechtliches</strong>
        <ul>
          <li><a href="/impressum/">Impressum</a></li>
          <li><a href="/datenschutz/">Datenschutz</a></li>
        </ul>
      </div>
    </div>
    <p class="footer-copy">© 2025 Feuerhaus Kalina GmbH &amp; Co. KG</p>
  </footer>

  <div id="cookie-banner" class="cookie-banner" role="dialog" aria-label="Cookie-Hinweis">
    <p>Diese Website verwendet Cookies für eine optimale Nutzererfahrung.
      <a href="/datenschutz/">Mehr erfahren</a></p>
    <div class="cookie-actions">
      <button id="cookie-accept" class="btn-cookie-accept">Akzeptieren</button>
      <button id="cookie-decline" class="btn-cookie-decline">Ablehnen</button>
    </div>
  </div>

  <script src="/js/main.js" defer></script>
</body>
</html>"""


# ─── HTML-Seiten schreiben ─────────────────────────────────────────────────────

print("Generiere HTML-Seiten...")

# Übersichtsseite
overview_dir = BASE_DIR / "hersteller" / "grandhall"
overview_dir.mkdir(parents=True, exist_ok=True)
(overview_dir / "index.html").write_text(generate_overview_page(), encoding="utf-8")
print("  ✓ hersteller/grandhall/index.html")

# Serien-Seiten
for familie in FAMILIEN:
    serie_dir = overview_dir / familie["slug"]
    serie_dir.mkdir(parents=True, exist_ok=True)
    (serie_dir / "index.html").write_text(generate_familie_page(familie), encoding="utf-8")
    print(f"  ✓ hersteller/grandhall/{familie['slug']}/index.html")

total_seiten = 1 + len(FAMILIEN)
total_produkte = sum(len(f["produkte"]) for f in FAMILIEN)

print()
print("=" * 60)
print("FERTIG")
print("=" * 60)
print(f"  Serien:            {len(FAMILIEN)}")
print(f"  Produkte gesamt:   {total_produkte}")
print(f"  Heruntergeladen:   {total_downloaded}")
print(f"  Bereits vorhanden: {total_skipped}")
print(f"  Fehler:            {total_errors}")
print(f"  HTML-Seiten:       {total_seiten}")
print("=" * 60)
