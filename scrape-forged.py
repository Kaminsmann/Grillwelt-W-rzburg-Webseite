#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Forged Produkt-Scraper & HTML-Generator – Grillwelt Feuerhaus Kalina
=====================================================================
Lädt alle Forged-Produkte von StyleDeVie (bessere Bilder, deutsche Namen)
herunter und generiert vollständige HTML-Seiten für alle 9 Serien.

Verwendung:
  python scrape-forged.py              # Bilder laden + HTML generieren
  python scrape-forged.py --dry-run    # Nur anzeigen, nichts tun
  python scrape-forged.py --no-html    # Nur Bilder laden, kein HTML
  python scrape-forged.py --html-only  # Nur HTML generieren (Bilder vorhanden)

Ausgabe:
  img/forged/[serie]-[produkt].jpg     → Produktbilder
  messer/forged/index.html             → Serienübersicht
  messer/forged/[serie]/index.html     → Produktseite je Serie
  data/forged-produkte.json            → Produktdaten
"""

import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import os, re, json, time, urllib.request, urllib.error
from pathlib import Path

# ─── Konfiguration ────────────────────────────────────────────────────────────

BASE_DIR    = Path(__file__).parent
IMG_DIR     = BASE_DIR / "img" / "forged"
DATA_DIR    = BASE_DIR / "data"
HTML_DIR    = BASE_DIR / "messer" / "forged"

SDV_BASE    = "https://styledevie.nl"
IMG_PARAMS  = "?width=800&height=800&background=white"
DELAY       = 0.8

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "image/*,*/*;q=0.8",
    "Referer": "https://styledevie.nl/de/",
}

# ─── Vollständige Produktdaten (StyleDeVie, Stand 2025) ─────────────────────
# Format: { "name": "...", "img": "dateiname.jpg" }
# img-Pfad relativ zu https://styledevie.nl/content/products/

SERIEN = [
    {
        "slug":       "brachial",
        "name":       "Brachial",
        "sdv_serie":  "Brute",
        "headline":   "Forged Brachial – Kraft trifft Handwerk",
        "beschreibung": (
            "Die Brachial-Serie ist für alle, die es beim Kochen ernst meinen. "
            "Handgehämmerte Oberfläche, schwere Klinge, rustikales Design. "
            "Geschmiedet für BBQ, Camping und die professionelle Küche."
        ),
        "merkmale": ["Handgehämmerte Oberfläche", "Schwere, stabile Klinge", "Olivenholzgriff", "Robustes BBQ-Design"],
        "hero_img":   "brutebrood.jpg",
        "produkte": [
            {"name": "Forged Brachial 3-teiliges Küchenmesserset", "img": "brute3comb.jpg"},
            {"name": "Forged Brachial Ausbeinmesser",              "img": "bruteuitbeen.jpg"},
            {"name": "Forged Brachial Brotmesser",                 "img": "brutebrood.jpg"},
            {"name": "Forged Brachial Tranchiermesser",            "img": "brutevleesmes.jpg"},
            {"name": "Forged Brachial Hackbeil",                   "img": "brutehakbijl.jpg"},
            {"name": "Forged Brachial Kochmesser",                 "img": "brutekoksmes.jpg"},
            {"name": "Forged Brachial Kochmesser 16 cm",           "img": "brutekoks16cm.png"},
            {"name": "Forged Brachial Metzgermesser",              "img": "brutebutcher.jpg"},
            {"name": "Forged Brachial Santokumesser 14 cm",        "img": "brutesant14cm.jpg"},
            {"name": "Forged Brachial Santokumesser 18 cm",        "img": "brutesantoku18cm.jpg"},
            {"name": "Forged Brachial Schälmesser",                "img": "bruteschilmes.jpg"},
            {"name": "Forged Brachial Steakmesser",                "img": "brutesteakmes.jpg"},
            {"name": "Forged Brachial Universalmesser",            "img": "bruteunimes.jpg"},
            {"name": "Forged Brachial Diamant-Wetzstahl",          "img": "bruintaanzet.jpg"},
            {"name": "Forged Brachial Tranchiergabel",             "img": "bruinttranchvork.jpg"},
        ],
    },
    {
        "slug":       "intense",
        "name":       "Intense",
        "sdv_serie":  "Intense",
        "headline":   "Forged Intense – Präzision für die moderne Küche",
        "beschreibung": (
            "Intense steht für schlanke Klingengeometrie und ausgewogene Balance. "
            "Weniger Material, mehr Kontrolle – die Serie für alle, die präzise und "
            "effizient arbeiten wollen. Modernes Design, zeitlose Qualität."
        ),
        "merkmale": ["Schlanke Klingengeometrie", "Ausgewogene Balance", "Modernes Design", "Für Küchenprofis"],
        "hero_img":   "intkoksmes.jpg",
        "produkte": [
            {"name": "Forged Intense 3-teiliges Küchenmesserset", "img": "intense3comb.jpg"},
            {"name": "Forged Intense Ausbeinmesser",              "img": "intuitbeen.jpg"},
            {"name": "Forged Intense Brotmesser",                 "img": "intbroodmes.jpg"},
            {"name": "Forged Intense Tranchiermesser",            "img": "intvleesmes.jpg"},
            {"name": "Forged Intense Hackbeil",                   "img": "inthakbijl.jpg"},
            {"name": "Forged Intense Kochmesser",                 "img": "intkoksmes.jpg"},
            {"name": "Forged Intense Kochmesser 16 cm",           "img": "intensekoks16cm.png"},
            {"name": "Forged Intense Metzgermesser",              "img": "intbutcher.jpg"},
            {"name": "Forged Intense Santokumesser 14 cm",        "img": "intsant14cm.jpg"},
            {"name": "Forged Intense Santokumesser 18 cm",        "img": "intsantoku18cm.jpg"},
            {"name": "Forged Intense Schälmesser",                "img": "intschilmes.jpg"},
            {"name": "Forged Intense Steakmesser",                "img": "intsteakmes.jpg"},
            {"name": "Forged Intense Universalmesser",            "img": "intunimes.jpg"},
        ],
    },
    {
        "slug":       "olive",
        "name":       "Olive",
        "sdv_serie":  "Olive",
        "headline":   "Forged Olive – Naturmaterial trifft Klingenkunst",
        "beschreibung": (
            "Der unverwechselbare Olivenholzgriff macht die Olive-Serie zu etwas Besonderem. "
            "Kein Griff ist identisch – jedes Messer ist ein Unikat. Die Klinge aus "
            "hochwertigem Stahl ergänzt die warme Ästhetik des Naturholzes perfekt."
        ),
        "merkmale": ["Echter Olivenholzgriff (Unikat)", "Hochwertige Stahlklinge", "Warm & natürlich", "Breitestes Sortiment"],
        "hero_img":   "olivekoksmes.jpg",
        "produkte": [
            {"name": "Forged Olive 3-teiliges Küchenmesserset",   "img": "olive3comb.jpg"},
            {"name": "Forged Olive Asiatisches Hackmesser",       "img": "olivecleaver.jpg"},
            {"name": "Forged Olive Ausbeinmesser",                "img": "oliveuitbeen.jpg"},
            {"name": "Forged Olive Brotmesser",                   "img": "olivebrood.jpg"},
            {"name": "Forged Olive Diamant-Wetzstahl",            "img": "oliveaanzet.jpg"},
            {"name": "Forged Olive Fischfiletiermesser",          "img": "olivevisfileer.png"},
            {"name": "Forged Olive Tranchiermesser",              "img": "olivevlees.jpg"},
            {"name": "Forged Olive Hackbeil",                     "img": "olivehakbijl.jpg"},
            {"name": "Forged Olive Kinderkochmesser",             "img": "olivekindkoks.png"},
            {"name": "Forged Olive Kochmesser",                   "img": "olivekoksmes.jpg"},
            {"name": "Forged Olive Kochmesser 16 cm",             "img": "olivekoks16cm.png"},
            {"name": "Forged Olive Metzgermesser",                "img": "olivebutcher.jpg"},
            {"name": "Forged Olive Petty Messer 11 cm",           "img": "olivepetty11.jpg"},
            {"name": "Forged Olive Santokumesser 14 cm",          "img": "olivesantoku14cm.jpg"},
            {"name": "Forged Olive Santokumesser 18 cm",          "img": "olivesantoku18cm.jpg"},
            {"name": "Forged Olive Schälmesser",                  "img": "oliveschilmes.jpg"},
            {"name": "Forged Olive Steakmesser",                  "img": "olivesteakmes.jpg"},
            {"name": "Forged Olive Steakmesser XXL",              "img": "olivesteakxxl.jpg"},
            {"name": "Forged Olive Tranchiergabel",               "img": "olivetranchvork.jpg"},
            {"name": "Forged Olive Universalmesser",              "img": "oliveuni.jpg"},
            {"name": "Forged Olive Universalmesser gezahnt",      "img": "oliveuniser.jpg"},
        ],
    },
    {
        "slug":       "sebra",
        "name":       "Sebra",
        "sdv_serie":  "Sebra",
        "headline":   "Forged Sebra – Charakterstarkes Zebramuster",
        "beschreibung": (
            "Die Sebra-Serie fällt sofort auf: Das charakteristische Zebramuster-Finish "
            "auf der Klinge macht jedes Messer zum Statement. Unter dem Design steckt "
            "hochwertige Schmiedequalität – für Liebhaber mit Stil."
        ),
        "merkmale": ["Unverwechselbares Zebramuster", "Hochwertige Schmiedeklinge", "Für Design-Bewusste", "Gesprächsstarter"],
        "hero_img":   "sebrakoksmes.jpg",
        "produkte": [
            {"name": "Forged Sebra 3-teiliges Küchenmesserset",   "img": "sebra3comb.jpg"},
            {"name": "Forged Sebra Asiatisches Hackmesser",       "img": "sebracleaver.jpg"},
            {"name": "Forged Sebra Ausbeinmesser",                "img": "sebrauitbeen.jpg"},
            {"name": "Forged Sebra Brotmesser",                   "img": "sebrabrood.jpg"},
            {"name": "Forged Sebra Diamant-Wetzstahl",            "img": "sebraaanzet.jpg"},
            {"name": "Forged Sebra Tranchiermesser",              "img": "sebravlees.jpg"},
            {"name": "Forged Sebra Hackbeil",                     "img": "sebrahakbijl.jpg"},
            {"name": "Forged Sebra Kochmesser",                   "img": "sebrakoksmes.jpg"},
            {"name": "Forged Sebra Kochmesser 16 cm",             "img": "sebrakoks16cm.png"},
            {"name": "Forged Sebra Metzgermesser",                "img": "sebrabutcher.jpg"},
            {"name": "Forged Sebra Santokumesser 14 cm",          "img": "sebrasantoku14cm.jpg"},
            {"name": "Forged Sebra Santokumesser 18 cm",          "img": "sebrasantoku18cm.jpg"},
            {"name": "Forged Sebra Schälmesser",                  "img": "sebraschil.jpg"},
            {"name": "Forged Sebra Steakmesser",                  "img": "sebrasteakmes.jpg"},
            {"name": "Forged Sebra Tranchiergabel",               "img": "sebratranchvork.jpg"},
            {"name": "Forged Sebra Universalmesser",              "img": "sebrauni.jpg"},
        ],
    },
    {
        "slug":       "vg10",
        "name":       "VG10",
        "sdv_serie":  "VG10",
        "headline":   "Forged VG10 – Japanischer Stahl, europäische Seele",
        "beschreibung": (
            "VG10-Stahl aus Japan gilt als einer der besten Messerstähle der Welt. "
            "Härte von 60+ HRC, außergewöhnliche Schärfe, überlegene Kantenstabilität. "
            "Forged kombiniert diesen Stahl mit europäischem Handwerk zu einem Messer "
            "für absolute Perfektion."
        ),
        "merkmale": ["VG10-Stahl (60+ HRC)", "Außergewöhnliche Schärfe", "Kantenstabilität", "Erhältlich mit Lederetui"],
        "hero_img":   "vg10koksmes.jpg",
        "produkte": [
            {"name": "Forged VG10 Ausbeinmesser",                 "img": "vg10uitbeen.jpg"},
            {"name": "Forged VG10 Brotmesser",                    "img": "vg10brood.jpg"},
            {"name": "Forged VG10 Bunka Messerset mit Lederetui", "img": "vg10bunkagift.jpg"},
            {"name": "Forged VG10 Fischfiletiermesser",           "img": "vg10visfileer.jpg"},
            {"name": "Forged VG10 Tranchiermesser",               "img": "vg10vlees.jpg"},
            {"name": "Forged VG10 Hackbeil",                      "img": "vg10hakbijl.jpg"},
            {"name": "Forged VG10 Kochmesser",                    "img": "vg10koksmes.jpg"},
            {"name": "Forged VG10 Kochmesser mit Lederetui",      "img": "vg10koksleer.jpg"},
            {"name": "Forged VG10 Kochmesser 16 cm",              "img": "vg10koks16cm.png"},
            {"name": "Forged VG10 Metzgermesser",                 "img": "vg10butcher.jpg"},
            {"name": "Forged VG10 Santokumesser 14 cm",           "img": "vg10sant14.jpg"},
            {"name": "Forged VG10 Santokumesser 18 cm",           "img": "vg10sant18.jpg"},
            {"name": "Forged VG10 Universalmesser",               "img": "vg10uni.jpg"},
            {"name": "Forged VG10 Universalmesser gezahnt",       "img": "vg10uniser.jpg"},
            {"name": "Forged VG10 Diamant-Wetzstahl",             "img": "vg10aanzet.jpg"},
        ],
    },
    {
        "slug":       "katai",
        "name":       "Katai",
        "sdv_serie":  "Katai",
        "headline":   "Forged Katai – Gehärteter Stahl mit japanischer Seele",
        "beschreibung": (
            "Katai bedeutet auf Japanisch 'hart' – und das spürt man. Die Serie "
            "verwendet besonders gehärteten Stahl für eine langanhaltende, "
            "messerscharfe Kante. Schlichtes, zeitloses Design ohne Kompromisse."
        ),
        "merkmale": ["Besonders gehärteter Stahl", "Langanhaltende Schärfe", "Schlichtes Design", "Zeitlose Qualität"],
        "hero_img":   "katkoksmes.jpg",
        "produkte": [
            {"name": "Forged Katai Ausbeinmesser",      "img": "katuitbeen.jpg"},
            {"name": "Forged Katai Brotmesser",         "img": "katbrood.jpg"},
            {"name": "Forged Katai Tranchiermesser",    "img": "katvlees.jpg"},
            {"name": "Forged Katai Kochmesser",         "img": "katkoksmes.jpg"},
            {"name": "Forged Katai Kochmesser 16 cm",   "img": "kataikoks16cm.png"},
            {"name": "Forged Katai Metzgermesser",      "img": "katbutcher.jpg"},
            {"name": "Forged Katai Santokumesser 14 cm","img": "katsant14cm.jpg"},
            {"name": "Forged Katai Santokumesser 18 cm","img": "katsant18cm.jpg"},
            {"name": "Forged Katai Universalmesser",    "img": "katuni.jpg"},
            {"name": "Forged Katai Diamant-Wetzstahl",  "img": "kataanzet.jpg"},
        ],
    },
    {
        "slug":       "bbq",
        "name":       "BBQ",
        "sdv_serie":  "BBQ",
        "headline":   "Forged BBQ – Grillzubehör mit Olivenholzgriff",
        "beschreibung": (
            "Die BBQ-Serie bringt Forged-Qualität an den Grill. Edelstahl-Zangen, "
            "Spachtel und der legendäre Flambadou – alle mit dem charakteristischen "
            "Olivenholzgriff. Für den, der auch beim Grillen keine Kompromisse macht."
        ),
        "merkmale": ["Edelstahl-Qualität", "Olivenholzgriff", "Für offenes Feuer", "Plancha-kompatibel"],
        "hero_img":   "olflambadou.jpg",
        "produkte": [
            {"name": "Forged BBQ Gripperzange XL",   "img": "oltongsxl.png"},
            {"name": "Forged BBQ Plancha-Spatel",    "img": "olplanchaspat.png"},
            {"name": "Forged BBQ Spachtel XL",       "img": "olspat.png"},
            {"name": "Forged Flambadou",             "img": "olflambadou.jpg"},
        ],
    },
    {
        "slug":       "churrasco",
        "name":       "Churrasco",
        "sdv_serie":  "Churrasco",
        "headline":   "Forged Churrasco – Das südamerikanische Grillerlebnis",
        "beschreibung": (
            "Churrasco ist mehr als Grillen – es ist eine Kultur. Die Forged "
            "Churrasco-Serie bringt die Tradition des südamerikanischen "
            "Feuerkochens nach Europa: Lange Spieße, Zangen und Zubehör aus "
            "Edelstahl mit Olivenholzgriff."
        ),
        "merkmale": ["Südamerikanische Grilltradition", "Lange Spieße bis 70 cm", "Olivenholzgriff", "Für offenes Feuer"],
        "hero_img":   "olskewf60.jpg",
        "produkte": [
            {"name": "Forged Churrasco 4 Greifzangen",         "img": "chur4tongs.jpg"},
            {"name": "Forged Churrasco Gabelspieß 50 cm",      "img": "olskewf50.jpg"},
            {"name": "Forged Churrasco Gabelspieß 60 cm",      "img": "olskewf60.jpg"},
            {"name": "Forged Churrasco Gabelspieß 70 cm",      "img": "olskewf70.jpg"},
            {"name": "Forged Churrasco Spieß V-Form 50 cm",    "img": "olskewv50.jpg"},
            {"name": "Forged Churrasco Spieß V-Form 60 cm",    "img": "olskewv60.jpg"},
            {"name": "Forged Churrasco Spieß V-Form 70 cm",    "img": "olskewv70.jpg"},
            {"name": "Forged Churrasco Servierpfanne",         "img": "olserver.jpg"},
        ],
    },
    {
        "slug":       "essentials",
        "name":       "Essentials",
        "sdv_serie":  "Essentials",
        "headline":   "Forged Essentials – Aufbewahrung, Pflege & Zubehör",
        "beschreibung": (
            "Die Essentials-Serie vervollständigt jede Forged-Kollektion. "
            "Hochwertige Lederscheiden für jede Klingenform, ein rotierender "
            "Magnetmesserblock, Pfannen und Pflegesets – alles was man für "
            "den perfekten Umgang mit Forged-Messern braucht."
        ),
        "merkmale": ["Lederscheiden für alle Forged-Modelle", "Rotierender Messerblock", "Gusseisen-Pfannen", "Pflege-Sets"],
        "hero_img":   "esmagnblolive.jpg",
        "produkte": [
            {"name": "Forged Bratpfanne 24 cm",                   "img": "esfrypan1h24.jpg"},
            {"name": "Forged Bratpfanne 28 cm",                   "img": "esfrypan1h28.jpg"},
            {"name": "Forged Bratpfanne 20 cm",                   "img": "esfrypan1h20.jpg"},
            {"name": "Forged Bratpfanne mit 2 Griffen 20 cm",     "img": "esfrypan2h20.jpg"},
            {"name": "Forged Bratpfanne mit 2 Griffen 24 cm",     "img": "esfrypan2h24.png"},
            {"name": "Forged Bratpfanne mit 2 Griffen 28 cm",     "img": "esfrypan2h28.png"},
            {"name": "Forged Ledertasche Braun",                  "img": "eskniferoll8brown.png"},
            {"name": "Forged Magnetischer Messerblock rotierend", "img": "esmagnblolive.jpg"},
            {"name": "Forged Pflegeset",                          "img": "esmaintkit.png"},
            {"name": "Forged Schneidebrett Natur Large",          "img": "escutbrdnatl.jpg"},
            {"name": "Forged Schneidebrett Natur Medium",         "img": "escutbrdnatm.jpg"},
            {"name": "Forged Lederetui Kochmesser",               "img": "leer1koksmes.jpg"},
            {"name": "Forged Lederetui Kochmesser 16 cm",         "img": "leer1koks16cm.jpg"},
            {"name": "Forged Lederetui Santokumesser 14 cm",      "img": "leer1sant14.jpg"},
            {"name": "Forged Lederetui Santokumesser 18 cm",      "img": "leer1sant18.jpg"},
            {"name": "Forged Lederetui Ausbeinmesser",            "img": "leer1uitbeen.jpg"},
            {"name": "Forged Lederetui Brotmesser",               "img": "leer1brood.jpg"},
            {"name": "Forged Lederetui Tranchiermesser",          "img": "leer1vlees.jpg"},
            {"name": "Forged Lederetui Metzgermesser",            "img": "leer1butcher.jpg"},
            {"name": "Forged Lederetui Hackbeil",                 "img": "leer1hakbijl.jpg"},
            {"name": "Forged Lederetui Fischfiletiermesser",      "img": "leer1visfileer.png"},
            {"name": "Forged Lederetui Asiatisches Hackmesser",   "img": "leer1cleaver.jpg"},
            {"name": "Forged Lederetui Universalmesser",          "img": "leer1uni.jpg"},
        ],
    },
]

# ─── Bild herunterladen ───────────────────────────────────────────────────────

def local_img_path(serie_slug: str, img_filename: str) -> Path:
    ext  = Path(img_filename).suffix
    stem = Path(img_filename).stem
    name = f"forged-{serie_slug}-{stem}{ext}"
    return IMG_DIR / name

def download_image(url: str, dest: Path, dry_run: bool) -> bool:
    if dest.exists():
        print(f"  ✓ {dest.name}")
        return True
    if dry_run:
        print(f"  [dry] {dest.name}")
        return True
    print(f"  ↓ {dest.name}")
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=20) as r:
            data = r.read()
        if len(data) < 500:
            print(f"    ✗ Zu klein ({len(data)} B)")
            return False
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        print(f"    → {len(data)//1024} KB")
        return True
    except Exception as e:
        print(f"    ✗ {e}")
        return False

# ─── HTML-Helfer ──────────────────────────────────────────────────────────────

NAV = """  <nav class="site-nav" role="navigation" aria-label="Hauptnavigation">
    <div class="container">
      <div class="nav-inner">
        <a href="/" class="nav-logo" aria-label="Feuerhaus Kalina Grillwelt – Startseite">
          Feuerhaus <span>Kalina</span>
          <sub>Grillwelt &amp; Outdoor Living</sub>
        </a>
        <ul class="nav-links" role="list">
          <li><a href="/outdoor-kuechen/">Outdoor-Küchen</a></li>
          <li><a href="/keramikgrills-kamado/">Kamado &amp; Grill</a></li>
          <li><a href="/plancha-feuerplatten/">Plancha</a></li>
          <li><a href="/zubehoer/">Zubehör</a></li>
          <li><a href="/hersteller/">Hersteller</a></li>
          <li><a href="/ratgeber/">Ratgeber</a></li>
        </ul>
        <div class="nav-end">
          <div class="nav-tel"><a href="tel:+4993658884218">09365 / 888 42 18</a></div>
          <a href="/kontakt/" class="nav-cta">Beratung anfragen</a>
        </div>
        <button class="nav-toggle" aria-label="Menü öffnen" aria-expanded="false">
          <span></span><span></span><span></span>
        </button>
      </div>
    </div>
  </nav>"""

FOOTER = """  <footer class="site-footer" role="contentinfo">
    <div class="container">
      <div class="footer-bottom">
        <span class="footer-copy">© 2025 Feuerhaus Kalina · Maidbronner Straße 3 · 97222 Rimpar</span>
        <div class="footer-legal">
          <a href="/impressum/">Impressum</a>
          <a href="/datenschutz/">Datenschutz</a>
        </div>
      </div>
    </div>
  </footer>

  <div class="cookie-banner" id="cookieBanner" role="dialog" aria-label="Cookie-Hinweis" style="display:none;">
    <div class="cookie-inner">
      <p>Diese Website verwendet funktionale Cookies sowie Analyse-Tools. Mit Klick auf „Akzeptieren" stimmen Sie zu. <a href="/datenschutz/">Datenschutz</a></p>
      <div class="cookie-actions">
        <button class="btn btn-primary" id="cookieAccept">Akzeptieren</button>
        <button class="btn" id="cookieDecline" style="background:transparent;border:1px solid rgba(255,255,255,0.3);color:var(--weiss);">Ablehnen</button>
      </div>
    </div>
  </div>

  <script src="/js/main.js" defer></script>"""

PRODUCT_GRID_CSS = """  <style>
    .produkte-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
      gap: 24px;
    }
    .produkt-karte {
      background: var(--weiss);
      border-radius: 4px;
      box-shadow: 0 2px 8px rgba(0,0,0,.06);
      overflow: hidden;
      transition: transform .25s, box-shadow .25s;
    }
    .produkt-karte:hover {
      transform: translateY(-4px);
      box-shadow: 0 8px 24px rgba(0,0,0,.1);
    }
    .produkt-img {
      width: 100%;
      aspect-ratio: 1/1;
      object-fit: contain;
      background: var(--creme);
      padding: 16px;
      display: block;
    }
    .produkt-body {
      padding: 14px 18px 18px;
    }
    .produkt-body h3 {
      font-family: var(--font-serif);
      font-size: 15px;
      margin: 0 0 12px;
      color: var(--anthrazit);
      line-height: 1.4;
    }
  </style>"""

# ─── HTML: Serie-Unterseite ───────────────────────────────────────────────────

def generate_serie_page(serie: dict) -> str:
    slug  = serie["slug"]
    name  = serie["name"]
    n     = len(serie["produkte"])

    cards = ""
    for p in serie["produkte"]:
        local = local_img_path(slug, p["img"])
        img_src = f"/img/forged/{local.name}"
        cards += f"""
      <div class="produkt-karte">
        <img src="/img/ui/placeholder.png" data-src="{img_src}"
             alt="{p['name']} kaufen Würzburg"
             class="produkt-img" loading="lazy">
        <div class="produkt-body">
          <h3>{p['name']}</h3>
          <a href="/kontakt/" class="btn btn-primary" style="font-size:13px;padding:8px 16px;">Preis anfragen</a>
        </div>
      </div>"""

    merkmale_html = "".join(
        f'<li style="padding:8px 0;border-bottom:1px solid var(--creme);color:var(--grau-mid);font-size:14px;">✓ {m}</li>'
        for m in serie["merkmale"]
    )

    return f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Forged {name} Messer kaufen Würzburg – {n} Produkte | Feuerhaus Kalina</title>
  <meta name="description" content="Forged {name} Serie kaufen in Rimpar bei Würzburg. {n} Produkte: {', '.join(p['name'].replace('Forged '+name+' ','') for p in serie['produkte'][:4])} und mehr. Autorisierter Forged Händler.">
  <link rel="canonical" href="https://grills.feuerhaus-kalina.de/messer/forged/{slug}/">
  <link rel="icon" type="image/x-icon" href="/img/ui/favicon.ico">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/css/style.css">
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      {{"@type":"ListItem","position":1,"name":"Startseite","item":"https://grills.feuerhaus-kalina.de/"}},
      {{"@type":"ListItem","position":2,"name":"Messer","item":"https://grills.feuerhaus-kalina.de/messer/"}},
      {{"@type":"ListItem","position":3,"name":"Forged","item":"https://grills.feuerhaus-kalina.de/messer/forged/"}},
      {{"@type":"ListItem","position":4,"name":"{name}","item":"https://grills.feuerhaus-kalina.de/messer/forged/{slug}/"}}
    ]
  }}
  </script>
{PRODUCT_GRID_CSS}
</head>
<body>

{NAV}

  <div class="breadcrumbs">
    <div class="breadcrumbs-inner container">
      <a href="/">Startseite</a><span>›</span>
      <a href="/messer/">Messer</a><span>›</span>
      <a href="/messer/forged/">Forged</a><span>›</span>
      <span>{name}</span>
    </div>
  </div>

  <section class="page-hero">
    <div class="page-hero-inner container">
      <span class="eyebrow">Forged – Serie {name}</span>
      <h1>{serie["headline"]}</h1>
      <p>{serie["beschreibung"]}</p>
    </div>
  </section>

  <section class="section-padding" style="background:var(--creme);">
    <div class="container">
      <div style="display:grid;grid-template-columns:2fr 1fr;gap:64px;align-items:start;margin-bottom:64px;">
        <div>
          <span class="eyebrow">Alle Produkte</span>
          <h2 style="font-family:var(--font-serif);font-size:clamp(22px,2vw,32px);margin:12px 0 32px;color:var(--anthrazit);">{n} Produkte in der {name}-Serie</h2>
          <div class="produkte-grid">
            {cards}
          </div>
        </div>
        <div style="position:sticky;top:100px;">
          <div style="background:var(--weiss);border-radius:4px;padding:32px;">
            <span class="eyebrow">Eigenschaften</span>
            <h3 style="font-family:var(--font-serif);font-size:20px;margin:12px 0 20px;color:var(--anthrazit);">Die {name}-Serie auf einen Blick</h3>
            <ul style="list-style:none;padding:0;margin:0 0 28px;">
              {merkmale_html}
            </ul>
            <a href="/messer/forged/" style="color:var(--grau-mid);font-size:13px;display:block;margin-bottom:16px;">← Alle Forged-Serien</a>
            <a href="/kontakt/" class="btn btn-primary" style="display:block;text-align:center;">Beratung anfragen</a>
          </div>
        </div>
      </div>
    </div>
  </section>

  <section class="beratungs-block">
    <div class="beratungs-inner container">
      <div>
        <span class="eyebrow">Forged {name} live erleben</span>
        <h2>Messer kauft man mit der Hand</h2>
        <p>Kommen Sie in unsere Ausstellung in Rimpar – wir zeigen Ihnen die {name}-Serie und alle anderen Forged-Serien im direkten Vergleich.</p>
      </div>
      <div style="display:flex;gap:16px;flex-wrap:wrap;">
        <a href="/kontakt/" class="btn btn-primary">Termin vereinbaren</a>
        <a href="/messer/forged/" class="btn" style="background:transparent;border:1px solid rgba(255,255,255,0.4);color:var(--weiss);">Alle Forged-Serien</a>
      </div>
    </div>
  </section>

{FOOTER}
</body>
</html>"""

# ─── HTML: Forged Index (Serienübersicht) ─────────────────────────────────────

def generate_index_page() -> str:
    total = sum(len(s["produkte"]) for s in SERIEN)

    series_cards = ""
    for s in SERIEN:
        local = local_img_path(s["slug"], s["hero_img"])
        img_src = f"/img/forged/{local.name}"
        n = len(s["produkte"])
        series_cards += f"""
      <a href="/messer/forged/{s['slug']}/" class="serie-card" style="display:block;background:var(--weiss);border-radius:4px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.06);transition:transform .25s,box-shadow .25s;text-decoration:none;" onmouseover="this.style.transform='translateY(-4px)';this.style.boxShadow='0 8px 24px rgba(0,0,0,.12)'" onmouseout="this.style.transform='';this.style.boxShadow='0 2px 8px rgba(0,0,0,.06)'">
        <img src="/img/ui/placeholder.png" data-src="{img_src}"
             alt="Forged {s['name']} Messer kaufen Würzburg"
             loading="lazy"
             style="width:100%;aspect-ratio:4/3;object-fit:contain;background:var(--creme);padding:24px;">
        <div style="padding:20px 24px 24px;">
          <span style="font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--rot);font-weight:600;">{n} Produkte</span>
          <h2 style="font-family:var(--font-serif);font-size:22px;margin:6px 0 10px;color:var(--anthrazit);">{s['name']}</h2>
          <p style="color:var(--grau-mid);font-size:14px;line-height:1.6;margin:0 0 16px;">{s['beschreibung'][:120]}…</p>
          <span style="color:var(--rot);font-size:13px;font-weight:600;">Zur Serie →</span>
        </div>
      </a>"""

    return f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Forged Messer kaufen Würzburg – alle 9 Serien | Feuerhaus Kalina</title>
  <meta name="description" content="Forged Messer kaufen in Rimpar bei Würzburg. Alle 9 Serien: Brachial, Intense, Olive, Sebra, VG10, Katai, BBQ, Churrasco, Essentials – {total} Produkte. Autorisierter Händler.">
  <link rel="canonical" href="https://grills.feuerhaus-kalina.de/messer/forged/">
  <link rel="icon" type="image/x-icon" href="/img/ui/favicon.ico">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/css/style.css">
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      {{"@type":"ListItem","position":1,"name":"Startseite","item":"https://grills.feuerhaus-kalina.de/"}},
      {{"@type":"ListItem","position":2,"name":"Messer","item":"https://grills.feuerhaus-kalina.de/messer/"}},
      {{"@type":"ListItem","position":3,"name":"Forged","item":"https://grills.feuerhaus-kalina.de/messer/forged/"}}
    ]
  }}
  </script>
</head>
<body>

{NAV}

  <div class="breadcrumbs">
    <div class="breadcrumbs-inner container">
      <a href="/">Startseite</a><span>›</span>
      <a href="/messer/">Messer</a><span>›</span>
      <span>Forged</span>
    </div>
  </div>

  <section class="page-hero">
    <div class="page-hero-inner container">
      <span class="eyebrow">Handgeschmiedete Messer</span>
      <h1>Forged – Meisterhafte Klingen für Küche &amp; Grill</h1>
      <p>Forged vereint europäisches Schmiedehandwerk mit modernem Design. {total} Produkte in 9 einzigartigen Serien – von der robusten Brachial-Klinge bis zum japanischen VG10-Stahl. Autorisierter Forged Händler in Rimpar bei Würzburg.</p>
    </div>
  </section>

  <section class="section-padding" style="background:var(--creme);">
    <div class="container">
      <div style="text-align:center;margin-bottom:56px;">
        <span class="eyebrow">9 Serien</span>
        <h2 style="font-family:var(--font-serif);font-size:clamp(24px,2.5vw,36px);margin:12px 0 16px;color:var(--anthrazit);">Wählen Sie Ihre Forged-Serie</h2>
        <p style="color:var(--grau-mid);max-width:560px;margin:0 auto;font-size:15px;line-height:1.7;">Jede Serie hat ihre eigene Persönlichkeit. Klicken Sie auf eine Serie um alle Produkte zu sehen und mehr über das Design und die Materialien zu erfahren.</p>
      </div>
      <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:28px;">
        {series_cards}
      </div>
    </div>
  </section>

  <section style="background:var(--anthrazit);padding:80px 0;">
    <div class="container" style="max-width:720px;text-align:center;">
      <span class="eyebrow" style="color:var(--rot);">Europäisches Handwerk</span>
      <h2 style="font-family:var(--font-serif);font-size:clamp(24px,2.5vw,36px);color:var(--weiss);margin:16px 0 24px;">"Jedes Forged-Messer ist ein Werkzeug – und ein Objekt."</h2>
      <p style="color:rgba(255,255,255,0.7);line-height:1.8;font-size:15px;">Forged-Messer werden nach traditionellen Schmiedeverfahren hergestellt. Jede Klinge wird von Hand geformt, gehärtet und geschliffen – das Ergebnis ist ein Messer, das Generationen übersteht.</p>
    </div>
  </section>

  <section class="section-padding" style="background:var(--weiss);">
    <div class="container" style="max-width:780px;">
      <h2 style="font-family:var(--font-serif);font-size:clamp(22px,2vw,30px);margin-bottom:32px;color:var(--anthrazit);">Häufige Fragen zu Forged Messern</h2>
      <div class="faq-item">
        <button class="faq-question" aria-expanded="false">Welche Forged-Serie ist für den BBQ geeignet?</button>
        <div class="faq-answer">
          <p>Die Brachial-Serie ist mit ihrer robusten, schweren Klinge ideal für den BBQ-Einsatz. Speziell für das Grillen gibt es auch die BBQ-Serie mit Zangen, Spachtel und Flambadou sowie die Churrasco-Serie für südamerikanisches Feuergrillen.</p>
        </div>
      </div>
      <div class="faq-item">
        <button class="faq-question" aria-expanded="false">Was ist der Unterschied zwischen VG10 und den anderen Serien?</button>
        <div class="faq-answer">
          <p>VG10 ist ein japanischer Hochleistungsstahl mit 60+ HRC Härte – deutlich härter als die anderen Serien. Das bedeutet: schärfer, längere Kantenstabilität, aber auch empfindlicher bei falscher Handhabung. Für Hobbyköche sind Olive oder Brachial oft die bessere Wahl.</p>
        </div>
      </div>
      <div class="faq-item">
        <button class="faq-question" aria-expanded="false">Sind Forged-Messer spülmaschinenfest?</button>
        <div class="faq-answer">
          <p>Nein – alle Forged-Messer sollten von Hand gewaschen werden. Spülmaschinen schädigen den Holzgriff und beschleunigen die Oxidation der Klinge. Handwäsche mit warmem Wasser und trocknen ist alles was sie brauchen.</p>
        </div>
      </div>
      <div class="faq-item">
        <button class="faq-question" aria-expanded="false">Kann ich einzelne Messer nachkaufen?</button>
        <div class="faq-answer">
          <p>Ja – jedes Messer aus allen Serien ist einzeln erhältlich. Fragen Sie uns nach dem aktuellen Lagerbestand oder vereinbaren Sie einen Termin in unserer Ausstellung in Rimpar.</p>
        </div>
      </div>
    </div>
  </section>

  <section class="beratungs-block">
    <div class="beratungs-inner container">
      <div>
        <span class="eyebrow">Persönliche Beratung</span>
        <h2>Forged Messer in unserer Ausstellung</h2>
        <p>Messer kauft man mit der Hand, nicht mit dem Bildschirm. Kommen Sie in unsere Ausstellung nach Rimpar – wir zeigen Ihnen alle 9 Serien und helfen Ihnen bei der Wahl.</p>
      </div>
      <div style="display:flex;gap:16px;flex-wrap:wrap;">
        <a href="/kontakt/" class="btn btn-primary">Beratungstermin anfragen</a>
        <a href="/ausstellung-beratung/" class="btn" style="background:transparent;border:1px solid rgba(255,255,255,0.4);color:var(--weiss);">Zur Ausstellung</a>
      </div>
    </div>
  </section>

{FOOTER}
</body>
</html>"""

# ─── Hauptprogramm ────────────────────────────────────────────────────────────

def main():
    dry_run   = "--dry-run"   in sys.argv
    html_only = "--html-only" in sys.argv
    no_html   = "--no-html"   in sys.argv

    print("Forged Produkt-Scraper & HTML-Generator")
    print("=" * 60)

    all_products = []
    downloaded = skipped = failed = 0

    if not html_only:
        IMG_DIR.mkdir(parents=True, exist_ok=True)
        print(f"Bilder → {IMG_DIR}\n")

        for serie in SERIEN:
            print(f"\n── {serie['name']} ({len(serie['produkte'])} Produkte) ──")
            for p in serie["produkte"]:
                url  = f"{SDV_BASE}/content/products/{p['img']}{IMG_PARAMS}"
                dest = local_img_path(serie["slug"], p["img"])

                if dest.exists():
                    skipped += 1
                else:
                    ok = download_image(url, dest, dry_run)
                    if ok:
                        downloaded += 1
                    else:
                        failed += 1
                    if not dry_run:
                        time.sleep(DELAY)

                all_products.append({
                    "serie":      serie["name"],
                    "serie_slug": serie["slug"],
                    "name":       p["name"],
                    "bild_lokal": f"img/forged/{dest.name}",
                    "bild_url":   url,
                })

        # JSON speichern
        if not dry_run:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            (DATA_DIR / "forged-produkte.json").write_text(
                json.dumps(all_products, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
            print(f"\n✓ JSON: {DATA_DIR / 'forged-produkte.json'}")
    else:
        print("HTML-Only Modus – überspringe Downloads\n")

    # HTML generieren
    if not no_html and not dry_run:
        print("\nGeneriere HTML-Seiten...")

        # Index
        HTML_DIR.mkdir(parents=True, exist_ok=True)
        index_html = generate_index_page()
        (HTML_DIR / "index.html").write_text(index_html, encoding="utf-8")
        print(f"  ✓ messer/forged/index.html")

        # Unterseiten je Serie
        for serie in SERIEN:
            serie_dir = HTML_DIR / serie["slug"]
            serie_dir.mkdir(parents=True, exist_ok=True)
            page_html = generate_serie_page(serie)
            (serie_dir / "index.html").write_text(page_html, encoding="utf-8")
            print(f"  ✓ messer/forged/{serie['slug']}/index.html")

    # Zusammenfassung
    print("\n" + "=" * 60)
    print("FERTIG")
    print("=" * 60)
    total = sum(len(s["produkte"]) for s in SERIEN)
    print(f"  Serien:            {len(SERIEN)}")
    print(f"  Produkte gesamt:   {total}")
    if not html_only:
        print(f"  Heruntergeladen:   {downloaded}")
        print(f"  Bereits vorhanden: {skipped}")
        if failed: print(f"  Fehlgeschlagen:    {failed}")
    if not no_html and not dry_run:
        print(f"  HTML-Seiten:       {len(SERIEN) + 1}")
    print("=" * 60)

if __name__ == "__main__":
    main()
