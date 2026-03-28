#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Style de Vie Produkt-Scraper & HTML-Generator – Grillwelt Feuerhaus Kalina
===========================================================================
Lädt alle Produkte von styledevie.nl herunter und generiert HTML-Seiten.

Marken: Laguiole Style de Vie (4 Serien), Style de Vie, Plate-it

Verwendung:
  python scrape-styledevie.py              # Bilder laden + HTML generieren
  python scrape-styledevie.py --dry-run    # Nur anzeigen
  python scrape-styledevie.py --html-only  # Nur HTML (Bilder schon vorhanden)
  python scrape-styledevie.py --no-html    # Nur Bilder
"""

import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import json, time, urllib.request, urllib.error
from pathlib import Path

BASE_DIR   = Path(__file__).parent
IMG_DIR    = BASE_DIR / "img"
DATA_DIR   = BASE_DIR / "data"
HTML_DIR   = BASE_DIR / "tischkultur-servieren"

SDV_BASE   = "https://styledevie.nl"
IMG_PARAMS = "?width=800&height=800&background=white"
DELAY      = 0.8

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "Accept": "image/*,*/*;q=0.8",
    "Referer": "https://styledevie.nl/de/",
}

# ─── Produktdaten ─────────────────────────────────────────────────────────────

LAGUIOLE_SERIEN = [
    {
        "slug":         "innovation-line",
        "name":         "Innovation Line",
        "headline":     "Innovation Line – Modernes Design aus Pakkaholz & Eiche",
        "beschreibung": "Die Innovation Line verbindet das klassische Laguiole-Erbe mit zeitgemäßen Materialien. Griff aus grauem Pakkaholz oder Eichenholz – pflegeleicht, modern und für den täglichen Gebrauch gemacht.",
        "merkmale":     ["Grau Pakkaholz oder Eichenholz", "Spülmaschinengeeignet", "Modernes Design", "Alltagstauglich"],
        "hero_img":     "innokoksseteik.jpg",
        "produkte": [
            {"name": "Innovation Line Buttermesser Graues Pakkaholz",                      "img": "innobotergrijs.jpg"},
            {"name": "Innovation Line Kochmesserset Eichenholz mit Magnet-Messerblock",    "img": "innokoksseteik.jpg"},
            {"name": "Innovation Line Käsemesser Eichenholz",                              "img": "innokaaseik.jpg"},
            {"name": "Innovation Line Käsemesser Graues Pakkaholz",                        "img": "innokaasgrijs.jpg"},
            {"name": "Innovation Line Steakmesser Eichenholz glatte Klinge",               "img": "innosteakeikglad.jpg"},
            {"name": "Innovation Line Steakmesser Eichenholz gezackte Klinge",             "img": "innosteakeik.jpg"},
            {"name": "Innovation Line Steakmesser Graues Pakkaholz glatte Klinge",         "img": "innosteakgrijsglad.jpg"},
        ],
    },
    {
        "slug":         "luxury-line",
        "name":         "Luxury Line",
        "headline":     "Luxury Line – Olivenholz, Eiche & edle Materialien",
        "beschreibung": "Die Luxury Line ist das Herzstück der Laguiole-Kollektion. Edle Griffe aus Olivenholz, Eiche Stonewash oder Rose-Finish – jedes Stück handveredelt und für besondere Anlässe gemacht.",
        "merkmale":     ["Echter Olivenholzgriff", "Eiche Stonewash Finish", "Für besondere Anlässe", "Handveredelt"],
        "hero_img":     "koksolijflag.jpg",
        "produkte": [
            {"name": "Luxury Line Austern-Geschenkset Eichenholz",                        "img": "oestereikgift.jpg"},
            {"name": "Luxury Line Austern-Geschenkset Olivenholz",                        "img": "oesterolivegift.jpg"},
            {"name": "Luxury Line Austern-Geschenkset Wengé Black Stonewash",             "img": "oesterwengegift.jpg"},
            {"name": "Luxury Line BBQ Set Olivenholz",                                    "img": "luxbbqsetolive.jpg"},
            {"name": "Luxury Line Besteckset 16-teilig Olivenholz",                       "img": "couvertolijf16-del.jpg"},
            {"name": "Luxury Line Brotmesser Olivenholz",                                 "img": "broodolijflag.jpg"},
            {"name": "Luxury Line Buttermesser Eiche Stonewash",                          "img": "botereikstone.jpg"},
            {"name": "Luxury Line Buttermesser Olivenholz",                               "img": "boterolijf.jpg"},
            {"name": "Luxury Line Champagnersäbel Olivenholz",                            "img": "sabelolijf.jpg"},
            {"name": "Luxury Line Champagnersäbel Rose",                                  "img": "sabelroos.jpg"},
            {"name": "Luxury Line Charcuterie-Set Olivenholz",                            "img": "luxcharolive.jpg"},
            {"name": "Luxury Line Gabeln Eichenholz Stonewash",                           "img": "luxvorkeikstone.jpg"},
            {"name": "Luxury Line Gabeln Olivenholz",                                     "img": "luxvorkolijf.jpg"},
            {"name": "Luxury Line Gabeln Rose",                                            "img": "luxvorkrose.jpg"},
            {"name": "Luxury Line Gabeln Schwarzes Pakkaholz",                            "img": "luxvorkzwart.jpg"},
            {"name": "Luxury Line Kochmesser Olivenholz",                                 "img": "koksolijflag.jpg"},
            {"name": "Luxury Line Kochmesserset Olivenholz mit Magnet-Messerblock Akazie","img": "koksmessetolijf.jpg"},
            {"name": "Luxury Line Korkenzieher Eiche mit Zubehör",                        "img": "kurkeikgift.jpg"},
            {"name": "Luxury Line Korkenzieher Olivenholz",                               "img": "kurkolijf.jpg"},
            {"name": "Luxury Line Korkenzieher Rose",                                     "img": "kurkroos.jpg"},
            {"name": "Luxury Line Korkenzieher Schwarzes Pakkaholz",                      "img": "kurkzwart.jpg"},
            {"name": "Luxury Line Käsemesserset Eichenholz Stonewash",                    "img": "luxkaaseikstone.jpg"},
            {"name": "Luxury Line Käsemesserset Eichenholz Stonewash V2",                 "img": "luxkaasv2eikstone.jpg"},
            {"name": "Luxury Line Käsemesserset Olivenholz",                              "img": "luxkaasolijf.jpg"},
            {"name": "Luxury Line Käsemesserset Olivenholz V2",                           "img": "luxkaasv2olijf.jpg"},
            {"name": "Luxury Line Löffel Olivenholz",                                     "img": "luxlepelolijf.jpg"},
            {"name": "Luxury Line Löffel Rostfreier Stahl",                               "img": "luxlepelrvs.jpg"},
            {"name": "Luxury Line Mini-Besteckset Olivenholz",                            "img": "luxminicouvol.jpg"},
            {"name": "Luxury Line Santokumesser Olivenholz",                              "img": "santolijflag.jpg"},
            {"name": "Luxury Line Santokumesser Olivenholz mit Schneidebrett",            "img": "santokuolijfplank.jpg"},
            {"name": "Luxury Line Steakmesser Eichenholz Stonewash",                      "img": "luxsteakeikstone.jpg"},
            {"name": "Luxury Line Steakmesser Olivenholz",                                "img": "luxsteakolijf.jpg"},
            {"name": "Luxury Line Steakmesser Rose",                                      "img": "luxsteakrose.jpg"},
            {"name": "Luxury Line Steakmesser Rostfreier Stahl",                          "img": "luxsteakrvs.jpg"},
            {"name": "Luxury Line Steakmesser Schwarzes Pakkaholz",                       "img": "luxsteakzwart.jpg"},
            {"name": "Luxury Line Steakmesser Verschiedene Holzarten",                    "img": "luxsteakmix.jpg"},
            {"name": "Luxury Line Steakmesser Wengé Schwarz",                             "img": "luxsteakwengezw.jpg"},
            {"name": "Luxury Line Taschenmesser Ahornholz",                               "img": "zakmesdoorn.jpg"},
            {"name": "Luxury Line Taschenmesser Rose",                                    "img": "zakmroos.jpg"},
            {"name": "Luxury Line Taschenmesser Rose mit Lederhülle",                     "img": "zakmleerroos.jpg"},
            {"name": "Luxury Line Taschenmesser Schwarzes Pakkaholz",                     "img": "zakmzwart.jpg"},
            {"name": "Luxury Line Taschenmesser Zebranoholz mit Lederhülle",              "img": "zakmleerzebrano.jpg"},
            {"name": "Luxury Line Taschenmesser mit Korkenzieher Olivenholz",             "img": "zakmkurkolijf.jpg"},
            {"name": "Luxury Line Taschenmesser-Bausatz",                                 "img": "maaklagzakm.jpg"},
            {"name": "Luxury Line The Exclusive Edition",                                  "img": "champcavoystoak.jpg"},
        ],
    },
    {
        "slug":         "premium-line",
        "name":         "Premium Line",
        "headline":     "Premium Line – Elegantes Schwarz für den modernen Tisch",
        "beschreibung": "Die Premium Line setzt auf konsequentes Schwarz. Black Stonewash, Dark Wood, Perlmutt oder Treasure – ein elegantes Tischbild für alle, die klare Kontraste und modernes Design lieben.",
        "merkmale":     ["Schwarzes Design-Statement", "6 Farb-/Materialvarianten", "Komplette Tischausstattung", "Für Restaurant & Zuhause"],
        "hero_img":     "1_8premblackstone.jpg",
        "produkte": [
            {"name": "Premium Line Pizzaschneider mit Servierbrett Akazie",               "img": "prempizzazw.jpg"},
            {"name": "Premium Line 12-teiliges Mini-Besteckset Schwarz",                  "img": "prminicouvzw.jpg"},
            {"name": "Premium Line 3-teiliges Küchenmesser-Set Schwarz",                  "img": "pressentknzw3pcs.png"},
            {"name": "Premium Line 3-teiliges Reiben-Set",                                "img": "prrasp3delzwgift.jpg"},
            {"name": "Premium Line 5 Käsemesser Schwarz mit Servierbrett",                "img": "kaas5zwartplank.jpg"},
            {"name": "Premium Line 8 Käsemesser Schwarz mit Servierbrett",                "img": "kaas8zwartplank.jpg"},
            {"name": "Premium Line Santoku Käsemesser mit Akazienholz-Brett",             "img": "santplankacazw.jpg"},
            {"name": "Premium Line Amuse-Bouche Löffel Schwarz 6 Stück",                  "img": "pramusezw.jpg"},
            {"name": "Premium Line Besteckset 24-teilig Rostfreier Stahl",                "img": "prcouvrvs.jpg"},
            {"name": "Premium Line Besteckset 24-teilig Schwarz",                         "img": "prcouvzwart.jpg"},
            {"name": "Premium Line Brotmesser Schwarz",                                   "img": "broodzwart.jpg"},
            {"name": "Premium Line Brotmesser Schwarz mit Baguette-Schneidebrett",        "img": "broodplankzwart.jpg"},
            {"name": "Premium Line Buttermesser Black Stonewash",                         "img": "botermesblackstone.jpg"},
            {"name": "Premium Line Buttermesser Dark Wood",                               "img": "botermesdarkwood.jpg"},
            {"name": "Premium Line Buttermesser Perlmutt",                                "img": "botermesparel.jpg"},
            {"name": "Premium Line Buttermesser Rostfreier Stahl",                        "img": "botermesrvs.jpg"},
            {"name": "Premium Line Buttermesser Schwarz",                                 "img": "botermeszwart.jpg"},
            {"name": "Premium Line Buttermesser Treasure",                                "img": "botermestreasure.jpg"},
            {"name": "Premium Line Gabeln Rostfreier Stahl 1.8 mm",                       "img": "prvorkrvs.jpg"},
            {"name": "Premium Line Gabeln Schwarz 1.8 mm",                                "img": "prvorkzwart.jpg"},
            {"name": "Premium Line Kuchengabeln Schwarz",                                 "img": "taartvorkzwart.jpg"},
            {"name": "Premium Line Käsemesser Black Stonewash",                           "img": "kaasblackstone1st.jpg"},
            {"name": "Premium Line Käsemesser Schwarz",                                   "img": "kaaszwart1st.jpg"},
            {"name": "Premium Line Käsemesserset 3-teilig Black Stonewash",               "img": "kaasblackstone3del.jpg"},
            {"name": "Premium Line Käsemesserset 3-teilig Dark Wood",                     "img": "kaasdarkwood3del.jpg"},
            {"name": "Premium Line Käsemesserset 3-teilig Perlmutt",                      "img": "kaasparel3del.jpg"},
            {"name": "Premium Line Käsemesserset 3-teilig Rostfreier Stahl",              "img": "kaasrvs3del.jpg"},
            {"name": "Premium Line Käsemesserset 3-teilig Schwarz",                       "img": "kaaszwart3del.jpg"},
            {"name": "Premium Line Käsemesserset 3-teilig Treasure",                      "img": "kaastreasure3del.jpg"},
            {"name": "Premium Line Käseschneider & Käsereibe Schwarz",                    "img": "premschaafraspzwart.jpg"},
            {"name": "Premium Line Mini-Löffel Schwarz",                                  "img": "prminispoonzw.jpg"},
            {"name": "Premium Line Pinchos Schwarz",                                      "img": "pinchozwartabs.jpg"},
            {"name": "Premium Line Pizzaschneider Schwarz",                               "img": "prpizzasnijder.jpg"},
            {"name": "Premium Line Reibe Extra Grob Schwarz",                             "img": "prraspexcoarsezw.png"},
            {"name": "Premium Line Reibe Fein Schwarz",                                   "img": "prraspfinezw.png"},
            {"name": "Premium Line Reibe Ribbon Schwarz",                                 "img": "prraspribbonzw.png"},
            {"name": "Premium Line Reibe Zester Schwarz",                                 "img": "prraspzestzw.png"},
            {"name": "Premium Line Steakmesser Black Stonewash 1.8 mm",                   "img": "1_8premblackstone.jpg"},
            {"name": "Premium Line Steakmesser Dark Wood 1.8 mm",                         "img": "1_8premdarkwood.jpg"},
            {"name": "Premium Line Steakmesser Perlmutt 1.8 mm",                          "img": "1_8premparel.jpg"},
            {"name": "Premium Line Steakmesser Rostfreier Stahl 1.8 mm",                  "img": "1_8premrvs.jpg"},
            {"name": "Premium Line Steakmesser Schwarz 1.8 mm",                           "img": "1_8premzwart.jpg"},
            {"name": "Premium Line Steakmesser Treasure 1.8 mm",                          "img": "1_8premtreasure.jpg"},
            {"name": "Premium Line Steakmesser Wood 1.8 mm",                              "img": "1_8premwood.jpg"},
            {"name": "Premium Line Wurstteller Akazienholz mit Schwarzem Messer",         "img": "worstplankaca.jpg"},
        ],
    },
    {
        "slug":         "prestige-line",
        "name":         "Prestige Line",
        "headline":     "Prestige Line – Gold & Copper Stonewash für besondere Anlässe",
        "beschreibung": "Die Prestige Line ist die exklusivste Laguiole-Kollektion. Gold Stonewash oder Copper Stonewash – ein luxuriöser Glanz für Feierlichkeiten, Geschenke und den perfekt gedeckten Tisch.",
        "merkmale":     ["Gold & Copper Stonewash Finish", "Geschenkverpackung", "Exklusivste Linie", "Perfekt als Geschenk"],
        "hero_img":     "pressteakgoudzw.jpg",
        "produkte": [
            {"name": "Prestige Line Buttermesser Copper Stonewash",            "img": "presboterkopzw.jpg"},
            {"name": "Prestige Line Buttermesser Gold Stonewash",              "img": "presbotergoudzw.jpg"},
            {"name": "Prestige Line Käsemesserset 3-teilig Copper Stonewash",  "img": "preskaaskopzw3.jpg"},
            {"name": "Prestige Line Käsemesserset 3-teilig Gold Stonewash",    "img": "preskaasgoudzw3.jpg"},
            {"name": "Prestige Line Steakmesser Copper Stonewash",             "img": "pressteakkopzw.jpg"},
            {"name": "Prestige Line Steakmesser Gold Stonewash",               "img": "pressteakgoudzw.jpg"},
        ],
    },
]

SDV_PRODUKTE = {
    "slug":       "style-de-vie",
    "name":       "Style de Vie",
    "headline":   "Style de Vie – Messerblöcke, Schneidebretter & Tafelkultur",
    "beschreibung": "Die Style de Vie Eigenmarke verbindet Funktion mit nordischem Design. Magnetische Messerblöcke aus Eiche und Walnuss, Schneidbretter aus Akazienholz und handgemachte Keramik-Ölschalen für den gedeckten Tisch.",
    "merkmale":  ["Magnetische Messerblöcke", "Akazienholz-Schneidebretter", "Keramik-Olivenölschalen", "Nordisches Design"],
    "hero_img":  "magnstanoak.jpg",
    "img_dir":   "img/style-de-vie",
    "html_dir":  "tischkultur-servieren/style-de-vie",
    "breadcrumb_parent": ("Tischkultur", "/tischkultur-servieren/"),
    "produkte": [
        {"name": "2 Keramik Olivenöl-Schälchen",                                        "img": "olijfdipschaal2.jpg"},
        {"name": "6-teiliges Käse- und Buttermesserset Schwarz",                         "img": "sdvcheese6black.jpg"},
        {"name": "6-teiliges Käse- und Buttermesserset Gold",                            "img": "sdvcheese6gold.jpg"},
        {"name": "6-teiliges Käse- und Buttermesserset Stahl",                           "img": "sdvcheese6steel.jpg"},
        {"name": "Keramik Olivenöl-Schale",                                              "img": "olijfdipschaal.jpg"},
        {"name": "Keramik Olivenöl-Schale Baum",                                         "img": "olijfdipboom.jpg"},
        {"name": "Keramik Olivenöl-, Butter- und Gewürzschale 3-teilig",                 "img": "olijfdip3del.png"},
        {"name": "Magnetischer Messerblock Eiche auf Natursteinfuß",                     "img": "magneiksteen.png"},
        {"name": "Magnetischer Messerblock Walnuss auf Natursteinfuß",                   "img": "magnwalsteen.png"},
        {"name": "Magnetischer Messerblock Eichenholz",                                  "img": "magnstanoak.jpg"},
        {"name": "Magnetische Messerleiste 50 cm Akazie",                                "img": "magnacacia50cm.jpg"},
        {"name": "Magnetische Messerleiste 50 cm Eiche",                                 "img": "magneik50cm.jpg"},
        {"name": "Magnetische Messerleiste 50 cm Walnuss",                               "img": "magnwalnoot50cm.jpg"},
        {"name": "Magnetische Messerleiste Natur Akazie",                                "img": "magnnatuuraca.jpg"},
        {"name": "Schneidebrett Natur Akazie Large",                                     "img": "snijnatacal.jpg"},
        {"name": "Schneidebrett Natur Akazie Medium",                                    "img": "snijnatacam.jpg"},
    ],
}

PLATEIT_PRODUKTE = {
    "slug":       "plate-it",
    "name":       "Plate-it",
    "headline":   "Plate-it – Professionelles Anrichten & Dekorieren",
    "beschreibung": "Plate-it ist das Werkzeug für alle, die Gerichte wie Profi-Köche anrichten möchten. Quenelle-Löffel, Garnierspritzen, Schablonen, Formen und Dekorationspinsel – alles für das perfekte Food-Styling.",
    "merkmale":   ["Profi-Anrichtwerkzeug", "Für Hobbyköche & Profis", "Spülmaschinenfest", "Komplett-Sets"],
    "hero_img":   "piquenelless.png",
    "img_dir":    "img/plate-it",
    "html_dir":   "tischkultur-servieren/plate-it",
    "breadcrumb_parent": ("Tischkultur", "/tischkultur-servieren/"),
    "produkte": [
        {"name": "Buñuelos Formen Flower Power 2-teilig",    "img": "pibunflowpow.png"},
        {"name": "Buñuelos Formen Tartelettes 2-teilig",     "img": "pibuntart.png"},
        {"name": "Buñuelos Formen Under the Sea 2-teilig",   "img": "pibunsea.png"},
        {"name": "Buñuelos Griff",                           "img": "pibunhandle.png"},
        {"name": "Buñuelos Rosetten 3-teilig",               "img": "pibunuelos3.png"},
        {"name": "Dekorationspinsel 2-teilig",               "img": "pibrush2.png"},
        {"name": "Dekorationspinzette 2-teilig",             "img": "pitweezers2.png"},
        {"name": "Dekorationssieb 8 cm",                     "img": "pidecosieve8.png"},
        {"name": "Dekorierlöffel 2-teilig",                  "img": "pidecspoons2.jpg"},
        {"name": "Formen Circle 3-teilig",                   "img": "pimoldscircle.png"},
        {"name": "Formen Infinity 3-teilig",                 "img": "pimoldsinfinity.png"},
        {"name": "Formen Love At First Bite 3-teilig",       "img": "pimoldslove.png"},
        {"name": "Formen Wood 3-teilig",                     "img": "pimoldswood.png"},
        {"name": "Garnierflaschen 3-teilig 220 ml",          "img": "pibottles220.jpg"},
        {"name": "Garnier Squeeze-Flaschen 2-teilig 500 ml", "img": "pibottles500.png"},
        {"name": "Garnierringe 4-teilig",                    "img": "pigarnrings4.jpg"},
        {"name": "Garnierringe Hexagon 4-teilig + Stößel",   "img": "pigarnhexa4.jpg"},
        {"name": "Offset-Spachtel 3-teilig",                 "img": "pispat3.png"},
        {"name": "Plattenteller Glas 30 cm",                 "img": "piturntable.png"},
        {"name": "Quenelle-Löffel Large 2-teilig",           "img": "piquenellesl.png"},
        {"name": "Quenelle-Löffel Small 2-teilig",           "img": "piquenelless.png"},
        {"name": "Schaber Vol.1 3-teilig",                   "img": "piscrapervol1.png"},
        {"name": "Spritzbeutelhalter inkl. Zubehör",         "img": "pinozzle11.png"},
        {"name": "Teller-Schablonen Hexagon 6-teilig",       "img": "pistenhexa6.png"},
    ],
}

# ─── Gemeinsame HTML-Bausteine ────────────────────────────────────────────────

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
      <p>Diese Website verwendet Cookies und Analyse-Tools. <a href="/datenschutz/">Datenschutz</a></p>
      <div class="cookie-actions">
        <button class="btn btn-primary" id="cookieAccept">Akzeptieren</button>
        <button class="btn" id="cookieDecline" style="background:transparent;border:1px solid rgba(255,255,255,0.3);color:var(--weiss);">Ablehnen</button>
      </div>
    </div>
  </div>
  <script src="/js/main.js" defer></script>"""

GRID_CSS = """  <style>
    .produkte-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(190px,1fr)); gap:20px; }
    .produkt-karte { background:var(--weiss);border-radius:4px;box-shadow:0 2px 8px rgba(0,0,0,.06);overflow:hidden;transition:transform .25s,box-shadow .25s; }
    .produkt-karte:hover { transform:translateY(-4px);box-shadow:0 8px 24px rgba(0,0,0,.1); }
    .produkt-img { width:100%;aspect-ratio:1/1;object-fit:contain;background:var(--creme);padding:12px;display:block; }
    .produkt-body { padding:12px 16px 16px; }
    .produkt-body h3 { font-family:var(--font-serif);font-size:14px;margin:0 0 10px;color:var(--anthrazit);line-height:1.4; }
  </style>"""

# ─── Download ────────────────────────────────────────────────────────────────

def download(url: str, dest: Path, dry_run: bool) -> bool:
    if dest.exists():
        print(f"  ✓ {dest.name}"); return True
    if dry_run:
        print(f"  [dry] {dest.name}"); return True
    print(f"  ↓ {dest.name}")
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=20) as r:
            data = r.read()
        if len(data) < 300:
            print(f"    ✗ Zu klein ({len(data)} B)"); return False
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        print(f"    → {len(data)//1024} KB"); return True
    except Exception as e:
        print(f"    ✗ {e}"); return False

# ─── HTML: Produktkarten ──────────────────────────────────────────────────────

def product_cards(produkte: list, img_subdir: str) -> str:
    html = ""
    for p in produkte:
        fname = Path(p["img"]).stem + Path(p["img"]).suffix
        img_src = f"/{img_subdir}/{fname}"
        html += f"""
      <div class="produkt-karte">
        <img src="/img/ui/placeholder.png" data-src="{img_src}" alt="{p['name']} kaufen Würzburg" class="produkt-img" loading="lazy">
        <div class="produkt-body">
          <h3>{p['name']}</h3>
          <a href="/kontakt/" class="btn btn-primary" style="font-size:12px;padding:7px 14px;">Preis anfragen</a>
        </div>
      </div>"""
    return html

def merkmale_html(lst: list) -> str:
    return "".join(
        f'<li style="padding:8px 0;border-bottom:1px solid var(--creme);color:var(--grau-mid);font-size:14px;">✓ {m}</li>'
        for m in lst
    )

# ─── HTML: Laguiole Serienunterseite ─────────────────────────────────────────

def laguiole_serie_page(serie: dict) -> str:
    n     = len(serie["produkte"])
    cards = product_cards(serie["produkte"], "img/laguiole")
    return f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Laguiole {serie['name']} kaufen Würzburg – {n} Produkte | Feuerhaus Kalina</title>
  <meta name="description" content="Laguiole Style de Vie {serie['name']} kaufen in Rimpar bei Würzburg. {n} Produkte: edles Tafelbesteck, Steakmesser, Käsemesser. Autorisierter Händler.">
  <link rel="canonical" href="https://grills.feuerhaus-kalina.de/tischkultur-servieren/laguiole/{serie['slug']}/">
  <link rel="icon" type="image/x-icon" href="/img/ui/favicon.ico">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/css/style.css">
  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
    {{"@type":"ListItem","position":1,"name":"Startseite","item":"https://grills.feuerhaus-kalina.de/"}},
    {{"@type":"ListItem","position":2,"name":"Tischkultur","item":"https://grills.feuerhaus-kalina.de/tischkultur-servieren/"}},
    {{"@type":"ListItem","position":3,"name":"Laguiole","item":"https://grills.feuerhaus-kalina.de/tischkultur-servieren/laguiole/"}},
    {{"@type":"ListItem","position":4,"name":"{serie['name']}","item":"https://grills.feuerhaus-kalina.de/tischkultur-servieren/laguiole/{serie['slug']}/"}}
  ]}}</script>
{GRID_CSS}
</head>
<body>
{NAV}
  <div class="breadcrumbs"><div class="breadcrumbs-inner container">
    <a href="/">Startseite</a><span>›</span>
    <a href="/tischkultur-servieren/">Tischkultur</a><span>›</span>
    <a href="/tischkultur-servieren/laguiole/">Laguiole</a><span>›</span>
    <span>{serie['name']}</span>
  </div></div>

  <section class="page-hero">
    <div class="page-hero-inner container">
      <span class="eyebrow">Laguiole Style de Vie</span>
      <h1>{serie['headline']}</h1>
      <p>{serie['beschreibung']}</p>
    </div>
  </section>

  <section class="section-padding" style="background:var(--creme);">
    <div class="container">
      <div style="display:grid;grid-template-columns:2fr 1fr;gap:48px;align-items:start;">
        <div>
          <h2 style="font-family:var(--font-serif);font-size:clamp(20px,2vw,28px);margin:0 0 28px;color:var(--anthrazit);">{n} Produkte – {serie['name']}</h2>
          <div class="produkte-grid">{cards}</div>
        </div>
        <div style="position:sticky;top:100px;">
          <div style="background:var(--weiss);border-radius:4px;padding:28px;">
            <span class="eyebrow">Merkmale</span>
            <h3 style="font-family:var(--font-serif);font-size:18px;margin:10px 0 16px;color:var(--anthrazit);">{serie['name']}</h3>
            <ul style="list-style:none;padding:0;margin:0 0 24px;">{merkmale_html(serie['merkmale'])}</ul>
            <a href="/tischkultur-servieren/laguiole/" style="color:var(--grau-mid);font-size:13px;display:block;margin-bottom:14px;">← Alle Laguiole-Serien</a>
            <a href="/kontakt/" class="btn btn-primary" style="display:block;text-align:center;">Beratung anfragen</a>
          </div>
        </div>
      </div>
    </div>
  </section>

  <section class="beratungs-block">
    <div class="beratungs-inner container">
      <div>
        <span class="eyebrow">Laguiole live erleben</span>
        <h2>Elegantes Tafelbesteck in unserer Ausstellung</h2>
        <p>Besteck hält man in der Hand – Fotos reichen nicht. Kommen Sie in unsere Ausstellung nach Rimpar und erleben Sie die {serie['name']} direkt.</p>
      </div>
      <div style="display:flex;gap:16px;flex-wrap:wrap;">
        <a href="/kontakt/" class="btn btn-primary">Termin vereinbaren</a>
        <a href="/tischkultur-servieren/laguiole/" class="btn" style="background:transparent;border:1px solid rgba(255,255,255,0.4);color:var(--weiss);">Alle Laguiole-Serien</a>
      </div>
    </div>
  </section>
{FOOTER}
</body></html>"""

# ─── HTML: Laguiole Übersichtsseite ──────────────────────────────────────────

def laguiole_index_page() -> str:
    total = sum(len(s["produkte"]) for s in LAGUIOLE_SERIEN)
    cards = ""
    for s in LAGUIOLE_SERIEN:
        n = len(s["produkte"])
        img = f"/img/laguiole/{s['hero_img']}"
        cards += f"""
      <a href="/tischkultur-servieren/laguiole/{s['slug']}/" style="display:block;background:var(--weiss);border-radius:4px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.06);text-decoration:none;transition:transform .25s,box-shadow .25s;" onmouseover="this.style.transform='translateY(-4px)';this.style.boxShadow='0 8px 24px rgba(0,0,0,.12)'" onmouseout="this.style.transform='';this.style.boxShadow='0 2px 8px rgba(0,0,0,.06)'">
        <img src="/img/ui/placeholder.png" data-src="{img}" alt="Laguiole {s['name']} kaufen Würzburg" loading="lazy" style="width:100%;aspect-ratio:4/3;object-fit:contain;background:var(--creme);padding:20px;">
        <div style="padding:18px 22px 22px;">
          <span style="font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--rot);font-weight:600;">{n} Produkte</span>
          <h2 style="font-family:var(--font-serif);font-size:20px;margin:6px 0 8px;color:var(--anthrazit);">{s['name']}</h2>
          <p style="color:var(--grau-mid);font-size:13px;line-height:1.6;margin:0 0 12px;">{s['beschreibung'][:100]}…</p>
          <span style="color:var(--rot);font-size:13px;font-weight:600;">Zur Serie →</span>
        </div>
      </a>"""

    return f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Laguiole Style de Vie kaufen Würzburg – Tafelbesteck & Messer | Feuerhaus Kalina</title>
  <meta name="description" content="Laguiole Style de Vie Tafelbesteck und Messer kaufen in Rimpar bei Würzburg. {total} Produkte in 4 Serien: Innovation, Luxury, Premium, Prestige. Autorisierter Händler.">
  <link rel="canonical" href="https://grills.feuerhaus-kalina.de/tischkultur-servieren/laguiole/">
  <link rel="icon" type="image/x-icon" href="/img/ui/favicon.ico">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/css/style.css">
  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
    {{"@type":"ListItem","position":1,"name":"Startseite","item":"https://grills.feuerhaus-kalina.de/"}},
    {{"@type":"ListItem","position":2,"name":"Tischkultur","item":"https://grills.feuerhaus-kalina.de/tischkultur-servieren/"}},
    {{"@type":"ListItem","position":3,"name":"Laguiole","item":"https://grills.feuerhaus-kalina.de/tischkultur-servieren/laguiole/"}}
  ]}}</script>
</head>
<body>
{NAV}
  <div class="breadcrumbs"><div class="breadcrumbs-inner container">
    <a href="/">Startseite</a><span>›</span>
    <a href="/tischkultur-servieren/">Tischkultur</a><span>›</span>
    <span>Laguiole Style de Vie</span>
  </div></div>

  <section class="page-hero">
    <div class="page-hero-inner container">
      <span class="eyebrow">Tafelbesteck &amp; Messer</span>
      <h1>Laguiole Style de Vie – Eleganz aus dem Massif Central</h1>
      <p>Laguiole ist mehr als ein Messer – es ist ein Kulturgut aus dem französischen Aubrac. {total} Produkte in 4 Serien: von modernem Pakkaholz der Innovation Line bis zum luxuriösen Gold Stonewash der Prestige Line. Autorisierter Händler in Rimpar bei Würzburg.</p>
    </div>
  </section>

  <section class="section-padding" style="background:var(--creme);">
    <div class="container">
      <div style="text-align:center;margin-bottom:48px;">
        <span class="eyebrow">4 Serien</span>
        <h2 style="font-family:var(--font-serif);font-size:clamp(22px,2.5vw,34px);margin:12px 0 14px;color:var(--anthrazit);">Wählen Sie Ihre Laguiole-Serie</h2>
        <p style="color:var(--grau-mid);max-width:520px;margin:0 auto;font-size:15px;line-height:1.7;">Jede Serie hat ihre eigene Ästhetik und ihren eigenen Anlass. Von alltagstauglich bis festlich-exklusiv.</p>
      </div>
      <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:24px;">{cards}</div>
    </div>
  </section>

  <section style="background:var(--anthrazit);padding:80px 0;">
    <div class="container" style="max-width:700px;text-align:center;">
      <span class="eyebrow" style="color:var(--rot);">Seit 1829</span>
      <h2 style="font-family:var(--font-serif);font-size:clamp(22px,2.5vw,34px);color:var(--weiss);margin:16px 0 20px;">"Das Laguiole ist kein Messer. Es ist ein Begleiter."</h2>
      <p style="color:rgba(255,255,255,0.7);line-height:1.8;font-size:15px;">Laguiole-Messer tragen das Wappen der Stadt Laguiole – einer kleinen Stadt in Südfrankreich, wo das Messer seit fast 200 Jahren hergestellt wird. Jedes Stück ist handgefertigt und einzigartig.</p>
    </div>
  </section>

  <section class="beratungs-block">
    <div class="beratungs-inner container">
      <div>
        <span class="eyebrow">Persönliche Beratung</span>
        <h2>Laguiole in unserer Ausstellung</h2>
        <p>Besteck und Messer muss man anfassen. Kommen Sie in unsere Ausstellung nach Rimpar – wir zeigen Ihnen alle 4 Laguiole-Serien und beraten Sie bei der Auswahl.</p>
      </div>
      <div style="display:flex;gap:16px;flex-wrap:wrap;">
        <a href="/kontakt/" class="btn btn-primary">Termin vereinbaren</a>
        <a href="/tischkultur-servieren/" class="btn" style="background:transparent;border:1px solid rgba(255,255,255,0.4);color:var(--weiss);">Alle Tischkultur</a>
      </div>
    </div>
  </section>
{FOOTER}
</body></html>"""

# ─── HTML: Einfache Produktseite (SDV & Plate-it) ────────────────────────────

def simple_product_page(brand: dict) -> str:
    n     = len(brand["produkte"])
    slug  = brand["slug"]
    name  = brand["name"]
    img_d = brand["img_dir"]
    bc_name, bc_url = brand["breadcrumb_parent"]
    cards = product_cards(brand["produkte"], img_d)

    return f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{name} kaufen Würzburg – {n} Produkte | Feuerhaus Kalina</title>
  <meta name="description" content="{name} kaufen in Rimpar bei Würzburg. {n} Produkte. {brand['beschreibung'][:100]}">
  <link rel="canonical" href="https://grills.feuerhaus-kalina.de/tischkultur-servieren/{slug}/">
  <link rel="icon" type="image/x-icon" href="/img/ui/favicon.ico">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/css/style.css">
{GRID_CSS}
</head>
<body>
{NAV}
  <div class="breadcrumbs"><div class="breadcrumbs-inner container">
    <a href="/">Startseite</a><span>›</span>
    <a href="{bc_url}">{bc_name}</a><span>›</span>
    <span>{name}</span>
  </div></div>

  <section class="page-hero">
    <div class="page-hero-inner container">
      <span class="eyebrow">Tischkultur &amp; Servieren</span>
      <h1>{brand['headline']}</h1>
      <p>{brand['beschreibung']}</p>
    </div>
  </section>

  <section class="section-padding" style="background:var(--creme);">
    <div class="container">
      <div style="display:grid;grid-template-columns:2fr 1fr;gap:48px;align-items:start;">
        <div>
          <h2 style="font-family:var(--font-serif);font-size:clamp(20px,2vw,28px);margin:0 0 28px;color:var(--anthrazit);">{n} Produkte</h2>
          <div class="produkte-grid">{cards}</div>
        </div>
        <div style="position:sticky;top:100px;">
          <div style="background:var(--weiss);border-radius:4px;padding:28px;">
            <span class="eyebrow">Merkmale</span>
            <h3 style="font-family:var(--font-serif);font-size:18px;margin:10px 0 16px;color:var(--anthrazit);">{name}</h3>
            <ul style="list-style:none;padding:0;margin:0 0 24px;">{merkmale_html(brand['merkmale'])}</ul>
            <a href="/kontakt/" class="btn btn-primary" style="display:block;text-align:center;">Beratung anfragen</a>
          </div>
        </div>
      </div>
    </div>
  </section>

  <section class="beratungs-block">
    <div class="beratungs-inner container">
      <div>
        <span class="eyebrow">Persönliche Beratung</span>
        <h2>{name} in unserer Ausstellung</h2>
        <p>Kommen Sie in unsere Ausstellung nach Rimpar – wir zeigen Ihnen alle {name}-Produkte und beraten Sie persönlich.</p>
      </div>
      <div style="display:flex;gap:16px;flex-wrap:wrap;">
        <a href="/kontakt/" class="btn btn-primary">Termin vereinbaren</a>
        <a href="/tischkultur-servieren/" class="btn" style="background:transparent;border:1px solid rgba(255,255,255,0.4);color:var(--weiss);">Alle Tischkultur</a>
      </div>
    </div>
  </section>
{FOOTER}
</body></html>"""

# ─── Hauptprogramm ────────────────────────────────────────────────────────────

def main():
    dry_run   = "--dry-run"   in sys.argv
    html_only = "--html-only" in sys.argv
    no_html   = "--no-html"   in sys.argv

    print("Style de Vie Produkt-Scraper & HTML-Generator")
    print("=" * 60)

    dl = sk = fa = 0

    # ── Laguiole ──────────────────────────────────────────────────────────────
    laguiole_img_dir = BASE_DIR / "img" / "laguiole"
    if not html_only:
        laguiole_img_dir.mkdir(parents=True, exist_ok=True)
        print(f"\n── Laguiole Style de Vie ({sum(len(s['produkte']) for s in LAGUIOLE_SERIEN)} Produkte) ──")
        for serie in LAGUIOLE_SERIEN:
            print(f"\n  Serie: {serie['name']} ({len(serie['produkte'])} Produkte)")
            for p in serie["produkte"]:
                url  = f"{SDV_BASE}/content/products/{p['img']}{IMG_PARAMS}"
                dest = laguiole_img_dir / p["img"]
                ok   = download(url, dest, dry_run)
                if ok and not dest.exists() and not dry_run: dl += 1
                elif dest.exists(): sk += 1
                elif not dry_run: fa += 1
                if not dry_run and not dest.exists(): time.sleep(DELAY)

    # ── Style de Vie Brand ────────────────────────────────────────────────────
    sdv_img_dir = BASE_DIR / "img" / "style-de-vie"
    if not html_only:
        sdv_img_dir.mkdir(parents=True, exist_ok=True)
        print(f"\n── Style de Vie Brand ({len(SDV_PRODUKTE['produkte'])} Produkte) ──")
        for p in SDV_PRODUKTE["produkte"]:
            url  = f"{SDV_BASE}/content/products/{p['img']}{IMG_PARAMS}"
            dest = sdv_img_dir / p["img"]
            ok   = download(url, dest, dry_run)
            if not dry_run and not dest.exists(): time.sleep(DELAY)

    # ── Plate-it ──────────────────────────────────────────────────────────────
    plateit_img_dir = BASE_DIR / "img" / "plate-it"
    if not html_only:
        plateit_img_dir.mkdir(parents=True, exist_ok=True)
        print(f"\n── Plate-it ({len(PLATEIT_PRODUKTE['produkte'])} Produkte) ──")
        for p in PLATEIT_PRODUKTE["produkte"]:
            url  = f"{SDV_BASE}/content/products/{p['img']}{IMG_PARAMS}"
            dest = plateit_img_dir / p["img"]
            ok   = download(url, dest, dry_run)
            if not dry_run and not dest.exists(): time.sleep(DELAY)

    # ── HTML ─────────────────────────────────────────────────────────────────
    if not no_html and not dry_run:
        print("\nGeneriere HTML-Seiten...")

        # Laguiole Index
        lag_dir = BASE_DIR / "tischkultur-servieren" / "laguiole"
        lag_dir.mkdir(parents=True, exist_ok=True)
        (lag_dir / "index.html").write_text(laguiole_index_page(), encoding="utf-8")
        print("  ✓ tischkultur-servieren/laguiole/index.html")

        # Laguiole Serienunterseiten
        for serie in LAGUIOLE_SERIEN:
            sd = lag_dir / serie["slug"]
            sd.mkdir(parents=True, exist_ok=True)
            (sd / "index.html").write_text(laguiole_serie_page(serie), encoding="utf-8")
            print(f"  ✓ tischkultur-servieren/laguiole/{serie['slug']}/index.html")

        # Style de Vie Brand
        sdv_dir = BASE_DIR / "tischkultur-servieren" / "style-de-vie"
        sdv_dir.mkdir(parents=True, exist_ok=True)
        (sdv_dir / "index.html").write_text(simple_product_page(SDV_PRODUKTE), encoding="utf-8")
        print("  ✓ tischkultur-servieren/style-de-vie/index.html")

        # Plate-it
        pi_dir = BASE_DIR / "tischkultur-servieren" / "plate-it"
        pi_dir.mkdir(parents=True, exist_ok=True)
        (pi_dir / "index.html").write_text(simple_product_page(PLATEIT_PRODUKTE), encoding="utf-8")
        print("  ✓ tischkultur-servieren/plate-it/index.html")

        # JSON
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        alle = []
        for s in LAGUIOLE_SERIEN:
            for p in s["produkte"]:
                alle.append({"marke":"Laguiole","serie":s["name"],"name":p["name"],"img":f"img/laguiole/{p['img']}"})
        for p in SDV_PRODUKTE["produkte"]:
            alle.append({"marke":"Style de Vie","serie":"","name":p["name"],"img":f"img/style-de-vie/{p['img']}"})
        for p in PLATEIT_PRODUKTE["produkte"]:
            alle.append({"marke":"Plate-it","serie":"","name":p["name"],"img":f"img/plate-it/{p['img']}"})
        (DATA_DIR / "styledevie-produkte.json").write_text(
            json.dumps(alle, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print("  ✓ data/styledevie-produkte.json")

    # ── Zusammenfassung ───────────────────────────────────────────────────────
    lag_total = sum(len(s["produkte"]) for s in LAGUIOLE_SERIEN)
    total = lag_total + len(SDV_PRODUKTE["produkte"]) + len(PLATEIT_PRODUKTE["produkte"])
    print(f"\n{'='*60}\nFERTIG\n{'='*60}")
    print(f"  Laguiole:      {lag_total} Produkte in {len(LAGUIOLE_SERIEN)} Serien")
    print(f"  Style de Vie:  {len(SDV_PRODUKTE['produkte'])} Produkte")
    print(f"  Plate-it:      {len(PLATEIT_PRODUKTE['produkte'])} Produkte")
    print(f"  Gesamt:        {total} Produkte")
    if not no_html and not dry_run:
        print(f"  HTML-Seiten:   {len(LAGUIOLE_SERIEN) + 3}")
    print("="*60)

if __name__ == "__main__":
    main()
