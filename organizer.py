import os
import shutil
import hashlib
from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime
from pathlib import Path

def get_exif_date(pfad):
    try:
        bild = Image.open(pfad)
        exif = bild._getexif()
        if exif:
            for tag, value in exif.items():
                if TAGS.get(tag) == 'DateTimeOriginal':
                    return datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
        return datetime.fromtimestamp(os.path.getmtime(pfad))
    except Exception:
        return datetime.fromtimestamp(os.path.getmtime(pfad))

def get_file_date(pfad):
    return datetime.fromtimestamp(os.path.getmtime(pfad))

def berechne_hash(pfad, blocksize=65536):
    hasher = hashlib.sha256()
    with open(pfad, 'rb') as f:
        for block in iter(lambda: f.read(blocksize), b""):
            hasher.update(block)
    return hasher.hexdigest()

def sortiere_medien(quellordner, zielordner, duplikat_ordner=None, nur_kopieren=False, print_fn=print, progress_fn=None):
    bilder = (".jpg", ".jpeg", ".png", ".heic", ".bmp", ".gif", ".tif", ".tiff")
    videos = (".mp4", ".mov", ".avi", ".mkv", ".wmv", ".3gp", ".mts")
    bekannte_hashes = set()
    dateien = []

    for root, _, files in os.walk(quellordner):
        for datei in files:
            pfad = os.path.join(root, datei)
            endung = Path(datei).suffix.lower()
            if endung in bilder + videos:
                dateien.append((pfad, endung, datei))

    anzahl = len(dateien)
    verarbeitet = 0
    verschoben = 0
    duplikate = 0

    for i, (pfad, endung, datei) in enumerate(dateien):
        file_hash = berechne_hash(pfad)
        if file_hash in bekannte_hashes:
            duplikate += 1
            print_fn(f"⚠️  Duplikat übersprungen: {pfad}")
            if duplikat_ordner:
                duplikat_ziel = Path(duplikat_ordner) / Path(datei).name
                Path(duplikat_ordner).mkdir(parents=True, exist_ok=True)
                shutil.copy2(pfad, duplikat_ziel)
                print_fn(f"    ➜ Duplikat gespeichert unter: {duplikat_ziel}")
            if progress_fn:
                progress_fn((i+1)/anzahl)
            continue
        else:
            bekannte_hashes.add(file_hash)

        datum = get_exif_date(pfad) if endung in bilder else get_file_date(pfad)
        jahr = str(datum.year)
        monat = f"{datum.month:02}"
        ziel_pfad = Path(zielordner) / jahr / monat
        ziel_pfad.mkdir(parents=True, exist_ok=True)

        ziel_datei = ziel_pfad / Path(datei).name
        counter = 1
        while ziel_datei.exists():
            name_stamm = Path(datei).stem
            ext = Path(datei).suffix
            ziel_datei = ziel_pfad / f"{name_stamm}_{counter}{ext}"
            counter += 1

        if nur_kopieren:
            shutil.copy2(pfad, ziel_datei)
            print_fn(f"📁 Kopiert: {pfad} ➜ {ziel_datei}")
        else:
            shutil.move(pfad, ziel_datei)
            print_fn(f"📂 Verschoben: {pfad} ➜ {ziel_datei}")
            verschoben += 1

        verarbeitet += 1
        if progress_fn:
            progress_fn((i+1)/anzahl)

    print_fn(f"\n✅ Fertig! {verarbeitet} verarbeitet, {verschoben} verschoben, {duplikate} Duplikate.")