# -*- coding: utf-8 -*-
import urllib.request
import urllib.parse
import re
import sys
import io
import json
import time
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).parent
IMG_DIR = BASE_DIR / "img" / "kamado-joe"
IMG_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# Modell-Familien: jede Familie bekommt eine Unterseite
FAMILIEN = [
    {
        "slug": "joe-jr",
        "name": "Joe Jr.",
        "headline": "Joe Jr.™ – Der tragbare Kamado",
        "beschreibung": "Der Joe Jr. ist Kamado Joes kompaktester Holzkohlegrill – mit 34 cm Grillfläche perfekt für Camping, Balkon oder spontane Grillabende. Inklusive gusseisernem Ständer.",
        "merkmale": ["Ø 34 cm Grillfläche", "Tragbar & leicht", "Keramik-Isolierung", "Air Lift Scharnier", "Firestarter & Grillrost inklusive"],
        "produkte_handles": ["joe-jr-with-cast-iron-stand", "joe-jr-grill-cart-cover-bundle"],
    },
    {
        "slug": "classic-joe-i",
        "name": "Classic Joe™ Serie I",
        "headline": "Classic Joe™ Serie I – Der Klassiker",
        "beschreibung": "Der Classic Joe I ist die ideale Einführung in die Welt des Kamado-Grillens. Mit innovativen Funktionen und 46 cm Grillfläche ist er für alle geeignet, die das Grillen mit Holzkohle lieben.",
        "merkmale": ["Ø 46 cm Grillfläche", "Divide & Conquer System", "Kontrollventile", "2-teiliger Feuerring", "Wagen mit 2 Rädern"],
        "produkte_handles": ["classic-joe-i"],
    },
    {
        "slug": "classic-joe-ii",
        "name": "Classic Joe™ Serie II",
        "headline": "Classic Joe™ Serie II – Mehr Kontrolle, mehr Genuss",
        "beschreibung": "Der Classic Joe II hebt das Grillerlebnis auf ein neues Level. Dank Air Lift Scharnier lässt sich der Deckel mühelos mit einer Hand öffnen – auch bei hohen Temperaturen.",
        "merkmale": ["Ø 46 cm Grillfläche", "Air Lift Scharnier", "Divide & Conquer System", "Slow Roller optional", "Auch freistehend erhältlich"],
        "produkte_handles": ["classic-joe-ii", "classic-joe-stand-alone-ii-ceramic-kamado-grill"],
    },
    {
        "slug": "classic-joe-iii",
        "name": "Classic Joe™ Serie III",
        "headline": "Classic Joe™ Serie III – Das Nonplusultra im 46 cm Format",
        "beschreibung": "Der Classic Joe III vereint alle Innovationen in einem Grill: SloRoller Hyperbolic Insert, Kontrol Board und Air Lift Scharnier für das ultimative Kocherlebnis im Freien.",
        "merkmale": ["Ø 46 cm Grillfläche", "SloRoller Hyperbolic Insert", "Air Lift Scharnier", "Kontrol Board 3.0", "Auch freistehend erhältlich"],
        "produkte_handles": ["classic-joe-iii", "classic-joe-iii-without-cart"],
    },
    {
        "slug": "big-joe-i",
        "name": "Big Joe™ Serie I",
        "headline": "Big Joe™ Serie I – Maximale Grillfläche",
        "beschreibung": "Der Big Joe I bietet eine Grillfläche von 61 cm – ideal für große Runden und Events. Mit innovativen Funktionen für ein unvergessliches kulinarisches Erlebnis.",
        "merkmale": ["Ø 61 cm Grillfläche", "Divide & Conquer System", "Kontrollventile", "2-teiliger Feuerring", "Solide Stahlbeinstruktur"],
        "produkte_handles": ["big-joe-i"],
    },
    {
        "slug": "big-joe-ii",
        "name": "Big Joe™ Serie II",
        "headline": "Big Joe™ Serie II – Großes Grillen, große Freiheit",
        "beschreibung": "Mit 61 cm Grillfläche und Air Lift Scharnier ist der Big Joe II für alle, die groß grillen wollen. Genug Platz für ein komplettes Festmahl.",
        "merkmale": ["Ø 61 cm Grillfläche", "Air Lift Scharnier", "Divide & Conquer System", "2-stufiges Kochsystem", "Auch freistehend erhältlich"],
        "produkte_handles": ["big-joe-ii", "big-joe-ii-stand-alone"],
    },
    {
        "slug": "big-joe-iii",
        "name": "Big Joe™ Serie III",
        "headline": "Big Joe™ Serie III – Der innovativste Kamado aller Zeiten",
        "beschreibung": "Unser leistungsstärkster Seriengrill: Der Big Joe III verbindet 61 cm Grillfläche mit dem SloRoller, Kontrol Board und Air Lift Scharnier für ein unvergleichliches Grillerlebnis.",
        "merkmale": ["Ø 61 cm Grillfläche", "SloRoller Hyperbolic Insert", "Air Lift Scharnier", "Kontrol Board 3.0", "Auch freistehend erhältlich"],
        "produkte_handles": ["big-joe-iii", "big-joe-standalone-grill-series-iii"],
    },
    {
        "slug": "konnected-joe",
        "name": "Konnected Joe™",
        "headline": "Konnected Joe™ – WLAN-gesteuertes Grillen",
        "beschreibung": "Der Konnected Joe verbindet traditionelles Kamado-Grillen mit digitaler Steuerung. Per App Temperatur überwachen, Lüftung regeln und immer perfekte Ergebnisse erzielen.",
        "merkmale": ["WLAN-Steuerung per App", "Automatische Temperaturregelung", "SloRoller inklusive", "Kontrol Board Digital", "Erhältlich in Classic & Big Joe"],
        "produkte_handles": ["classic-joe-konnected-joe", "big-joe-konnected-joe"],
    },
]


def fetch_json(url):
    req = urllib.request.Request(url, headers=HEADERS)
    data = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", errors="replace")
    return json.loads(data)


def download_image(url, dest_path):
    if dest_path.exists():
        return False, dest_path.stat().st_size
    try:
        # Entferne Query-String für saubere URL
        clean_url = url.split("?")[0]
        req = urllib.request.Request(clean_url, headers=HEADERS)
        data = urllib.request.urlopen(req, timeout=20).read()
        dest_path.write_bytes(data)
        return True, len(data)
    except Exception as e:
        print(f"    FEHLER: {e}")
        return False, 0


def local_img_name(handle, img_url, index):
    ext = Path(img_url.split("?")[0]).suffix or ".jpg"
    return f"kj-{handle}-{index:02d}{ext}"


def strip_html(text):
    return re.sub(r"<[^>]+>", "", text).strip()


def generate_modell_html(produkt, imgs_local):
    title = produkt["title"]
    desc = strip_html(produkt.get("body_html", ""))[:320]
    handle = produkt["handle"]

    thumbs_html = ""
    for i, local in enumerate(imgs_local[:5]):
        active = " active" if i == 0 else ""
        thumbs_html += f"""
              <div class="modell-thumb{active}">
                <img data-src="/img/kamado-joe/{local}" src="/img/ui/placeholder.png" alt="{title} Bild {i+1}" class="lazy" loading="lazy">
              </div>"""

    anfragen_url = f"/kontakt/?produkt={urllib.parse.quote(title)}"
    main_img = f"/img/kamado-joe/{imgs_local[0]}" if imgs_local else "/img/ui/placeholder.png"

    return f"""
          <div class="modell-card">
            <div class="modell-img-wrap">
              <img data-src="{main_img}" src="/img/ui/placeholder.png" alt="{title}" class="lazy" loading="lazy" data-lightbox-src="{main_img}">
            </div>
            <div class="modell-gallery-thumbs">{thumbs_html}
            </div>
            <div class="modell-body">
              <h3>{title}</h3>
              <p>{desc}…</p>
              <a href="{anfragen_url}" class="modell-anfragen">Anfragen</a>
            </div>
          </div>"""


def generate_familie_page(familie, produkte_data, alle_imgs):
    merkmale_html = "\n".join(
        f'            <li><span class="check">✓</span> {m}</li>'
        for m in familie["merkmale"]
    )
    slug = familie["slug"]
    name = familie["name"]
    headline = familie["headline"]
    beschreibung = familie["beschreibung"]

    modell_cards = ""
    for p in produkte_data:
        imgs_local = alle_imgs.get(p["handle"], [])
        modell_cards += generate_modell_html(p, imgs_local)

    breadcrumb_pos4 = f'{{"@type":"ListItem","position":4,"name":"{name}","item":"https://grills.feuerhaus-kalina.de/hersteller/kamado-joe/{slug}/"}}'

    return f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{headline} | Feuerhaus Kalina Würzburg</title>
  <meta name="description" content="{beschreibung[:155]}">
  <link rel="canonical" href="https://grills.feuerhaus-kalina.de/hersteller/kamado-joe/{slug}/">
  <link rel="icon" href="/img/ui/favicon.ico">
  <link rel="stylesheet" href="/css/style.css">
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      {{"@type":"ListItem","position":1,"name":"Start","item":"https://grills.feuerhaus-kalina.de/"}},
      {{"@type":"ListItem","position":2,"name":"Hersteller","item":"https://grills.feuerhaus-kalina.de/hersteller/"}},
      {{"@type":"ListItem","position":3,"name":"Kamado Joe","item":"https://grills.feuerhaus-kalina.de/hersteller/kamado-joe/"}},
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
              <a itemprop="item" href="/hersteller/kamado-joe/"><span itemprop="name">Kamado Joe</span></a>
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

    <section class="container">
      <div class="serie-layout" style="padding:64px 0">
        <div class="modell-grid" style="padding:0">
{modell_cards}
        </div>

        <aside class="sticky-sidebar">
          <div class="sidebar-box">
            <h3>Merkmale</h3>
            <ul class="merkmale-list">
{merkmale_html}
            </ul>
          </div>
          <div class="sidebar-box cta-box">
            <h3>Beratung & Demo</h3>
            <p>Alle Kamado Joe Grills können Sie bei uns in Würzburg live erleben. Wir beraten Sie gerne persönlich.</p>
            <a href="/ausstellung-beratung/" class="btn btn-primary">Zur Ausstellung</a>
            <a href="/kontakt/" class="btn-outline" style="margin-top:8px">Kontakt aufnehmen</a>
          </div>
        </aside>
      </div>
    </section>
  </main>

  <footer class="site-footer">
    <div class="container footer-inner" style="padding:24px 0;border-top:1px solid #222;">
      <p style="color:#555;font-size:12px">&copy; 2025 Feuerhaus Kalina GmbH &middot;
        <a href="/impressum/" style="color:#555">Impressum</a> &middot;
        <a href="/datenschutz/" style="color:#555">Datenschutz</a>
      </p>
    </div>
  </footer>

  <div class="cookie-banner" id="cookie-banner" role="dialog" aria-label="Cookie-Hinweis">
    <p>Wir nutzen Cookies für eine optimale Nutzererfahrung. <a href="/datenschutz/">Mehr erfahren</a></p>
    <button onclick="document.getElementById('cookie-banner').style.display='none';localStorage.setItem('cookies','1')" class="btn btn-primary">Akzeptieren</button>
  </div>
  <script>if(localStorage.getItem('cookies'))document.getElementById('cookie-banner').style.display='none';</script>
  <script src="/js/main.js" defer></script>
</body>
</html>
"""


def generate_index_page(familien_data):
    cards_html = ""
    for fam, hero_img in familien_data:
        slug = fam["slug"]
        name = fam["name"]
        desc = fam["beschreibung"][:110] + "…"
        hero_src = f"/img/kamado-joe/{hero_img}" if hero_img else "/img/ui/placeholder.png"
        cards_html += f"""
      <article class="serie-card">
        <a href="/hersteller/kamado-joe/{slug}/">
          <div class="serie-card-img">
            <img data-src="{hero_src}" src="/img/ui/placeholder.png" alt="Kamado Joe {name}" class="lazy" loading="lazy">
          </div>
          <div class="serie-card-body">
            <span class="eyebrow">Kamado Joe</span>
            <h2>{name}</h2>
            <p>{desc}</p>
            <span class="btn-link">Modelle ansehen &rarr;</span>
          </div>
        </a>
      </article>"""

    return f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Kamado Joe Grills – Alle Modelle | Feuerhaus Kalina Würzburg</title>
  <meta name="description" content="Entdecken Sie alle Kamado Joe Grills: Joe Jr., Classic Joe und Big Joe in Serie I bis III sowie den Konnected Joe mit WLAN-Steuerung. Erhältlich in Würzburg.">
  <link rel="canonical" href="https://grills.feuerhaus-kalina.de/hersteller/kamado-joe/">
  <link rel="icon" href="/img/ui/favicon.ico">
  <link rel="stylesheet" href="/css/style.css">
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      {{"@type":"ListItem","position":1,"name":"Start","item":"https://grills.feuerhaus-kalina.de/"}},
      {{"@type":"ListItem","position":2,"name":"Hersteller","item":"https://grills.feuerhaus-kalina.de/hersteller/"}},
      {{"@type":"ListItem","position":3,"name":"Kamado Joe","item":"https://grills.feuerhaus-kalina.de/hersteller/kamado-joe/"}}
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
              <span itemprop="name">Kamado Joe</span>
              <meta itemprop="position" content="3">
            </li>
          </ol>
        </nav>
        <h1>Kamado Joe – Alle Modelle</h1>
        <p class="hero-lead">Von kompakt bis XXL: Kamado Joe bietet für jeden Anspruch den richtigen Grill. Alle Modelle können Sie in unserer Ausstellung in Würzburg live erleben und testen.</p>
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
          <h2>Warum Kamado Joe?</h2>
          <p>Kamado Joe steht seit Jahrzehnten für Keramikgrills der Extraklasse. Die doppelwandige Keramik isoliert perfekt – ob 100 °C zum Smoken oder 350 °C zum Pizzabacken. Einmal angefacht, reguliert sich die Temperatur über die Lüftungsschieber millimetergenau.</p>
        </div>
        <div>
          <h2>Beratung & Vorführung in Würzburg</h2>
          <p>In unserer Ausstellung finden Sie alle aktuellen Kamado Joe Modelle zum Anfassen. Unsere Experten zeigen Ihnen live die Unterschiede zwischen den Serien und helfen Ihnen bei der Wahl des richtigen Grills.</p>
          <a href="/ausstellung-beratung/" class="btn btn-primary">Ausstellung besuchen</a>
        </div>
      </div>
    </section>
  </main>

  <footer class="site-footer">
    <div class="container footer-inner" style="padding:24px 0;border-top:1px solid #222;">
      <p style="color:#555;font-size:12px">&copy; 2025 Feuerhaus Kalina GmbH &middot;
        <a href="/impressum/" style="color:#555">Impressum</a> &middot;
        <a href="/datenschutz/" style="color:#555">Datenschutz</a>
      </p>
    </div>
  </footer>

  <div class="cookie-banner" id="cookie-banner" role="dialog" aria-label="Cookie-Hinweis">
    <p>Wir nutzen Cookies für eine optimale Nutzererfahrung. <a href="/datenschutz/">Mehr erfahren</a></p>
    <button onclick="document.getElementById('cookie-banner').style.display='none';localStorage.setItem('cookies','1')" class="btn btn-primary">Akzeptieren</button>
  </div>
  <script>if(localStorage.getItem('cookies'))document.getElementById('cookie-banner').style.display='none';</script>
  <script src="/js/main.js" defer></script>
</body>
</html>
"""


# ─── MAIN ─────────────────────────────────────────────────────────────────────

print("Kamado Joe Scraper & HTML-Generator")
print("=" * 60)

# Alle Produkte laden
print("Lade Produkte von Shopify API...")
j = fetch_json("https://international.kamadojoe.com/de-eu/collections/grills/products.json?limit=50")
alle_produkte = {p["handle"]: p for p in j.get("products", [])}
print(f"  {len(alle_produkte)} Produkte geladen\n")

# Bilder downloaden
alle_imgs = {}  # handle -> [local_filename, ...]
gesamt_geladen = 0

for fam in FAMILIEN:
    print(f"── {fam['name']} ──")
    for handle in fam["produkte_handles"]:
        p = alle_produkte.get(handle)
        if not p:
            print(f"  FEHLER: {handle} nicht gefunden")
            continue
        imgs_local = []
        imgs = p.get("images", [])[:6]  # max 6 Bilder pro Produkt
        print(f"  {p['title'][:60]} ({len(imgs)} Bilder)")
        for i, img in enumerate(imgs):
            url = img["src"].split("?")[0]
            local = local_img_name(handle, url, i)
            dest = IMG_DIR / local
            new, size = download_image(url, dest)
            status = "↓" if new else "✓"
            print(f"    {status} {local} → {size // 1024} KB")
            if new:
                gesamt_geladen += 1
            imgs_local.append(local)
        alle_imgs[handle] = imgs_local
    print()

# HTML generieren
print("Generiere HTML-Seiten...")
out_dir = BASE_DIR / "hersteller" / "kamado-joe"
out_dir.mkdir(parents=True, exist_ok=True)

familien_data = []
for fam in FAMILIEN:
    slug = fam["slug"]
    produkte_data = [alle_produkte[h] for h in fam["produkte_handles"] if h in alle_produkte]

    # Hero-Bild = erstes Bild des ersten Produkts
    hero_img = None
    if fam["produkte_handles"] and fam["produkte_handles"][0] in alle_imgs:
        imgs = alle_imgs[fam["produkte_handles"][0]]
        if imgs:
            hero_img = imgs[0]

    familien_data.append((fam, hero_img))

    # Unterseite
    fam_dir = out_dir / slug
    fam_dir.mkdir(exist_ok=True)
    html = generate_familie_page(fam, produkte_data, alle_imgs)
    (fam_dir / "index.html").write_text(html, encoding="utf-8")
    print(f"  ✓ hersteller/kamado-joe/{slug}/index.html")

# Übersichtsseite
html = generate_index_page(familien_data)
(out_dir / "index.html").write_text(html, encoding="utf-8")
print("  ✓ hersteller/kamado-joe/index.html")

print()
print("=" * 60)
print("FERTIG")
print("=" * 60)
print(f"  Familien:      {len(FAMILIEN)}")
print(f"  Neu geladen:   {gesamt_geladen}")
print(f"  HTML-Seiten:   {len(FAMILIEN) + 1}")
print("=" * 60)
