#!/usr/bin/env python3
"""Zadanie 11 - zastosowanie jąder splotu na obrazie YesNo_TestFiltrow.png

Skrypt:
- wczytuje obraz `YesNo_TestFiltrow.png` z katalogu nadrzędnego
- stosuje cztery zadane jądra (h_a, h_b, h_c, h_d) z normalizacją
- zapisuje wyniki filtrowania (reskalowane do 0-255) w katalogu zad11/
- drukuje krótką analizę: low/high-pass oraz kierunek czułości dla kierunkowych filtrów
"""

import os
import numpy as np
from PIL import Image

def get_script_dir():
    return os.path.dirname(os.path.abspath(__file__))

def load_image(img_path):
    img = Image.open(img_path).convert('L')
    return np.array(img, dtype=np.float32)

def try_convolve2d():
    try:
        from scipy.signal import convolve2d
        return lambda im, k: convolve2d(im, k, mode='same', boundary='symm')
    except Exception:
        try:
            from scipy.ndimage import convolve
            return lambda im, k: convolve(im, k, mode='reflect')
        except Exception:
            # fallback: simple numpy implementation (slow)
            def conv_fallback(im, k):
                kh, kw = k.shape
                pad_h = kh // 2
                pad_w = kw // 2
                padded = np.pad(im, ((pad_h, pad_h), (pad_w, pad_w)), mode='reflect')
                out = np.zeros_like(im)
                for i in range(out.shape[0]):
                    for j in range(out.shape[1]):
                        patch = padded[i:i+kh, j:j+kw]
                        out[i, j] = np.sum(patch * k)
                return out
            return conv_fallback

def normalize_kernel(k):
    k = np.array(k, dtype=np.float32)
    s = k.sum()
    if abs(s) > 1e-8:
        return k / s
    # sum == 0 -> normalize by sum of absolute values to keep scale
    a = np.sum(np.abs(k))
    if a == 0:
        return k
    return k / a

def rescale_to_uint8(arr):
    mn = arr.min()
    mx = arr.max()
    if mx - mn < 1e-8:
        return np.clip(arr, 0, 255).astype(np.uint8)
    scaled = (arr - mn) / (mx - mn) * 255.0
    return np.clip(scaled, 0, 255).astype(np.uint8)

def kernel_direction(k):
    # compute weighted centroid (dx, dy) where x is cols (east +), y is rows (south +)
    kh, kw = k.shape
    cy = kh // 2
    cx = kw // 2
    ys, xs = np.mgrid[0:kh, 0:kw]
    dx = np.sum((xs - cx) * k)
    dy = np.sum((ys - cy) * k)
    # if negligible vector, return None
    if abs(dx) < 1e-6 and abs(dy) < 1e-6:
        return None
    ang = np.degrees(np.arctan2(-dy, dx))  # negative dy since image y grows down
    ang = (ang + 360) % 360
    # map to 8 compass directions
    directions = ['E', 'NE', 'N', 'NW', 'W', 'SW', 'S', 'SE']
    sector = int(((ang + 22.5) % 360) // 45)
    return directions[sector]

def analyze_kernel(k):
    k = np.array(k, dtype=np.float32)
    has_neg = np.any(k < 0)
    s = k.sum()
    if not has_neg and s > 0:
        kind = 'low-pass (smoothing)'
    else:
        if abs(s) < 1e-6:
            kind = 'high-pass / edge detector (zero-sum kernel)'
        elif has_neg and s > 0:
            kind = 'sharpening / band-pass (contains negative lobes)'
        else:
            kind = 'other (mixed signs)'
    direction = kernel_direction(k)
    return kind, s, direction

def main():
    script_dir = get_script_dir()
    zad11_dir = os.path.join(script_dir)
    parent = os.path.normpath(os.path.join(script_dir, '..'))
    img_path = os.path.join(parent, 'YesNo_TestFiltrow.png')
    if not os.path.exists(img_path):
        print('ERROR: input image not found:', img_path)
        return

    im = load_image(img_path)
    conv = try_convolve2d()

    kernels = {
        'h_a': np.array([[0,0,1,0,0],[0,2,2,2,0],[1,2,5,2,1],[0,2,2,2,0],[0,0,1,0,0]], dtype=np.float32),
        'h_b': np.array([[1,-2,1],[-2,5,-2],[1,-2,1]], dtype=np.float32),
        'h_c': np.array([[0,1,1],[-1,1,1],[-1,-1,0]], dtype=np.float32),
        'h_d': np.array([[1,-1,-1],[1,-2,-1],[1,1,1]], dtype=np.float32),
    }

    out_dir = os.path.join(parent, 'zad11_outputs')
    os.makedirs(out_dir, exist_ok=True)

    summary_lines = []

    for name, k in kernels.items():
        k_norm = normalize_kernel(k)
        print(f'Applying {name} (normalized). Sum before normalization = {k.sum():.3f}, after = {k_norm.sum():.3f}')
        res = conv(im, k_norm)
        # save a rescaled visualization
        vis = rescale_to_uint8(res)
        out_path = os.path.join(out_dir, f'{name}_filtered.png')
        Image.fromarray(vis).save(out_path)
        kind, s, direction = analyze_kernel(k)
        summary_lines.append(f"{name}: kind={kind}, raw_sum={k.sum():.3f}, direction={direction}")
        print(summary_lines[-1])

    # Save summary
    summary_path = os.path.join(out_dir, 'summary.txt')
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(summary_lines))

    print('\nOutputs saved to:', out_dir)
    print('Summary:')
    for l in summary_lines:
        print(' -', l)

if __name__ == '__main__':
    main()
