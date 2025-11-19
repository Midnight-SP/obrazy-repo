#!/usr/bin/env python3
"""
Zadanie 3: Charakterystyka jakościowa obrazów
- Wyznacz kontrast globalny (Michelsona) oraz lokalny (Webera i lokalny Michelson) 
  dla obrazów tygrysA.png, tygrysB.png, tygrysC.png.

Definicje (dla obrazu w skali szarości, zakres 0..255):
- Kontrast globalny (Michelsona): K_M = (I_max - I_min) / (I_max + I_min),
  gdzie I_max i I_min to maksymalna i minimalna intensywność w całym obrazie.
- Kontrast lokalny (Webera) dla piksela g: K_W(g) = (g - mean(N_g)) / mean(N_g),
  gdzie N_g to 8-sąsiedztwo (ośmiospójne) piksela g. Dla mean ~ 0 stosujemy eps.
- Kontrast lokalny (Michelsona) w oknie 3x3: K_M_local(g) = (max(W_g) - min(W_g)) / (max(W_g) + min(W_g)),
  gdzie W_g to okno 3x3 wokół g (z włączeniem g).

Skrypt zapisuje mapy kontrastu lokalnego oraz drukuje podsumowanie liczbowe.
"""
import os
import sys
from typing import Tuple
import numpy as np
from PIL import Image


def load_gray(path: str) -> np.ndarray:
    img = Image.open(path).convert('L')
    return np.asarray(img, dtype=np.float32)


def global_contrast_michelson(gray: np.ndarray) -> float:
    imin = float(np.min(gray))
    imax = float(np.max(gray))
    denom = imax + imin
    if denom <= 1e-9:
        return 0.0
    return (imax - imin) / denom


def neighbors8_sum_and_count(gray: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Fast 8-neighborhood sum and count using array shifts (no loops, no scipy)."""
    h, w = gray.shape
    # Pad by 1 with edge replication to handle borders gracefully
    pad = np.pad(gray, ((1, 1), (1, 1)), mode='edge')

    # Slices for 8 directions around the center
    UL = pad[0:h,     0:w    ]
    U  = pad[0:h,     1:w+1  ]
    UR = pad[0:h,     2:w+2  ]
    L  = pad[1:h+1,   0:w    ]
    R  = pad[1:h+1,   2:w+2  ]
    DL = pad[2:h+2,   0:w    ]
    D  = pad[2:h+2,   1:w+1  ]
    DR = pad[2:h+2,   2:w+2  ]

    s = UL + U + UR + L + R + DL + D + DR

    # Neighbor count per pixel (varies on borders): build via ones with same pad trick
    ones = np.ones_like(gray, dtype=np.float32)
    pad1 = np.pad(ones, ((1,1),(1,1)), mode='constant', constant_values=0)
    c = (pad1[0:h,0:w] + pad1[0:h,1:w+1] + pad1[0:h,2:w+2] +
         pad1[1:h+1,0:w]                 + pad1[1:h+1,2:w+2] +
         pad1[2:h+2,0:w] + pad1[2:h+2,1:w+1] + pad1[2:h+2,2:w+2])
    return s, c


ess = 1e-6

def local_contrast_weber(gray: np.ndarray) -> np.ndarray:
    s, c = neighbors8_sum_and_count(gray)
    mean_nb = s / np.maximum(c, 1.0)
    return (gray - mean_nb) / np.maximum(mean_nb, ess)


def local_contrast_michelson(gray: np.ndarray) -> np.ndarray:
    """Local Michelson contrast in a 3x3 window around each pixel (including center)."""
    h, w = gray.shape
    pad = np.pad(gray, ((1,1),(1,1)), mode='edge')
    # Collect the 9 positions
    stacks = [
        pad[0:h,0:w],   pad[0:h,1:w+1],   pad[0:h,2:w+2],
        pad[1:h+1,0:w], pad[1:h+1,1:w+1], pad[1:h+1,2:w+2],
        pad[2:h+2,0:w], pad[2:h+2,1:w+1], pad[2:h+2,2:w+2],
    ]
    arr = np.stack(stacks, axis=0)  # [9, h, w]
    local_min = np.min(arr, axis=0)
    local_max = np.max(arr, axis=0)
    denom = local_max + local_min
    out = np.zeros_like(gray, dtype=np.float32)
    mask = denom > ess
    out[mask] = (local_max[mask] - local_min[mask]) / denom[mask]
    return out


def to_uint8_image(arr: np.ndarray, mode: str = 'abs') -> Image.Image:
    """Map contrast array to 0..255 for visualization.
    - mode='abs': map |arr| with percentile-based clipping (p1..p99) for robustness.
    - mode='pos': assume arr in [0,1], scale to 0..255.
    """
    a = np.asarray(arr, dtype=np.float32)
    if mode == 'pos':
        a = np.clip(a, 0.0, 1.0)
        a = (a * 255.0).astype(np.uint8)
        return Image.fromarray(a, mode='L')
    # abs mode
    v = np.abs(a)
    p1, p99 = np.percentile(v, [1, 99])
    if p99 <= p1 + 1e-9:
        p1, p99 = 0.0, float(np.max(v) or 1.0)
    v = np.clip((v - p1) / max(p99 - p1, 1e-6), 0.0, 1.0)
    v = (v * 255.0).astype(np.uint8)
    return Image.fromarray(v, mode='L')


def analyze_image(path: str, out_dir: str) -> None:
    name = os.path.splitext(os.path.basename(path))[0]
    gray = load_gray(path)

    K_global = global_contrast_michelson(gray)
    K_weber = local_contrast_weber(gray)
    K_mloc = local_contrast_michelson(gray)

    # Stats
    weber_mean = float(np.mean(np.abs(K_weber)))
    weber_median = float(np.median(np.abs(K_weber)))
    mloc_mean = float(np.mean(K_mloc))
    mloc_median = float(np.median(K_mloc))

    # Save maps
    os.makedirs(out_dir, exist_ok=True)
    to_uint8_image(K_weber, mode='abs').save(os.path.join(out_dir, f"{name}-weber.png"))
    to_uint8_image(K_mloc, mode='pos').save(os.path.join(out_dir, f"{name}-local-michelson.png"))

    # Print summary
    print(f"{name}: Global Michelson = {K_global:.4f}")
    print(f"{name}: Local Weber |mean| = {weber_mean:.4f}, median|.| = {weber_median:.4f}")
    print(f"{name}: Local Michelson mean = {mloc_mean:.4f}, median = {mloc_median:.4f}")


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    # Default paths (adjust if needed)
    base = os.path.dirname(os.path.abspath(__file__))
    imgs = [
        os.path.join(base, 'tygrysA.png'),
        os.path.join(base, 'tygrysB.png'),
        os.path.join(base, 'tygrysC.png'),
    ]
    out_dir = base

    for p in imgs:
        if not os.path.exists(p):
            print(f"Brak pliku: {p}")
        else:
            analyze_image(p, out_dir)


if __name__ == '__main__':
    main()
