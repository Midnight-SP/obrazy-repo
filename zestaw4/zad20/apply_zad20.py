#!/usr/bin/env python3
"""Zadanie 20: wykrywanie krawędzi operatorem Sobela dla Escher.png

Skrypt:
- wczytuje `Escher.png` z katalogu nadrzędnego
- oblicza g1 = g * h1 (pionowa pochodna Sobela)
- oblicza g2 = g * h2 (pozioma pochodna Sobela)
- oblicza g3 = sqrt(g1^2 + g2^2)
- zapisuje wyniki w `zestaw4/zad20_outputs/`
"""

import os
import numpy as np
from PIL import Image

def load_image(path):
    return np.array(Image.open(path).convert('L'), dtype=np.float32)

def save_uint8(arr, path, clip_percent=0.0):
    # optional clipping by percentiles to improve contrast
    if clip_percent > 0:
        lo = np.percentile(arr, clip_percent)
        hi = np.percentile(arr, 100-clip_percent)
        arr = np.clip(arr, lo, hi)
    mn = arr.min()
    mx = arr.max()
    if mx - mn < 1e-8:
        out = np.clip(arr, 0, 255).astype(np.uint8)
    else:
        out = ((arr - mn) / (mx - mn) * 255.0).astype(np.uint8)
    Image.fromarray(out).save(path)

def convolve2d(im, k):
    try:
        from scipy.signal import convolve2d
        return convolve2d(im, k, mode='same', boundary='symm')
    except Exception:
        try:
            from scipy.ndimage import convolve
            return convolve(im, k, mode='reflect')
        except Exception:
            # naive fallback
            kh, kw = k.shape
            ph, pw = kh//2, kw//2
            padded = np.pad(im, ((ph,ph),(pw,pw)), mode='reflect')
            out = np.zeros_like(im)
            for i in range(im.shape[0]):
                for j in range(im.shape[1]):
                    out[i,j] = np.sum(padded[i:i+kh, j:j+kw] * k)
            return out

def main():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    img_path = os.path.join(base, 'Escher.png')
    out_dir = os.path.join(base, 'zad20_outputs')
    os.makedirs(out_dir, exist_ok=True)

    if not os.path.exists(img_path):
        print('Input image not found:', img_path)
        return

    g = load_image(img_path)

    # Sobel kernels (as in the task)
    h1 = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=np.float32)  # vertical
    h2 = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float32)  # horizontal

    conv = convolve2d

    g1 = conv(g, h1)
    g2 = conv(g, h2)

    # magnitude
    g3 = np.hypot(g1, g2)

    # save
    Image.fromarray(np.clip(g,0,255).astype(np.uint8)).save(os.path.join(out_dir, 'original.png'))
    save_uint8(g1, os.path.join(out_dir, 'g1_sobel_vertical.png'))
    save_uint8(np.abs(g1), os.path.join(out_dir, 'g1_sobel_vertical_abs.png'))
    save_uint8(g2, os.path.join(out_dir, 'g2_sobel_horizontal.png'))
    save_uint8(np.abs(g2), os.path.join(out_dir, 'g2_sobel_horizontal_abs.png'))
    save_uint8(g3, os.path.join(out_dir, 'g3_sobel_magnitude.png'), clip_percent=0.5)

    # save raw numpy arrays for inspection
    np.save(os.path.join(out_dir, 'g1_raw.npy'), g1)
    np.save(os.path.join(out_dir, 'g2_raw.npy'), g2)
    np.save(os.path.join(out_dir, 'g3_raw.npy'), g3)

    # summary
    def stats(name, a):
        print(f"{name}: min={a.min():.3f}, max={a.max():.3f}, mean={a.mean():.3f}, std={a.std():.3f}")

    stats('g (orig)', g)
    stats('g1 (vertical)', g1)
    stats('g2 (horizontal)', g2)
    stats('g3 (magnitude)', g3)

    print('Outputs saved to', out_dir)

if __name__ == '__main__':
    main()
