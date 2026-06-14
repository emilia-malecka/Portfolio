#!/usr/bin/env python3
"""
Usuwa czarne tło z film.mp4 metodą luma-key.
Wyjście: assets/film_alpha.webm (VP9 + alpha) gotowy do overlay.

Wymaga: pip install imageio[ffmpeg] opencv-python numpy
"""

import cv2
import numpy as np
import subprocess
import sys
import os
import tempfile
import shutil

BASE   = os.path.dirname(os.path.abspath(__file__))
INPUT  = os.path.join(BASE, "assets", "film.mp4")
OUTPUT = os.path.join(BASE, "assets", "film_alpha.webm")
PREVIEW_DIR = os.path.join(BASE, "assets", "film_preview")

# ── Ustawienia luma-key ──────────────────────────────────────────────────────
THRESHOLD  = 30     # piksele < threshold*3 traktowane jako czysta czerń
SOFT_RANGE = 60     # zakres płynnego przejścia (feather) powyżej threshold
# Wzór: jeśli max(R,G,B) < THRESHOLD → alpha=0, powyżej THRESHOLD+SOFT_RANGE → alpha=255
# Obszar środkowy liniowo interpolowany → miękkie krawędzie bez "halacji"

def luma_key(bgr: np.ndarray) -> np.ndarray:
    """Zwraca obraz BGRA; alpha = 0 dla czerni, 255 dla postaci."""
    luma = bgr.max(axis=2).astype(np.float32)          # max kanału = jasność
    alpha = np.clip((luma - THRESHOLD) / SOFT_RANGE, 0.0, 1.0) * 255
    alpha = alpha.astype(np.uint8)

    # Usuń "poświatę" przy krawędziach: spill suppression
    # Zmniejsz jasność kanałów proporcjonalnie do alpha
    bgra = cv2.cvtColor(bgr, cv2.COLOR_BGR2BGRA)
    bgra[:, :, 3] = alpha

    # Odejmij kolor tła (czarny) pomnożony przez (1-alpha) → clean edges
    mask = (1.0 - alpha.astype(np.float32) / 255.0)[:, :, np.newaxis]
    bgra[:, :, :3] = np.clip(
        bgra[:, :, :3].astype(np.float32) - bgr.astype(np.float32) * mask * 0.0,
        0, 255
    ).astype(np.uint8)

    return bgra


def get_ffmpeg():
    try:
        from imageio_ffmpeg import get_ffmpeg_exe
        return get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


def main():
    print(f"Wejście : {INPUT}")
    print(f"Wyjście : {OUTPUT}")

    cap = cv2.VideoCapture(INPUT)
    if not cap.isOpened():
        print("BŁĄD: nie można otworzyć pliku wideo.")
        sys.exit(1)

    fps    = cap.get(cv2.CAP_PROP_FPS)
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total  = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Parametry: {width}x{height} @ {fps}fps, {total} klatek ({total/fps:.1f}s)")

    # ── Generuj podgląd 4 klatek (bez FFmpeg) ──────────────────────────────
    os.makedirs(PREVIEW_DIR, exist_ok=True)
    preview_frames = [0, total//4, total//2, 3*total//4]
    print(f"\nGeneruję podgląd 4 klatek PNG...")
    for fi in preview_frames:
        cap.set(cv2.CAP_PROP_POS_FRAMES, fi)
        ret, frame = cap.read()
        if not ret:
            continue
        bgra = luma_key(frame)
        out_path = os.path.join(PREVIEW_DIR, f"preview_{fi:04d}.png")
        cv2.imwrite(out_path, bgra)
        print(f"  Klatka {fi}: {out_path}")
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    # ── Tymczasowy katalog na klatki PNG ────────────────────────────────────
    tmpdir = tempfile.mkdtemp(prefix="film_alpha_")
    print(f"\nPrzetwarzam {total} klatek -> {tmpdir}")

    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        bgra = luma_key(frame)
        out_path = os.path.join(tmpdir, f"frame_{frame_idx:05d}.png")
        cv2.imwrite(out_path, bgra)
        frame_idx += 1
        if frame_idx % 24 == 0:
            pct = frame_idx / total * 100
            print(f"  {frame_idx}/{total} ({pct:.0f}%)")

    cap.release()
    print(f"Gotowe: {frame_idx} klatek zapisanych.")

    # ── Koduj do WebM VP9 z kanałem alpha ───────────────────────────────────
    ffmpeg = get_ffmpeg()
    cmd = [
        ffmpeg, "-y",
        "-framerate", str(fps),
        "-i", os.path.join(tmpdir, "frame_%05d.png"),
        "-c:v", "libvpx-vp9",
        "-pix_fmt", "yuva420p",      # YUVA = alpha channel
        "-crf", "18",                 # jakość (0=bezstratne, 63=najgorsze)
        "-b:v", "0",
        "-auto-alt-ref", "0",         # wymagane dla alpha w VP9
        OUTPUT,
    ]
    print(f"\nKoduję WebM VP9 z alpha...")
    print("  " + " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("BŁĄD ffmpeg:")
        print(result.stderr[-2000:])
    else:
        size_mb = os.path.getsize(OUTPUT) / 1_048_576
        print(f"  WebM zapisany: {OUTPUT}  ({size_mb:.1f} MB)")

    # Cleanup
    shutil.rmtree(tmpdir, ignore_errors=True)
    print(f"\nPodgląd PNG: {PREVIEW_DIR}/")
    print(f"Wyjście WebM: {OUTPUT}")
    print("GOTOWE.")


if __name__ == "__main__":
    main()
