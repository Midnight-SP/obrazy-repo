#!/usr/bin/env python3
"""
Zadanie 4: Ocena jakości obrazów - MSE
- Referencja: osaRGB_PNG.png
- Porównania: osaRGB_gif.gif, osaRGB_JPG.jpg

Liczymy MSE dla obrazów RGB:
- MSE_R, MSE_G, MSE_B osobno
- MSE_avg = (MSE_R + MSE_G + MSE_B) / 3

Dodatkowo zapisujemy mapy błędu (różnica) dla wizualizacji.
"""
import os
import sys
from typing import Tuple
import numpy as np
from PIL import Image


def load_rgb(path: str) -> np.ndarray:
    img = Image.open(path).convert('RGB')
    return np.asarray(img, dtype=np.float32)


def mse_per_channel(ref: np.ndarray, test: np.ndarray) -> Tuple[float, float, float, float]:
    if ref.shape != test.shape:
        raise ValueError("Rozmiary obrazów nie zgadzają się: %s vs %s" % (ref.shape, test.shape))
    diff = ref - test
    se = diff * diff
    # kanały
    r = float(np.mean(se[..., 0]))
    g = float(np.mean(se[..., 1]))
    b = float(np.mean(se[..., 2]))
    avg = (r + g + b) / 3.0
    return r, g, b, avg


def save_error_visuals(ref: np.ndarray, test: np.ndarray, out_prefix: str) -> None:
    diff = np.abs(ref - test)
    # mapa |diff| w luminancji (prosty average kanałów)
    lum = np.mean(diff, axis=2)
    # skalowanie do 0..255 poprzez percentyle (robustnie)
    p95 = np.percentile(lum, 95)
    scale = 255.0 / max(p95, 1e-6)
    vis = np.clip(lum * scale, 0, 255).astype(np.uint8)
    Image.fromarray(vis, mode='L').save(out_prefix + '-diff-luma.png')

    # per kanał heatmapa (po prostu diff skompresowany do 0..255)
    for i, ch in enumerate('RGB'):
        chd = diff[..., i]
        p95c = np.percentile(chd, 95)
        scalec = 255.0 / max(p95c, 1e-6)
        visc = np.clip(chd * scalec, 0, 255).astype(np.uint8)
        Image.fromarray(visc, mode='L').save(out_prefix + f'-diff-{ch}.png')


def main():
    base = os.path.dirname(os.path.abspath(__file__))
    ref_path = os.path.join(base, 'osaRGB_PNG.png')
    gif_path = os.path.join(base, 'osaRGB_gif.gif')
    jpg_path = os.path.join(base, 'osaRGB_JPG.jpg')

    for p in [ref_path, gif_path, jpg_path]:
        if not os.path.exists(p):
            print('Brak pliku:', p)
            return 1

    ref = load_rgb(ref_path)
    gif = load_rgb(gif_path)
    jpg = load_rgb(jpg_path)

    if ref.shape != gif.shape or ref.shape != jpg.shape:
        print('Rozmiary obrazów są różne:', ref.shape, gif.shape, jpg.shape)
        return 1

    r_gif, g_gif, b_gif, avg_gif = mse_per_channel(ref, gif)
    r_jpg, g_jpg, b_jpg, avg_jpg = mse_per_channel(ref, jpg)

    print('GIF vs PNG: MSE_R = %.2f, MSE_G = %.2f, MSE_B = %.2f, MSE_avg = %.2f' % (r_gif, g_gif, b_gif, avg_gif))
    print('JPG vs PNG: MSE_R = %.2f, MSE_G = %.2f, MSE_B = %.2f, MSE_avg = %.2f' % (r_jpg, g_jpg, b_jpg, avg_jpg))

    # Zapisy wizualizacji różnic
    save_error_visuals(ref, gif, os.path.join(base, 'GIF'))
    save_error_visuals(ref, jpg, os.path.join(base, 'JPG'))

    # Który lepszy wg MSE
    better = 'GIF' if avg_gif < avg_jpg else 'JPEG'
    print('Lepszy wg MSE:', better)
    return 0


if __name__ == '__main__':
    sys.exit(main())
