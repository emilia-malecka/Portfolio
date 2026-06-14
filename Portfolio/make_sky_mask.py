#!/usr/bin/env python3
"""
Sky Mask Generator
==================
Generuje sky-mask.png — maska nieba do animacji chmur.

Algorytm:
  1. Detekcja krawedziowa Canny na scenie.
  2. Dla kazdej kolumny — najnizszy wyrazny edge w gornych 55% obrazu
     wyznacza granice nieba (sylweta gor).
  3. Wygludzanie granicy (moving average) dla plynnej linii.
  4. Budowa maski: bialy = niebo, czarny = gory/foreground.
  5. Pionowy Gaussian blur (feather) na granicy — naturalne przejscie.

Wejscie:  assets/scene-home.png
Wyjscie:  assets/sky-mask.png  (greyscale L, rozmiar = scena)
"""

import numpy as np
from PIL import Image
import cv2
import os

BASE   = os.path.dirname(os.path.abspath(__file__))
SCENE  = os.path.join(BASE, "assets", "scene-home.png")
OUTPUT = os.path.join(BASE, "assets", "sky-mask.png")

# ── Wczytaj scene ───────────────────────────────────────────────────────────
arr = np.array(Image.open(SCENE).convert("RGB"))
h, w = arr.shape[:2]
print(f"Scena: {w}x{h} px")

bgr  = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

# ── Krok 1: Canny edges — wykrywa sylwete gor ───────────────────────────────
blurred = cv2.GaussianBlur(gray, (5, 5), 2)
edges   = cv2.Canny(blurred, 25, 80)

# ── Krok 2: Sky boundary per kolumna ───────────────────────────────────────
# Szukamy najnizszego wyraznego edge w gornych 55% obrazu
limit = int(h * 0.55)
sky_bound = np.full(w, limit, dtype=np.float32)

for x in range(w):
    col_e = edges[:limit, x]
    nz    = np.nonzero(col_e)[0]
    if len(nz) > 0:
        sky_bound[x] = float(nz[-1])

# ── Krok 3: Wygludzanie granicy (moving average + clamp) ────────────────────
win    = 80   # piks - szerokosc okna wygludzajacego
padded = np.pad(sky_bound, win, mode='edge')
smoothed = np.array([
    padded[i : i + 2 * win + 1].mean()
    for i in range(w)
], dtype=np.float32)

# Dolna klapa: granica nie moze byc wyzej niz 8% ani nizej niz 62%
smoothed = np.clip(smoothed, h * 0.08, h * 0.62)

# ── Krok 4: Buduj maske binarna ─────────────────────────────────────────────
# Kazda kolumna: biale powyzej granicy, czarne ponizej
mask = np.zeros((h, w), dtype=np.uint8)
for x in range(w):
    end_row = int(smoothed[x]) + 20   # +20 px zapasu ponizej sylwety
    end_row = min(end_row, h)
    mask[:end_row, x] = 255

# ── Krok 5: Feather — pionowy Gaussian blur na granicy ──────────────────────
# Kernel (1, 81): bardzo waskie poziomo, szerokie pionowo
# → miekka granica gora/dol, bez rozmycia poziomego
feathered = cv2.GaussianBlur(mask.astype(np.float32), (1, 81), 28)
feathered = np.clip(feathered, 0, 255).astype(np.uint8)

# ── Krok 6: Zapisz ──────────────────────────────────────────────────────────
Image.fromarray(feathered, 'L').save(OUTPUT)

sky_pct  = (feathered > 127).sum() / feathered.size * 100
print(f"Maska zapisana: {OUTPUT}")
print(f"Pokrycie nieba: {sky_pct:.1f}% sceny")
print(f"Granica nieba (min/avg/max): "
      f"{smoothed.min():.0f} / {smoothed.mean():.0f} / {smoothed.max():.0f} px")
