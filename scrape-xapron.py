# -*- coding: utf-8 -*-
"""
Xapron Scraper & HTML-Generator
Fetches product images from xapron.nl and generates pages for hersteller/xapron/
Also updates schuerzen/ and zubehoer/ category pages.
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
IMG_DIR = BASE_DIR / "img" / "xapron"
IMG_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
    "Referer": "https://xapron.nl/",
}

BASE_URL = "https://xapron.nl"

# ─── Produktkategorien ────────────────────────────────────────────────────────
KATEGORIEN = [
    {
        "slug": "herren",
        "name": "Herren Schürzen",
        "headline": "Xapron Herren Grillschürzen – Echtleder aus den Niederlanden",
        "beschreibung": "Xapron fertigt handgemachte Lederschürzen für Männer, die beim Grillen und Kochen auf Stil und Qualität bestehen. Alle Schürzen werden in Waalwijk (Niederlande) aus vollnarbigem Büffelleder hergestellt.",
        "merkmale": ["100% Vollnarbleder", "Handgefertigt in den Niederlanden", "Verstellbare Gurte mit Schnalle", "Wasserabweisend gewachst", "Personalisierbar mit Namen/Logo"],
        "produkte": [
            {
                "slug": "bovine-leren-schort",
                "name": "Bovine Lederschürze",
                "preis": "ab 89,95 €",
                "kurzbeschreibung": "Handgefertigte Schürze aus vollnarbigem italienischem Büffelleder mit weichem Relief. Verstellbare Gurte mit Bronzeschnalle. Erhältlich in M, L, XL.",
                "farben": "Schwarz, Braun, Cognac, Dunkelgrün, Marine, Rot, Safari, Taupe",
            },
            {
                "slug": "dallas-leren-schort",
                "name": "Dallas Lederschürze",
                "preis": "79,95 €",
                "kurzbeschreibung": "Die neue Dallas-Kollektion – handgefertigt aus europäischem Vollnarbleder. Nachhaltig produziert mit minimalem Lederabfall.",
                "farben": "Schwarz, Braun, Cognac, Grün, Marine, Rot, Safari, Taupe",
            },
            {
                "slug": "new-york",
                "name": "New York Schürze",
                "preis": "ab 119,95 €",
                "kurzbeschreibung": "Vollnarbleder mit glatt gespriztem Finish – das wertvollste Stück der Haut. Weiches Büffelleder, handgefertigt in Waalwijk.",
                "farben": "Cognac, Braun, Schwarz",
            },
            {
                "slug": "schort-new-york-schouderbanden",
                "name": "New York mit Schulterbändern",
                "preis": "ab 139,95 €",
                "kurzbeschreibung": "Die beliebte New York Schürze mit zusätzlichen Schulterbändern für optimalen Halt und noch mehr Komfort beim Grillen.",
                "farben": "Cognac, Braun, Schwarz",
            },
            {
                "slug": "utah",
                "name": "Utah Schürze",
                "preis": "ab 129,95 €",
                "kurzbeschreibung": "Aus extra geöltem Vollnarbenbüffelleder. Die natürliche Oberflächenstruktur bleibt erhalten – robust, geschmeidig und bequem.",
                "farben": "Schwarz, Schokolade, Rost",
            },
            {
                "slug": "atlanta",
                "name": "Atlanta Schürze",
                "preis": "ab 119,95 €",
                "kurzbeschreibung": "Atlanta – geschmeidiges Leder im Vintage-Look. Natürlich gegerbte Gurte, einfach zu reinigen mit einem feuchten Tuch.",
                "farben": "Kastanie, Kamel, Ranch, Taupe",
            },
            {
                "slug": "schort-atlanta-schouderbanden",
                "name": "Atlanta mit Schulterbändern",
                "preis": "ab 149,95 €",
                "kurzbeschreibung": "Die Atlanta Schürze mit Schulterbändern – für maximalen Halt beim langen Grillabend.",
                "farben": "Kastanie, Kamel, Ranch, Taupe",
            },
            {
                "slug": "schort-bovine-schouderbanden",
                "name": "Bovine mit Schulterbändern",
                "preis": "ab 109,95 €",
                "kurzbeschreibung": "Die Bovine Lederschürze mit zusätzlichen Schulterbändern. Optimale Gewichtsverteilung für lange Grillsessions.",
                "farben": "Schwarz, Braun, Cognac, Marine, Safari, Taupe",
            },
            {
                "slug": "miami-leren-schort",
                "name": "Miami Lederschürze",
                "preis": "ab 49,95 €",
                "kurzbeschreibung": "Kompakte Lederschürze im Miami-Stil – ideal für den schnellen Grillabend. Gutes Preis-Leistungs-Verhältnis.",
                "farben": "Grau, Braun",
            },
        ],
    },
    {
        "slug": "damen",
        "name": "Damen Schürzen",
        "headline": "Xapron Damen Grillschürzen – Leder für Frauen",
        "beschreibung": "Die Xapron Damenschürze kombiniert Stärke, Mode und Funktionalität. Handgefertigt aus 100% weichem Rindsleder – mit schmalem Leder-Nackenband und Bindegurt.",
        "merkmale": ["100% weiches Rindsleder", "Handgefertigt in den Niederlanden", "Schlankes Leder-Nackenband", "Wasserabweisend gewachst", "Personalisierbar"],
        "produkte": [
            {
                "slug": "leren-dames-schort",
                "name": "Leder Damenschürze",
                "preis": "99,95 €",
                "kurzbeschreibung": "Handgefertigt aus einem Stück weichem Rindsleder (keine Nähte). 74 cm hoch × 60 cm breit. Erhältlich in Braun, Rost, Schwarz und Blau.",
                "farben": "Braun, Rost, Schwarz, Blau",
            },
        ],
    },
    {
        "slug": "kinder",
        "name": "Kinder Schürzen",
        "headline": "Xapron Kinder Grillschürzen – Kleine Grillmeister",
        "beschreibung": "Xapron fertigt auch Lederschürzen für die Kleinsten – robust, wasserabweisend und mit verstellbarem Baumwollband. Für Kinder von 3 bis 8 Jahren.",
        "merkmale": ["Für Kinder von 3–8 Jahren", "50 cm × 40 cm", "Verstellbares Baumwollband", "Wasserabweisend gewachst", "Personalisierbar (max. 8 Zeichen)"],
        "produkte": [
            {
                "slug": "leren-kinder-short-bovine",
                "name": "Kinder Lederschürze Bovine",
                "preis": "64,95 €",
                "kurzbeschreibung": "Handgefertigte Lederschürze für Kinder von 3–8 Jahren. 50 cm × 40 cm, mit wasserabweisender Wachsbeschichtung. Erhältlich in 4 Farben.",
                "farben": "Braun, Schwarz, Rost, Blau",
            },
        ],
    },
    {
        "slug": "vegan-denim",
        "name": "Vegan & Denim",
        "headline": "Xapron Vegan & Denim – Nachhaltige Alternativen",
        "beschreibung": "Xapron bietet neben klassischem Leder auch vegane und nachhaltige Alternativen: Die Amsterdam Appleskin-Schürze aus veganem Apfelleder und die Arizona Denim-Schürze aus recycelter Baumwolle.",
        "merkmale": ["100% vegan (Appleskin)", "Recycelte Baumwolle (Denim)", "Abnehmbare Appleleder-Gurte", "Nachhaltig produziert", "Personalisierbar"],
        "produkte": [
            {
                "slug": "schort-amsterdam-vegan",
                "name": "Amsterdam Vegan Appleskin",
                "preis": "99,95 €",
                "kurzbeschreibung": "Vegane Schürze aus Appleskin (Apfelleder) – nachhaltig und tierfrei. Die ideale Wahl für bewusste Grillmeister.",
                "farben": "Braun, Schwarz",
            },
            {
                "slug": "arizona-denim-schort",
                "name": "Arizona Denim Schürze",
                "preis": "49,95 €",
                "kurzbeschreibung": "Handgefertigte Jeans-Schürze aus recycelter Baumwolle mit abnehmbaren Appleleder-Gurten. Vegan erhältlich.",
                "farben": "Hell, Dunkel",
            },
        ],
    },
    {
        "slug": "zubehoer",
        "name": "Schürzen-Zubehör",
        "headline": "Xapron Zubehör – Ergänzungen für Ihre Lederschürze",
        "beschreibung": "Xapron bietet hochwertiges Leder-Zubehör für Ihre Schürze: Flaschenhalter, Messerhalter, Taschen und mehr – alles handgefertigt in den Niederlanden.",
        "merkmale": ["Handgefertigtes Leder-Zubehör", "Kompatibel mit allen Xapron Schürzen", "Hochwertige Verarbeitung", "Einfache Befestigung", "Personalisierbar"],
        "produkte": [
            {
                "slug": "bottle-holster",
                "name": "Bottle Holster",
                "preis": "34,95 €",
                "kurzbeschreibung": "Lederner Flaschenhalter für die Schürze – hält Ihre Lieblingsgetränke griffbereit beim Grillen.",
                "farben": "Braun, Schwarz",
            },
            {
                "slug": "knife-holder-2-knives",
                "name": "Messerhalter für 2 Messer",
                "preis": "32,50 €",
                "kurzbeschreibung": "Leder-Messerhalter für 2 Messer – direkt an der Schürze befestigbar. Hält Ihre Grillmesser sicher und griffbereit.",
                "farben": "Braun",
            },
            {
                "slug": "waiter-holder",
                "name": "Waiter Holder",
                "preis": "39,95 €",
                "kurzbeschreibung": "Praktischer Leder-Halter für Kellnerbedarf oder Grillbesteck – passt an alle Xapron Schürzen.",
                "farben": "Braun, Schwarz",
            },
            {
                "slug": "pocket-13x19-cm",
                "name": "Ledertasche 13×19 cm",
                "preis": "10,00 €",
                "kurzbeschreibung": "Kleine Ledertasche als Zusatzausstattung für Ihre Schürze. Ideal für Gewürze, Feuerzeug oder kleine Utensilien.",
                "farben": "Braun",
            },
            {
                "slug": "pocket-18x22-cm",
                "name": "Ledertasche 18×22 cm",
                "preis": "11,00 €",
                "kurzbeschreibung": "Größere Ledertasche als Zusatz für Ihre Schürze – für mehr Stauraum beim Grillen.",
                "farben": "Braun",
            },
            {
                "slug": "water-holder",
                "name": "Water Holder",
                "preis": "32,50 €",
                "kurzbeschreibung": "Leder-Wasserflaschenhalter für die Schürze – hält Ihre Wasserflasche sicher an der Hüfte.",
                "farben": "Braun",
            },
        ],
    },
]

# ─── Hilfsfunktionen ──────────────────────────────────────────────────────────

def fetch_html(url):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        return urllib.request.urlopen(req, timeout=20).read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"    FETCH-FEHLER {url}: {e}")
        return ""


SKIP_PATTERNS = ["logo", "favicon", "icon", "banner", "size-chart", "size_chart",
                 "leren-ovenwanten", "Brown.png", "cropped-"]


def extract_product_images(html):
    raw = re.findall(
        r'https://xapron\.nl/wp-content/uploads/[^\s"\'<>]+\.(?:png|jpg|jpeg|webp)',
        html, re.IGNORECASE
    )
    seen = set()
    result = []
    for url in raw:
        clean = re.sub(r'-\d+x\d+(?=\.(png|jpg|jpeg|webp))', '', url)
        if clean not in seen and not any(p.lower() in clean.lower() for p in SKIP_PATTERNS):
            seen.add(clean)
            result.append(clean)
    return result


def img_filename(kat_slug, prod_slug, img_url, index):
    ext = Path(img_url.split("?")[0]).suffix or ".jpg"
    return f"xapron-{kat_slug}-{prod_slug}-{index:02d}{ext}"


def download_image(url, dest_path):
    if dest_path.exists():
        data = dest_path.read_bytes()
        if data[:8] == b'\x89PNG\r\n\x1a\n' or data[:3] == b'\xff\xd8\xff':
            return False, dest_path.stat().st_size
        else:
            dest_path.unlink()  # Delete invalid file
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        data = urllib.request.urlopen(req, timeout=20).read()
        if data[:8] == b'\x89PNG\r\n\x1a\n' or data[:3] == b'\xff\xd8\xff':
            dest_path.write_bytes(data)
            return True, len(data)
        else:
            print(f"    UNGÜLTIG (kein Bild): {url}")
            return False, 0
    except Exception as e:
        print(f"    FEHLER: {e}")
        return False, 0


# ─── Daten sammeln ────────────────────────────────────────────────────────────

print("Xapron Scraper & HTML-Generator")
print("=" * 60)
print(f"Bilder → {IMG_DIR}")
print()

alle_daten = {}  # kat_slug/prod_slug -> {"imgs": [], "name": str}
total_dl = 0
total_skip = 0
total_err = 0

for kat in KATEGORIEN:
    kat_slug = kat["slug"]
    print(f"── {kat['name']} ──")
    for prod in kat["produkte"]:
        prod_slug = prod["slug"]
        url = f"{BASE_URL}/product/{prod_slug}/"
        print(f"  Fetche: {prod_slug}")
        html = fetch_html(url)
        time.sleep(0.4)

        imgs_from_page = extract_product_images(html) if html else []
        local_imgs = []

        for i, img_url in enumerate(imgs_from_page[:4]):
            fname = img_filename(kat_slug, prod_slug, img_url, i + 1)
            dest = IMG_DIR / fname
            downloaded, size = download_image(img_url, dest)
            if size > 0:
                local_imgs.append(fname)
                if downloaded:
                    print(f"    ↓ {fname} → {size // 1024} KB")
                    total_dl += 1
                else:
                    print(f"    ✓ {fname}")
                    total_skip += 1
            else:
                total_err += 1

        # Fallback: already downloaded files
        if not local_imgs:
            pattern = re.compile(rf"xapron-{re.escape(kat_slug)}-{re.escape(prod_slug)}-\d+\.")
            local_imgs = sorted(f.name for f in IMG_DIR.glob(f"xapron-{kat_slug}-{prod_slug}-*")
                                if pattern.match(f.name))

        if not local_imgs:
            print(f"    ⚠ Keine Bilder für {prod_slug}")

        key = f"{kat_slug}/{prod_slug}"
        alle_daten[key] = {
            "imgs": local_imgs,
            "name": prod["name"],
            "preis": prod.get("preis", ""),
            "kurzbeschreibung": prod.get("kurzbeschreibung", ""),
            "farben": prod.get("farben", ""),
        }

print()
print(f"Bilder: {total_dl} heruntergeladen, {total_skip} vorhanden, {total_err} Fehler")
print()


# ─── HTML-Templates ───────────────────────────────────────────────────────────

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
        <p>Grillwelt Würzburg<br>Rottendorfer Str. 12<br>97074 Würzburg</p>
      </div>
      <div class="footer-col">
        <strong>Kontakt</strong>
        <p>Tel: <a href="tel:+499317607950">0931 760 79 50</a><br>
        <a href="mailto:info@feuerhaus-kalina.de">info@feuerhaus-kalina.de</a></p>
      </div>
      <div class="footer-col">
        <strong>Schürzen</strong>
        <ul>
          <li><a href="/hersteller/xapron/herren/">Herren Schürzen</a></li>
          <li><a href="/hersteller/xapron/damen/">Damen Schürzen</a></li>
          <li><a href="/hersteller/xapron/kinder/">Kinder Schürzen</a></li>
          <li><a href="/hersteller/xapron/vegan-denim/">Vegan &amp; Denim</a></li>
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

  <script src="/js/main.js" defer></script>"""


def prod_card(prod_data, kat_slug):
    name = prod_data["name"]
    preis = prod_data["preis"]
    kurz = prod_data["kurzbeschreibung"]
    farben = prod_data["farben"]
    imgs = prod_data["imgs"]
    anfragen_url = f"/kontakt/?produkt={urllib.parse.quote(name)}"

    if imgs:
        main_img = f"/img/xapron/{imgs[0]}"
        img_tag = f'<img data-src="{main_img}" src="/img/ui/placeholder.png" alt="{name}" class="lazy" loading="lazy">'
    else:
        img_tag = f'<img src="/img/ui/placeholder.png" alt="{name}">'

    preis_html = f'<span class="product-price">{preis}</span>' if preis else ""
    farben_html = f'<p class="product-farben"><small>Farben: {farben}</small></p>' if farben else ""

    return f"""          <div class="product-card">
            <div class="product-img-wrap">
              {img_tag}
            </div>
            <div class="product-info">
              <h3>{name}</h3>
              {preis_html}
              <p class="product-desc">{kurz}</p>
              {farben_html}
              <a href="{anfragen_url}" class="product-anfragen">Anfragen</a>
            </div>
          </div>"""


def generate_kategorie_page(kat):
    slug = kat["slug"]
    name = kat["name"]
    headline = kat["headline"]
    beschreibung = kat["beschreibung"]
    merkmale_html = "\n".join(
        f'            <li><span class="check">✓</span> {m}</li>'
        for m in kat["merkmale"]
    )

    produkt_cards = ""
    for prod in kat["produkte"]:
        key = f"{slug}/{prod['slug']}"
        pdata = alle_daten.get(key, {"imgs": [], "name": prod["name"],
                                     "preis": prod.get("preis", ""),
                                     "kurzbeschreibung": prod.get("kurzbeschreibung", ""),
                                     "farben": prod.get("farben", "")})
        produkt_cards += prod_card(pdata, slug) + "\n"

    bc4 = f'{{"@type":"ListItem","position":4,"name":"{name}","item":"https://grills.feuerhaus-kalina.de/hersteller/xapron/{slug}/"}}'

    return f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{headline} | Feuerhaus Kalina Würzburg</title>
  <meta name="description" content="{beschreibung[:155]}">
  <link rel="canonical" href="https://grills.feuerhaus-kalina.de/hersteller/xapron/{slug}/">
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
      {{"@type":"ListItem","position":3,"name":"Xapron","item":"https://grills.feuerhaus-kalina.de/hersteller/xapron/"}},
      {bc4}
    ]
  }}
  </script>
</head>
<body>
{NAV}

  <main>
    <section class="page-hero">
      <div class="container">
        <nav class="breadcrumb" aria-label="Breadcrumb">
          <ol>
            <li><a href="/">Start</a></li>
            <li><a href="/hersteller/">Hersteller</a></li>
            <li><a href="/hersteller/xapron/">Xapron</a></li>
            <li>{name}</li>
          </ol>
        </nav>
        <h1>{headline}</h1>
        <p class="hero-lead">{beschreibung}</p>
      </div>
    </section>

    <section class="serie-section">
      <div class="container serie-layout">
        <div class="serie-content">
          <h2>{name} – Alle Modelle</h2>
          <div class="product-grid product-grid--wide">
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
            <p>Xapron Schürzen in Aktion erleben – in unserer Ausstellung in Würzburg.</p>
            <a href="/ausstellung-beratung/" class="btn-outline">Zur Ausstellung</a>
            <a href="/kontakt/" class="btn-outline" style="margin-top:.5rem">Jetzt anfragen</a>
          </div>
          <div class="sidebar-box">
            <h3>Xapron Kategorien</h3>
            <ul class="merkmale-list">
              <li><a href="/hersteller/xapron/herren/">Herren Schürzen</a></li>
              <li><a href="/hersteller/xapron/damen/">Damen Schürzen</a></li>
              <li><a href="/hersteller/xapron/kinder/">Kinder Schürzen</a></li>
              <li><a href="/hersteller/xapron/vegan-denim/">Vegan &amp; Denim</a></li>
              <li><a href="/hersteller/xapron/zubehoer/">Zubehör</a></li>
            </ul>
          </div>
        </aside>
      </div>
    </section>
  </main>

{FOOTER}
</body>
</html>"""


def generate_overview_page():
    serien_cards = ""
    for kat in KATEGORIEN:
        slug = kat["slug"]
        name = kat["name"]
        # First image from category
        first_img = "/img/ui/placeholder.png"
        for prod in kat["produkte"]:
            key = f"{slug}/{prod['slug']}"
            pdata = alle_daten.get(key, {})
            if pdata.get("imgs"):
                first_img = f"/img/xapron/{pdata['imgs'][0]}"
                break

        serien_cards += f"""        <a href="/hersteller/xapron/{slug}/" class="serie-card">
          <div class="serie-card-img">
            <img data-src="{first_img}" src="/img/ui/placeholder.png" alt="{name}" class="lazy" loading="lazy">
          </div>
          <div class="serie-card-body">
            <h3>{name}</h3>
            <span class="btn-link">Zur Kategorie →</span>
          </div>
        </a>
"""

    return f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Xapron Grillschürzen – Handgemachtes Leder | Feuerhaus Kalina Würzburg</title>
  <meta name="description" content="Xapron Lederschürzen für Herren, Damen & Kinder – handgefertigt in den Niederlanden. Jetzt bei Feuerhaus Kalina in Würzburg ansehen und anfragen.">
  <link rel="canonical" href="https://grills.feuerhaus-kalina.de/hersteller/xapron/">
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
      {{"@type":"ListItem","position":3,"name":"Xapron","item":"https://grills.feuerhaus-kalina.de/hersteller/xapron/"}}
    ]
  }}
  </script>
</head>
<body>
{NAV}

  <main>
    <section class="page-hero">
      <div class="container">
        <nav class="breadcrumb" aria-label="Breadcrumb">
          <ol>
            <li><a href="/">Start</a></li>
            <li><a href="/hersteller/">Hersteller</a></li>
            <li>Xapron</li>
          </ol>
        </nav>
        <h1>Xapron – Handgemachte Grillschürzen aus Leder</h1>
        <p class="hero-lead">Xapron steht seit Jahren für hochwertige Lederschürzen aus den Niederlanden. Alle Modelle werden in Waalwijk von Hand gefertigt – aus vollnarbigem Büffelleder, für Herren, Damen und Kinder.</p>
      </div>
    </section>

    <section class="serien-uebersicht">
      <div class="container">
        <h2>Xapron Kategorien</h2>
        <div class="serien-grid">
{serien_cards}        </div>
      </div>
    </section>

    <section class="info-block">
      <div class="container info-cols">
        <div>
          <h2>Handgefertigt in den Niederlanden</h2>
          <p>Xapron produziert alle Schürzen in Waalwijk, Niederlande – einem traditionsreichen Zentrum der Lederwirtschaft. Jede Schürze wird aus vollnarbigem Büffelleder zugeschnitten und handgenäht. Das Ergebnis: unvergleichliche Qualität, die jahrelang hält.</p>
          <p>Von der klassischen Bovine-Linie über die trendy Dallas-Kollektion bis hin zur veganen Amsterdam-Schürze – Xapron hat für jeden Grillmeister das Passende.</p>
        </div>
        <div>
          <h2>Xapron bei Feuerhaus Kalina</h2>
          <p>In unserem Grillstore in Würzburg können Sie ausgewählte Xapron-Modelle live anfassen und anprobieren. Unsere Experten beraten Sie gerne bei der Auswahl der richtigen Schürze – ob als Geschenk oder für sich selbst.</p>
          <p><a href="/ausstellung-beratung/" class="btn-outline">Ausstellung &amp; Öffnungszeiten</a></p>
        </div>
      </div>
    </section>
  </main>

{FOOTER}
</body>
</html>"""


def generate_schuerzen_category():
    """Aktualisiert /schuerzen/index.html mit Xapron-Inhalt"""
    # Sammel alle Herren/Damen/Kinder Produkte für Schürzen-Übersicht
    cards = ""
    for kat_slug in ["herren", "damen", "kinder"]:
        kat = next(k for k in KATEGORIEN if k["slug"] == kat_slug)
        for prod in kat["produkte"]:
            key = f"{kat_slug}/{prod['slug']}"
            pdata = alle_daten.get(key, {"imgs": [], "name": prod["name"],
                                         "preis": prod.get("preis", ""),
                                         "kurzbeschreibung": prod.get("kurzbeschreibung", ""),
                                         "farben": prod.get("farben", "")})
            cards += prod_card(pdata, kat_slug) + "\n"

    return f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Grillschürzen – Leder von Xapron | Feuerhaus Kalina Würzburg</title>
  <meta name="description" content="Premium Grillschürzen aus echtem Büffelleder von Xapron – für Herren, Damen und Kinder. Handgefertigt in den Niederlanden. Jetzt in Würzburg ansehen.">
  <link rel="canonical" href="https://grills.feuerhaus-kalina.de/schuerzen/">
  <link rel="icon" href="/img/ui/favicon.ico">
  <link rel="apple-touch-icon" href="/img/ui/apple-touch-icon.png">
  <link rel="stylesheet" href="/css/style.css">
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      {{"@type":"ListItem","position":1,"name":"Start","item":"https://grills.feuerhaus-kalina.de/"}},
      {{"@type":"ListItem","position":2,"name":"Grillschürzen","item":"https://grills.feuerhaus-kalina.de/schuerzen/"}}
    ]
  }}
  </script>
</head>
<body>
{NAV}

  <main>
    <section class="page-hero">
      <div class="container">
        <nav class="breadcrumb" aria-label="Breadcrumb">
          <ol>
            <li><a href="/">Start</a></li>
            <li>Grillschürzen</li>
          </ol>
        </nav>
        <h1>Grillschürzen – Premium Leder von Xapron</h1>
        <p class="hero-lead">Hochwertige Grillschürzen aus echtem Büffelleder – handgefertigt in den Niederlanden von Xapron. Für Herren, Damen und Kinder. Wasserabweisend, langlebig und personalisierbar.</p>
      </div>
    </section>

    <section class="serie-section">
      <div class="container serie-layout">
        <div class="serie-content">
          <h2>Alle Grillschürzen</h2>
          <div class="xapron-kat-links" style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:28px;">
            <a href="/hersteller/xapron/herren/" class="btn-outline" style="font-size:13px;padding:8px 16px;">Herren</a>
            <a href="/hersteller/xapron/damen/" class="btn-outline" style="font-size:13px;padding:8px 16px;">Damen</a>
            <a href="/hersteller/xapron/kinder/" class="btn-outline" style="font-size:13px;padding:8px 16px;">Kinder</a>
            <a href="/hersteller/xapron/vegan-denim/" class="btn-outline" style="font-size:13px;padding:8px 16px;">Vegan &amp; Denim</a>
          </div>
          <div class="product-grid product-grid--wide">
{cards}          </div>
        </div>

        <aside class="sticky-sidebar">
          <div class="sidebar-box">
            <h3>Warum Xapron?</h3>
            <ul class="merkmale-list">
              <li><span class="check">✓</span> Handgefertigt in den Niederlanden</li>
              <li><span class="check">✓</span> 100% Vollnarbleder</li>
              <li><span class="check">✓</span> Wasserabweisend &amp; langlebig</li>
              <li><span class="check">✓</span> Personalisierbar mit Namen</li>
              <li><span class="check">✓</span> Für Herren, Damen &amp; Kinder</li>
              <li><span class="check">✓</span> Vegane Alternativen verfügbar</li>
            </ul>
          </div>
          <div class="sidebar-box cta-box">
            <h3>Beratung &amp; Anprobieren</h3>
            <p>Schürzen anfassen und anprobieren – kommen Sie in unsere Ausstellung in Würzburg.</p>
            <a href="/ausstellung-beratung/" class="btn-outline">Ausstellung</a>
            <a href="/kontakt/" class="btn-outline" style="margin-top:.5rem">Kontakt</a>
          </div>
        </aside>
      </div>
    </section>
  </main>

{FOOTER}
</body>
</html>"""


# ─── HTML-Seiten schreiben ─────────────────────────────────────────────────────

print("Generiere HTML-Seiten...")

# Übersichtsseite Xapron
xapron_dir = BASE_DIR / "hersteller" / "xapron"
xapron_dir.mkdir(parents=True, exist_ok=True)
(xapron_dir / "index.html").write_text(generate_overview_page(), encoding="utf-8")
print("  ✓ hersteller/xapron/index.html")

# Kategorieseiten
for kat in KATEGORIEN:
    kat_dir = xapron_dir / kat["slug"]
    kat_dir.mkdir(parents=True, exist_ok=True)
    (kat_dir / "index.html").write_text(generate_kategorie_page(kat), encoding="utf-8")
    print(f"  ✓ hersteller/xapron/{kat['slug']}/index.html")

# Schürzen-Kategorie aktualisieren
schuerzen_dir = BASE_DIR / "schuerzen"
schuerzen_dir.mkdir(parents=True, exist_ok=True)
(schuerzen_dir / "index.html").write_text(generate_schuerzen_category(), encoding="utf-8")
print("  ✓ schuerzen/index.html")

print()
total_seiten = 1 + len(KATEGORIEN) + 1
total_produkte = sum(len(k["produkte"]) for k in KATEGORIEN)
print("=" * 60)
print("FERTIG")
print("=" * 60)
print(f"  Kategorien:        {len(KATEGORIEN)}")
print(f"  Produkte gesamt:   {total_produkte}")
print(f"  Heruntergeladen:   {total_dl}")
print(f"  Bereits vorhanden: {total_skip}")
print(f"  Fehler:            {total_err}")
print(f"  HTML-Seiten:       {total_seiten}")
print("=" * 60)
