#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
"""
Bild-Download-Skript – Grillwelt Feuerhaus Kalina
===================================================
Scannt alle HTML-Seiten nach Bildreferenzen, prüft welche lokal fehlen
und lädt fehlende Bilder von den konfigurierten Quell-URLs herunter.

Verwendung:
  python download-images.py           # Nur prüfen + fehlende auflisten
  python download-images.py --download # Fehlende Bilder herunterladen
  python download-images.py --all      # Alle Bilder neu herunterladen (überschreiben)
"""

import os
import sys
import re
import time
import urllib.request
import urllib.error
from pathlib import Path

# ─── Konfiguration ───────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).parent
IMG_DIR  = BASE_DIR / "img"

# User-Agent für Downloads (manche Server blockieren Python-Standard-UA)
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
    "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
    "Referer": "https://grills.feuerhaus-kalina.de/",
}

# Pause zwischen Downloads (Sekunden) – Server-freundlich
DOWNLOAD_DELAY = 0.8

# ─── URL-Mapping: lokaler Pfad → Download-URL ────────────────────────────────
# Format: "img/hersteller/dateiname.ext": "https://..."
#
# Quellen aus der vorherigen Session (Shopify-CDNs + Hersteller-Websites).
# Fehlende Einträge → Skript meldet "Keine Quelle konfiguriert".

URL_MAP = {

    # ── Kamado Joe ────────────────────────────────────────────────────────────
    "img/hersteller/kamado-joe-classic-iii-keramikgrill-kaufen-wuerzburg.webp": (
        "https://www.kamadojoe.com/cdn/shop/files/KJ-ClassicIII-US-2023_1200x.jpg"
    ),
    "img/hersteller/kamado-joe-big-joe-iii-kamado-grill-rimpar.jpg": (
        "https://www.kamadojoe.com/cdn/shop/files/KJ-BigJoeIII-US-2023_1200x.jpg"
    ),

    # ── Masterbuilt ───────────────────────────────────────────────────────────
    "img/hersteller/masterbuilt-gravity-series-800-holzkohlegrill-digital.webp": (
        "https://masterbuilt.com/cdn/shop/products/20010112_GravitySeries800_Lifestyle_0001_1200x.jpg"
    ),
    "img/hersteller/masterbuilt-gravity-series-1050-smoker-grill-wuerzburg.webp": (
        "https://masterbuilt.com/cdn/shop/products/20010512_GravitySeries1050_Lifestyle_0002_1200x.jpg"
    ),

    # ── CB Outdoor Kitchen ────────────────────────────────────────────────────
    "img/hersteller/cb-outdoor-kitchen-modular-system-desktop.webp": (
        "https://cboutdoorkitchen.com/cdn/shop/files/CB-Outdoor-Kitchen-Modular-System_1200x.jpg"
    ),
    "img/hersteller/cb-outdoor-kitchen-gasgrill-modul.webp": (
        "https://cboutdoorkitchen.com/cdn/shop/files/CB-Gas-Grill-Module_1200x.jpg"
    ),
    "img/hersteller/cb-outdoor-kitchen-monolith-modul.webp": (
        "https://cboutdoorkitchen.com/cdn/shop/files/CB-Monolith-Module_1200x.jpg"
    ),
    "img/hersteller/cb-outdoor-kitchen-ambiente-outdoor-kueche-terrasse.webp": (
        "https://cboutdoorkitchen.com/cdn/shop/files/CB-Outdoor-Kitchen-Lifestyle-Terrace_1200x.jpg"
    ),
    "img/hersteller/cb-outdoor-kitchen-freunde-garten-grillen-premium.webp": (
        "https://cboutdoorkitchen.com/cdn/shop/files/CB-Outdoor-Kitchen-Friends-Garden_1200x.jpg"
    ),
    "img/hersteller/cb-outdoor-kitchen-abend-grillen-couple-premium.webp": (
        "https://cboutdoorkitchen.com/cdn/shop/files/CB-Outdoor-Kitchen-Evening-Couple_1200x.jpg"
    ),

    # ── Everdure by Heston ────────────────────────────────────────────────────
    "img/hersteller/everdure-by-heston-blumenthal-4k-kamado-grill.png": (
        "https://everdure.com/cdn/shop/products/4K-CHARCOAL-BLK-01-1200x.jpg"
    ),

    # ── Grandhall ─────────────────────────────────────────────────────────────
    "img/hersteller/grandhall-gas-grill-built-in-hochwertig.jpg": (
        "https://www.grandhall.eu/media/catalog/product/cache/1/image/9df78eab33525d08d6e5fb8d27136e95/g/r/grandhall-built-in-gasgrill.jpg"
    ),
    "img/hersteller/grandhall-outdoor-kueche-grill-einbau-premium.jpg": (
        "https://www.grandhall.eu/media/catalog/product/cache/1/image/9df78eab33525d08d6e5fb8d27136e95/g/r/grandhall-outdoor-kitchen-premium.jpg"
    ),

    # ── Crossray ─────────────────────────────────────────────────────────────
    "img/hersteller/crossray-infrarot-grill-outdoor-kueche.webp": (
        "https://crossray.com.au/cdn/shop/products/crossray-infrared-bbq-outdoor-kitchen_1200x.jpg"
    ),
    "img/hersteller/crossray-2-brenner-infrarot-gasgrill-einbau.jpg": (
        "https://crossray.com.au/cdn/shop/products/crossray-2-burner-built-in-infrared_1200x.jpg"
    ),
    "img/hersteller/crossray-4-brenner-infrarot-gasgrill.png": (
        "https://crossray.com.au/cdn/shop/products/crossray-4-burner-infrared-bbq_1200x.jpg"
    ),

    # ── Heatstrip ────────────────────────────────────────────────────────────
    "img/hersteller/heatstrip-classic-infrarot-terrassenstrahler.jpg": (
        "https://heatstrip.com/cdn/shop/products/heatstrip-classic-heater_1200x.jpg"
    ),
    "img/hersteller/heatstrip-intense-terrassenheizung-infrarot.jpg": (
        "https://heatstrip.com/cdn/shop/products/heatstrip-intense-heater_1200x.jpg"
    ),
    "img/hersteller/heatstrip-elegance-terrassenstrahler-design.jpg": (
        "https://heatstrip.com/cdn/shop/products/heatstrip-elegance-heater_1200x.jpg"
    ),

    # ── Yakiniku ─────────────────────────────────────────────────────────────
    "img/hersteller/yakiniku-shichirin-mini-tischgrill-japanisch.jpg": (
        "https://www.yakiniku.nl/cdn/shop/products/yakiniku-shichirin-mini-table-grill_1200x.jpg"
    ),
    "img/hersteller/yakiniku-shichirin-rechteckig-yakitori.jpg": (
        "https://www.yakiniku.nl/cdn/shop/products/yakiniku-shichirin-rectangular_1200x.jpg"
    ),
    "img/hersteller/yakiniku-kamado-medium-schwarz-holzkohle.jpg": (
        "https://www.yakiniku.nl/cdn/shop/products/yakiniku-kamado-medium-black_1200x.jpg"
    ),
    "img/hersteller/yakiniku-kamado-grill-japanisch-keramik.jpg": (
        "https://www.yakiniku.nl/cdn/shop/products/yakiniku-kamado-ceramic-japanese_1200x.jpg"
    ),
    "img/hersteller/yakiniku-kamado-grill-premium-banner.jpg": (
        "https://www.yakiniku.nl/cdn/shop/files/yakiniku-kamado-banner_1200x.jpg"
    ),

    # ── Xapron ───────────────────────────────────────────────────────────────
    "img/hersteller/xapron-lederschuerze-navy-lang-bbq.png": (
        "https://www.xapron.com/cdn/shop/products/xapron-navy-long-apron_1200x.jpg"
    ),
    "img/hersteller/xapron-lederschuerze-schwarz-grillen.png": (
        "https://www.xapron.com/cdn/shop/products/xapron-black-bbq-apron_1200x.jpg"
    ),
    "img/hersteller/xapron-leder-bbq-schuerze-grillschuerze-premium.jpg": (
        "https://www.xapron.com/cdn/shop/products/xapron-leather-apron-premium_1200x.jpg"
    ),
    "img/hersteller/xapron-leder-qualitaet-material-schuerzen.jpg": (
        "https://www.xapron.com/cdn/shop/files/xapron-leather-quality-detail_1200x.jpg"
    ),

    # ── Zayiko ───────────────────────────────────────────────────────────────
    "img/hersteller/zayiko-damastmesser-sakura-serie-kaufen.png": (
        "https://zayiko.de/cdn/shop/products/zayiko-damask-knife-sakura_1200x.jpg"
    ),
    "img/hersteller/zayiko-damastmesser-essentials-serie-grillmesser.png": (
        "https://zayiko.de/cdn/shop/products/zayiko-damask-knife-essentials_1200x.jpg"
    ),
    "img/hersteller/zayiko-damastmesser-hochwertig-wuerzburg.jpg": (
        "https://zayiko.de/cdn/shop/files/zayiko-damask-knife-premium_1200x.jpg"
    ),

    # ── Le Maître ────────────────────────────────────────────────────────────
    "img/hersteller/le-maitre-corten-stahl-outdoor-bbq-feuerstelle.jpg": (
        "https://www.le-maitre.com/cdn/shop/products/le-maitre-corten-steel-bbq_1200x.jpg"
    ),

    # ── Witt ─────────────────────────────────────────────────────────────────
    "img/hersteller/witt-etna-rotante-pizzaofen-outdoor-garten.jpg": (
        "https://witt-international.com/cdn/shop/products/witt-etna-rotante-outdoor-pizza-oven_1200x.jpg"
    ),
    "img/hersteller/witt-etna-rotante-pizzaofen-rotierender-stein.jpg": (
        "https://witt-international.com/cdn/shop/products/witt-etna-rotante-rotating-stone_1200x.jpg"
    ),

    # ── The MeatStick ─────────────────────────────────────────────────────────
    "img/hersteller/the-meatstick-4-kabelloses-fleischthermometer.jpg": (
        "https://themeatstick.com/cdn/shop/products/meatstick-4-wireless-thermometer_1200x.jpg"
    ),
    "img/hersteller/the-meatstick-bbq-kitchen-set-thermometer.jpg": (
        "https://themeatstick.com/cdn/shop/products/meatstick-bbq-kitchen-set_1200x.jpg"
    ),

    # ── Camp Chef ─────────────────────────────────────────────────────────────
    "img/hersteller/camp-chef-woodwind-pro-36-pelletgrill-smoker.jpg": (
        "https://www.campchef.com/cdn/shop/products/woodwind-pro-36-pellet-grill_1200x.jpg"
    ),

    # ────────────────────────────────────────────────────────────────────────
    # HERO & KATEGORIEN – noch keine konkreten URLs bekannt.
    # Wenn Sie Bilder für /img/hero/ und /img/kategorien/ haben,
    # tragen Sie hier Dateiname → URL ein:
    # ────────────────────────────────────────────────────────────────────────
    # "img/hero/startseite-hero-outdoor-grill.jpg":
    #     "https://example.com/bild.jpg",
    # "img/kategorien/outdoor-kuechen-kategorie.jpg":
    #     "https://example.com/bild.jpg",
}

# ─── Hilfsfunktionen ─────────────────────────────────────────────────────────

def scan_html_images():
    """Alle img src / data-src aus HTML-Dateien extrahieren."""
    pattern = re.compile(
        r'(?:data-src|src)=["\']([^"\']+\.(?:jpg|jpeg|png|webp|gif|svg))["\']',
        re.IGNORECASE
    )
    found = set()
    for html_file in BASE_DIR.rglob("*.html"):
        # Eigene Website-Pfade, keine externen URLs
        text = html_file.read_text(encoding="utf-8", errors="ignore")
        for match in pattern.finditer(text):
            path = match.group(1)
            if path.startswith("/img/") and "placeholder" not in path:
                found.add(path.lstrip("/"))
    return sorted(found)


def check_missing(paths):
    """Gibt zurück welche lokalen Pfade nicht existieren."""
    missing = []
    for rel_path in paths:
        full = BASE_DIR / rel_path
        if not full.exists():
            missing.append(rel_path)
    return missing


def download_image(rel_path, url, overwrite=False):
    """Lädt ein Bild herunter und speichert es lokal."""
    dest = BASE_DIR / rel_path
    dest.parent.mkdir(parents=True, exist_ok=True)

    if dest.exists() and not overwrite:
        print(f"  → Vorhanden, übersprungen: {rel_path}")
        return True

    print(f"  ↓ Lade herunter: {rel_path}")
    print(f"    Quelle: {url}")

    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as response:
            content_type = response.headers.get("Content-Type", "")
            data = response.read()

        if len(data) < 1000:
            print(f"  ✗ Zu klein ({len(data)} Bytes) – möglicherweise Fehlerseite")
            return False

        dest.write_bytes(data)
        print(f"  ✓ Gespeichert ({len(data) // 1024} KB) [{content_type}]")
        return True

    except urllib.error.HTTPError as e:
        print(f"  ✗ HTTP {e.code}: {url}")
        return False
    except urllib.error.URLError as e:
        print(f"  ✗ URL-Fehler: {e.reason}")
        return False
    except Exception as e:
        print(f"  ✗ Fehler: {e}")
        return False


def print_summary(all_paths, missing, downloaded, failed, no_url):
    print("\n" + "═" * 60)
    print("ZUSAMMENFASSUNG")
    print("═" * 60)
    print(f"  Gefundene Bildreferenzen: {len(all_paths)}")
    print(f"  Bereits vorhanden:        {len(all_paths) - len(missing)}")
    print(f"  Fehlend:                  {len(missing)}")
    if downloaded:
        print(f"  Heruntergeladen:          {len(downloaded)}")
    if failed:
        print(f"  Fehlgeschlagen:           {len(failed)}")
        for f in failed:
            print(f"    ✗ {f}")
    if no_url:
        print(f"  Keine URL konfiguriert:   {len(no_url)}")
        for f in no_url:
            print(f"    ? {f}")
        print()
        print("  → Tragen Sie für diese Dateien eine URL in URL_MAP ein.")
    print("═" * 60)


# ─── Hauptprogramm ───────────────────────────────────────────────────────────

def main():
    do_download = "--download" in sys.argv or "--all" in sys.argv
    overwrite   = "--all" in sys.argv

    print("Grillwelt Feuerhaus Kalina – Bild-Download-Skript")
    print("=" * 60)
    print(f"Basisverzeichnis: {BASE_DIR}\n")

    # 1. HTML scannen
    print("Scanne HTML-Dateien...")
    all_paths = scan_html_images()
    print(f"  {len(all_paths)} Bildreferenzen gefunden.\n")

    # 2. Fehlende ermitteln
    if overwrite:
        missing = all_paths
    else:
        missing = check_missing(all_paths)

    if not missing:
        print("Alle Bilder sind bereits vorhanden.")
        print_summary(all_paths, missing, [], [], [])
        return

    print(f"Fehlende Bilder ({len(missing)}):")
    for p in missing:
        status = "✓ URL bekannt" if p in URL_MAP else "? Keine URL"
        print(f"  [{status}] {p}")
    print()

    if not do_download:
        print("Tipp: Starten Sie mit --download um fehlende Bilder herunterzuladen.")
        print("      Oder mit --all um alle Bilder neu herunterzuladen.")
        print_summary(all_paths, missing, [], [], [p for p in missing if p not in URL_MAP])
        return

    # 3. Herunterladen
    downloaded = []
    failed     = []
    no_url     = []

    print("Starte Download...\n")
    for rel_path in missing:
        if rel_path not in URL_MAP:
            no_url.append(rel_path)
            print(f"  ? Keine URL: {rel_path}")
            continue

        url = URL_MAP[rel_path]
        ok  = download_image(rel_path, url, overwrite=overwrite)

        if ok:
            downloaded.append(rel_path)
        else:
            failed.append(rel_path)

        time.sleep(DOWNLOAD_DELAY)

    print_summary(all_paths, missing, downloaded, failed, no_url)


if __name__ == "__main__":
    main()
