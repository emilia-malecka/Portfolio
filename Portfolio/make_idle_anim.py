#!/usr/bin/env python3
"""
Character Idle Animation Compositor
=====================================
Nakłada postać z zamkniętymi oczami na scenę tła.
Efekty: mruganie + delikatny wiatr we włosach.

Wejście:
  assets/scene-home.png         — tło sceny (1672×941)
  assets/Person.png             — postać, otwarte oczy (RGBA)
  assets/Person close eye.png   — postać, zamknięte oczy (RGBA)

Wyjście:
  assets/idle_anim.gif          — pętla GIF
  assets/idle_anim.mp4          — pętla MP4 (H.264, brak metadanych)

Wymagania:
  pip install pillow opencv-python numpy rembg[cpu]
"""

import os
import io
import math
import numpy as np
from PIL import Image
import cv2

# ══════════════════════════════════════════════════════════════════════════════
# KONFIGURACJA
# ══════════════════════════════════════════════════════════════════════════════

BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
ASSETS        = os.path.join(BASE_DIR, "assets")

SCENE_PATH    = os.path.join(ASSETS, "scene-home.png")
OPEN_PATH     = os.path.join(ASSETS, "Person.png")
CLOSE_PATH    = os.path.join(ASSETS, "Person close eye.png")
OUTPUT_GIF    = os.path.join(ASSETS, "idle_anim.gif")
OUTPUT_MP4    = os.path.join(ASSETS, "idle_anim.mp4")

FPS           = 24          # klatki na sekundę
LOOP_SEC      = 6.0         # długość pętli [s]

# Mruganie
BLINK_AT_SEC  = 2.5         # czas pierwszego mrugnięcia w pętli [s]
BLINK_CLOSE   = 0.070       # czas zamykania oczu [s]
BLINK_HOLD    = 0.065       # czas trzymania oczu zamkniętych [s]
BLINK_OPEN    = 0.110       # czas otwierania oczu [s]

# Wiatr we włosach
WIND_AMP      = 5.0         # maksymalne przemieszczenie pikseli [px]
WIND_FREQ     = 0.35        # częstotliwość falowania [Hz]
WIND_ZONE     = 0.42        # strefa włosów: górne X% ramki postaci


# ══════════════════════════════════════════════════════════════════════════════
# 1. USUWANIE TŁA  (szachownica / jednolity kolor / ML fallback)
# ══════════════════════════════════════════════════════════════════════════════

def _sample_corners(arr: np.ndarray, size: int = 20) -> np.ndarray:
    """Zwraca RGB pikseli z czterech narożników obrazu."""
    h, w = arr.shape[:2]
    return np.vstack([
        arr[:size,  :size,  :3].reshape(-1, 3),
        arr[:size,  -size:, :3].reshape(-1, 3),
        arr[-size:, :size,  :3].reshape(-1, 3),
        arr[-size:, -size:, :3].reshape(-1, 3),
    ]).astype(np.float32)


def _detect_bg_colors(corners: np.ndarray):
    """
    Wykrywa 1 lub 2 kolory tła z próbki narożników.
    Szachownica → 2 kolory (jasny / ciemny).
    Jednolite tło → 1 kolor.
    """
    brightness = corners.mean(axis=1)
    std = corners.std(axis=0).mean()

    if std < 18:
        # Jednolity kolor
        return [corners.mean(axis=0)], 22
    else:
        # Dwa kolory (szachownica): dziel wg jasności
        median = np.median(brightness)
        light = corners[brightness >= median].mean(axis=0)
        dark  = corners[brightness <  median].mean(axis=0)
        return [light, dark], 30


def _color_bg_mask(arr: np.ndarray, bg_colors, tolerance: int) -> np.ndarray:
    """
    Tworzy maskę binarną (uint8) dla pikseli tła na podstawie koloru.
    Wartość 255 = tło, 0 = postać.
    """
    rgb  = arr[:, :, :3].astype(np.float32)
    mask = np.zeros(arr.shape[:2], dtype=np.uint8)
    for col in bg_colors:
        dist = np.linalg.norm(rgb - col, axis=2)
        mask |= (dist < tolerance).astype(np.uint8) * 255
    return mask


def _flood_fill_bg(mask: np.ndarray) -> np.ndarray:
    """
    Flood-fill od narożników: izoluje jedynie zewnętrzne tło,
    pozostawiając ewentualne 'wyspy' tła wewnątrz postaci nieruszone.
    """
    h, w = mask.shape
    filled = mask.copy()
    seed_mask = np.zeros((h + 2, w + 2), dtype=np.uint8)
    for cy, cx in [(0, 0), (0, w - 1), (h - 1, 0), (h - 1, w - 1)]:
        if filled[cy, cx] > 127:
            cv2.floodFill(filled, seed_mask, (cx, cy),
                          255, loDiff=(18, 18, 18), upDiff=(18, 18, 18))
    return filled


def _feather_alpha(fg_mask: np.ndarray, radius: int = 3) -> np.ndarray:
    """
    Rozmywa krawędzie maski (anty-aliasing).
    fg_mask: 0 = tło, 255 = postać (float32 lub uint8).
    Zwraca float32 [0..255].
    """
    kernel = 2 * radius + 1
    feathered = cv2.GaussianBlur(fg_mask.astype(np.float32),
                                  (kernel, kernel), radius / 2)
    return feathered


def remove_background(img: Image.Image) -> Image.Image:
    """
    Usuwa tło z obrazu RGBA.

    Krok 1 — sprawdź, czy obraz ma już realną przezroczystość.
    Krok 2 — algorytm własny: próbkowanie narożników + flood-fill.
    Krok 3 — fallback ML: rembg (jeśli algorytm własny nie dał >40% przezroczystości).
    """
    arr  = np.array(img.convert("RGBA"))
    h, w = arr.shape[:2]

    # ── Krok 1: czy alfa już działa? ─────────────────────────────────────────
    alpha       = arr[:, :, 3]
    transp_pct  = (alpha < 128).sum() / alpha.size
    if transp_pct > 0.40:
        print(f"    Alpha OK — {transp_pct*100:.0f}% pikseli przezroczystych.")
        return img

    print(f"    Alpha brak ({transp_pct*100:.1f}% przezroczystych). Uruchamiam usuwanie tła...")

    # ── Krok 2: algorytm własny ───────────────────────────────────────────────
    corners            = _sample_corners(arr)
    bg_colors, tol     = _detect_bg_colors(corners)
    print(f"    Wykryte tło: {len(bg_colors)} kolor(y), tolerancja={tol}px")

    raw_mask  = _color_bg_mask(arr, bg_colors, tol)            # 255=tło
    ext_mask  = _flood_fill_bg(raw_mask)                       # tylko zewnętrzne tło
    ext_mask  = cv2.dilate(ext_mask,                           # lekkia dylatacja krawędzi
                            cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)),
                            iterations=1)
    fg_mask   = 255 - ext_mask                                 # 255=postać
    feathered = _feather_alpha(fg_mask, radius=2)              # miękkie krawędzie

    result    = arr.copy()
    result[:, :, 3] = np.clip(feathered, 0, 255).astype(np.uint8)

    # Sprawdź wynik
    transp2 = (result[:, :, 3] < 128).sum() / result[:, :, 3].size
    if transp2 > 0.35:
        print(f"    Algorytm własny OK — {transp2*100:.0f}% przezroczystych.")
        return Image.fromarray(result, "RGBA")

    # ── Krok 3: fallback rembg ────────────────────────────────────────────────
    print(f"    Własny algorytm słaby ({transp2*100:.1f}%). Próba rembg ML...")
    try:
        from rembg import remove as rembg_remove
        with open(img.filename, 'rb') as f:
            data = rembg_remove(f.read())
        out = Image.open(io.BytesIO(data)).convert("RGBA")
        arr3    = np.array(out)
        transp3 = (arr3[:, :, 3] < 128).sum() / arr3[:, :, 3].size
        print(f"    rembg OK — {transp3*100:.0f}% przezroczystych.")
        return out
    except Exception as e:
        print(f"    rembg niedostępny: {e}. Zwracam częściowy wynik.")
        return Image.fromarray(result, "RGBA")


# ══════════════════════════════════════════════════════════════════════════════
# 2. SKALOWANIE I WYRÓWNANIE 1:1 (object-fit: cover)
# ══════════════════════════════════════════════════════════════════════════════

def cover_scale(img: Image.Image, target_wh: tuple) -> Image.Image:
    """
    Skaluje obraz metodą 'cover': wypełnia target_wh zachowując proporcje,
    następnie przycina środek do dokładnego rozmiaru docelowego.
    Wynik jest wyrównany piksel-do-piksela z tłem sceny.
    """
    tw, th = target_wh
    pw, ph = img.size
    scale  = max(tw / pw, th / ph)
    nw, nh = round(pw * scale), round(ph * scale)
    scaled = img.resize((nw, nh), Image.LANCZOS)
    x0     = (nw - tw) // 2
    y0     = (nh - th) // 2
    return scaled.crop((x0, y0, x0 + tw, y0 + th))


# ══════════════════════════════════════════════════════════════════════════════
# 3. WIATR WE WŁOSACH (displacement map)
# ══════════════════════════════════════════════════════════════════════════════

def wind_displacement_maps(shape: tuple, t: float,
                            amplitude: float, freq: float,
                            zone_frac: float):
    """
    Buduje mapy przemieszczenia (map_x, map_y) dla cv2.remap.

    Ograniczenia:
    - Tylko górna 'zone_frac' część ramki (strefa głowy/włosów).
    - Przemieszczenie X zanika liniowo od góry (pełna amplituda)
      do granicy strefy (zero) — reszta ciała nieruchoma.
    - Trzy zsumowane fale sinusoidalne dają organiczne falowanie.
    """
    h, w = shape[:2]
    zone_px = int(h * zone_frac)

    map_x = np.tile(np.arange(w, dtype=np.float32), (h, 1))
    map_y = np.tile(np.arange(h, dtype=np.float32).reshape(-1, 1), (1, w))

    tau = 2 * math.pi * freq * t
    for row in range(zone_px):
        decay = 1.0 - row / zone_px          # 1.0 na górze → 0.0 na granicy
        dx = amplitude * decay * (
            math.sin(tau)                       * 0.60 +   # główna fala
            math.sin(tau * 1.7  + row * 0.04)  * 0.25 +   # harmonixa
            math.sin(tau * 0.53 - row * 0.07)  * 0.15     # niska fala
        )
        map_x[row, :] = np.clip(map_x[row, :] + dx, 0, w - 1)

    return map_x, map_y


def apply_wind(person_arr: np.ndarray, t: float,
               amplitude: float, freq: float, zone_frac: float) -> np.ndarray:
    """
    Stosuje przemieszczenie wiatru do postaci RGBA.
    Tylko strefa głowy/włosów jest przemieszczana;
    dolna część ciała pozostaje bez zmian (zakotwiczona).
    """
    h, w    = person_arr.shape[:2]
    zone_px = int(h * zone_frac)

    map_x, map_y = wind_displacement_maps(person_arr.shape, t,
                                           amplitude, freq, zone_frac)

    # Remap tylko strefy włosów (reszta bez zmian → brak artefaktów na ciele)
    zone_arr = person_arr[:zone_px].astype(np.float32)
    zone_mx  = map_x[:zone_px].astype(np.float32)
    zone_my  = map_y[:zone_px].astype(np.float32)

    remapped = cv2.remap(zone_arr, zone_mx, zone_my,
                         interpolation=cv2.INTER_LINEAR,
                         borderMode=cv2.BORDER_REPLICATE)

    result = person_arr.copy()
    result[:zone_px] = np.clip(remapped, 0, 255).astype(np.uint8)
    return result


# ══════════════════════════════════════════════════════════════════════════════
# 4. KRZYWA MRUGANIA
# ══════════════════════════════════════════════════════════════════════════════

def blink_alpha(t: float, blink_t0: float,
                close_s: float, hold_s: float, open_s: float) -> float:
    """
    Zwraca wartość [0.0 – 1.0] warstwy zamkniętych oczu w chwili t.
    Kształt krzywej:
        0 → 1  (zamykanie, czas close_s)
        1       (utrzymanie, czas hold_s)
        1 → 0  (otwieranie, czas open_s)
    """
    dt    = t - blink_t0
    total = close_s + hold_s + open_s
    if dt < 0 or dt > total:
        return 0.0
    if dt < close_s:
        return dt / close_s
    elif dt < close_s + hold_s:
        return 1.0
    else:
        return 1.0 - (dt - close_s - hold_s) / open_s


# ══════════════════════════════════════════════════════════════════════════════
# 5. KOMPOZYCJA KLATKI
# ══════════════════════════════════════════════════════════════════════════════

def composite_frame(scene_np: np.ndarray,
                    open_arr: np.ndarray,
                    close_arr: np.ndarray,
                    t: float) -> np.ndarray:
    """
    Buduje jedną klatkę RGB:

    Warstwa 0: scene_np          (tło sceny, RGB)
    Warstwa 1: open_arr + wiatr  (postać z otwartymi oczami, RGBA)
    Warstwa 2: close_arr + wiatr (zamknięte oczy, RGBA, modulowane alpha mrugania)

    Mieszanie: standard alpha compositing (Porter-Duff 'over').
    """
    frame = scene_np.astype(np.float32)

    # — Postać, otwarte oczy + wiatr ──────────────────────────────────────────
    open_w = apply_wind(open_arr, t, WIND_AMP, WIND_FREQ, WIND_ZONE)
    oa     = open_w[:, :, 3:4].astype(np.float32) / 255.0
    frame  = frame * (1.0 - oa) + open_w[:, :, :3].astype(np.float32) * oa

    # — Warstwa zamkniętych oczu (mruganie) ───────────────────────────────────
    ba = blink_alpha(t, BLINK_AT_SEC, BLINK_CLOSE, BLINK_HOLD, BLINK_OPEN)
    if ba > 0.001:
        close_w = apply_wind(close_arr, t, WIND_AMP, WIND_FREQ, WIND_ZONE)
        ca      = (close_w[:, :, 3:4].astype(np.float32) / 255.0) * ba
        frame   = frame * (1.0 - ca) + close_w[:, :, :3].astype(np.float32) * ca

    return np.clip(frame, 0, 255).astype(np.uint8)


# ══════════════════════════════════════════════════════════════════════════════
# 6. EKSPORT (GIF + MP4, brak metadanych)
# ══════════════════════════════════════════════════════════════════════════════

def export_gif(frames: list, path: str, fps: int):
    ms = max(20, round(1000 / fps))   # GIF minimalny krok to 10ms, praktycznie 20ms
    frames[0].save(
        path,
        save_all=True,
        append_images=frames[1:],
        duration=ms,
        loop=0,
        optimize=False,
        comment=b"",          # brak metadanych / komentarzy
    )
    size_mb = os.path.getsize(path) / 1_048_576
    print(f"  GIF: {path}  [{len(frames)} klatek, {ms}ms/kl, {size_mb:.1f} MB]")


def export_mp4(frames: list, path: str, fps: int):
    w, h   = frames[0].size
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(path, fourcc, fps, (w, h))
    for img in frames:
        bgr = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        writer.write(bgr)
    writer.release()
    size_mb = os.path.getsize(path) / 1_048_576
    print(f"  MP4: {path}  [{len(frames)} klatek @ {fps}fps, {size_mb:.1f} MB]")
    # Uwaga: VideoWriter('mp4v') nie osadza metadanych EXIF/XMP/GPS.
    # Dla dodatkowej gwarancji można uruchomić:
    #   ffmpeg -i idle_anim.mp4 -map_metadata -1 -c copy idle_anim_clean.mp4


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("  Character Idle Animation Compositor  v1.0")
    print("=" * 60)

    # ── 1. Tło sceny ─────────────────────────────────────────────────────────
    print("\n[1/5] Tlo sceny...")
    scene      = Image.open(SCENE_PATH).convert("RGB")
    scene_wh   = scene.size
    scene_np   = np.array(scene)
    print(f"  {scene_wh[0]}x{scene_wh[1]} px  |  {SCENE_PATH}")

    # ── 2. Warstwy postaci ────────────────────────────────────────────────────
    print("\n[2/5] Warstwy postaci (usuwanie tla jesli konieczne)...")

    # Ladujemy z przypisaniem .filename (potrzebne dla rembg fallback)
    def load_with_filename(path):
        img = Image.open(path).convert("RGBA")
        img.filename = path          # zachowaj sciezke dla rembg fallback
        return img

    person_open  = remove_background(load_with_filename(OPEN_PATH))
    person_close = remove_background(load_with_filename(CLOSE_PATH))

    # ── 3. Wyrównanie 1:1 (cover scale do rozmiaru sceny) ────────────────────
    print("\n[3/5] Wyrownanie 1:1 do sceny (cover scale)...")
    open_sc   = cover_scale(person_open,  scene_wh)
    close_sc  = cover_scale(person_close, scene_wh)
    open_arr  = np.array(open_sc)
    close_arr = np.array(close_sc)

    # Walidacja wyrownania: srednia roznica kolorow postaci
    scene_test  = scene_np.astype(np.float32)
    open_rgb    = open_arr[:, :, :3].astype(np.float32)
    char_mask   = open_arr[:, :, 3] > 30
    mean_diff   = np.abs(scene_test - open_rgb)[char_mask].mean()
    print(f"  Srednia roznica kolorow w obszarze postaci: {mean_diff:.1f}/255")
    if mean_diff < 20:
        print("  Wyrownanie DOSKONALE (< 20 / 255). Kompozycja bedzie bezszwowa.")
    elif mean_diff < 40:
        print("  Wyrownanie DOBRE. Drobne roznice mozliwe na krawedziach.")
    else:
        print("  UWAGA: duza roznica — sprawdz czy pliki postaci odpowiadaja scenie.")

    # ── 4. Generowanie klatek ────────────────────────────────────────────────
    total_frames = round(FPS * LOOP_SEC)
    print(f"\n[4/5] Generowanie {total_frames} klatek  ({FPS}fps x {LOOP_SEC}s)...")
    pil_frames = []
    for i in range(total_frames):
        t     = i / FPS
        frame = composite_frame(scene_np, open_arr, close_arr, t)
        pil_frames.append(Image.fromarray(frame, "RGB"))
        if (i + 1) % FPS == 0 or i == total_frames - 1:
            pct = (i + 1) / total_frames * 100
            print(f"  {i+1:4d}/{total_frames}  ({pct:.0f}%)  t={t:.2f}s")

    # ── 5. Eksport ───────────────────────────────────────────────────────────
    print("\n[5/5] Eksport...")
    export_gif(pil_frames, OUTPUT_GIF, FPS)
    export_mp4(pil_frames, OUTPUT_MP4, FPS)

    print("\n[OK] Gotowe!")
    print(f"  Wyjscie GIF : {OUTPUT_GIF}")
    print(f"  Wyjscie MP4 : {OUTPUT_MP4}")
    print("\n  Metadane: PIL i OpenCV VideoWriter nie osadzaja EXIF/XMP/GPS.")
    print("  Dla MP4 mozna dodatkowo: ffmpeg -i idle_anim.mp4 -map_metadata -1 -c copy out_clean.mp4")


if __name__ == "__main__":
    main()
