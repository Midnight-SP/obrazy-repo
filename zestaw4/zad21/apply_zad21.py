#!/usr/bin/env python3
"""Zadanie 21: Detektor krawędzi Kirscha

Skrypt:
- wczytuje `Escher.png` z katalogu nadrzędnego
- tworzy 8 jąder Kirsch (N, NE, E, SE, S, SW, W, NW)
- konwoluuje każdy z nich z obrazem (boundary='symm' jeśli dostępne)
- oblicza maksymalną odpowiedź f = max_i (g * h_i)
- zapisuje obrazy odpowiedzi oraz mapę kierunków (argmax) w `zad21_outputs`
"""

import os
import numpy as np
from PIL import Image

def load_image(path):
    return np.array(Image.open(path).convert('L'), dtype=np.float32)

def save_uint8(arr, path, clip_percent=0.0):
    if clip_percent > 0:
        lo = np.percentile(arr, clip_percent)
        hi = np.percentile(arr, 100-clip_percent)
        arr = np.clip(arr, lo, hi)
    mn, mx = arr.min(), arr.max()
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
    out_dir = os.path.join(base, 'zad21_outputs')
    os.makedirs(out_dir, exist_ok=True)

    if not os.path.exists(img_path):
        print('Input image not found:', img_path)
        return

    g = load_image(img_path)

    # Kirsch kernels (standard 8 directions)
    K = []
    K.append(np.array([[-3,-3,5],[-3,0,5],[-3,-3,5]], dtype=np.float32))  # N
    K.append(np.array([[-3,5,5],[-3,0,5],[-3,-3,-3]], dtype=np.float32))  # NE (matches task h1)
    K.append(np.array([[5,5,5],[-3,0,-3],[-3,-3,-3]], dtype=np.float32))  # E
    K.append(np.array([[5,5,-3],[5,0,-3],[-3,-3,-3]], dtype=np.float32))  # SE
    K.append(np.array([[5,-3,-3],[5,0,-3],[5,-3,-3]], dtype=np.float32))  # S
    K.append(np.array([[-3,-3,-3],[5,0,-3],[5,5,-3]], dtype=np.float32))  # SW
    K.append(np.array([[-3,-3,-3],[-3,0,-3],[5,5,5]], dtype=np.float32))  # W
    K.append(np.array([[-3,-3,-3],[-3,0,5],[-3,5,5]], dtype=np.float32))  # NW

    conv = convolve2d

    responses = []
    for idx, k in enumerate(K):
        r = conv(g, k)
        responses.append(r)
        save_uint8(np.abs(r), os.path.join(out_dir, f'response_{idx:02d}.png'))

    resp_stack = np.stack(responses, axis=0)  # shape (8,H,W)
    # max response and argmax (direction index)
    resp_max = np.max(resp_stack, axis=0)
    resp_arg = np.argmax(resp_stack, axis=0)

    # save max response (edge map)
    save_uint8(resp_max, os.path.join(out_dir, 'kirsch_max_response.png'), clip_percent=0.5)

    # create direction map (color-coded)
    colors = np.array([
        [255,0,0],    # N - red
        [255,128,0],  # NE - orange
        [255,255,0],  # E - yellow
        [0,255,0],    # SE - green
        [0,255,255],  # S - cyan
        [0,0,255],    # SW - blue
        [128,0,255],  # W - purple
        [255,0,128],  # NW - magenta
    ], dtype=np.uint8)

    h,w = resp_arg.shape
    dir_map = np.zeros((h,w,3), dtype=np.uint8)
    for i in range(8):
        mask = (resp_arg == i)
        dir_map[mask] = colors[i]

    Image.fromarray(dir_map).save(os.path.join(out_dir, 'kirsch_direction_map.png'))

    # summary statistics
    def stats(name, a):
        print(f"{name}: min={a.min():.3f}, max={a.max():.3f}, mean={a.mean():.3f}, std={a.std():.3f}")

    stats('g (orig)', g)
    for i,r in enumerate(responses):
        stats(f'response_{i}', r)
    stats('resp_max', resp_max)

    # save raw arrays
    np.save(os.path.join(out_dir, 'resp_stack.npy'), resp_stack)
    np.save(os.path.join(out_dir, 'resp_max.npy'), resp_max)
    np.save(os.path.join(out_dir, 'resp_arg.npy'), resp_arg)

    print('Kirsch outputs saved to', out_dir)

if __name__ == '__main__':
    main()
