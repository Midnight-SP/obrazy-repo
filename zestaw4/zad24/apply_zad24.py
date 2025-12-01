#!/usr/bin/env python3
"""Zadanie 24: Dekonwolucja metodą Van Citterta

Wejście: `wiewiorka_filtered.png` (obrazu przefiltrowany filtrem Newtona podanego w zadaniu)

Zadania:
- Uruchomić Van Cittert dla k = 2, 5, 15 iteracji (relaksacja alpha = 1.0 domyślnie)
- Zapisz obrazy przywrócone oraz obrazy różnic (symetryczne, wizualizowane wokół mid-gray)
- Zapisz też surowe tablice jako .npy

Użycie: python3 apply_zad24.py [--alpha 1.0]
"""
import os
import argparse
import numpy as np
from PIL import Image


def ensure_dir(p):
    if not os.path.exists(p):
        os.makedirs(p, exist_ok=True)


def to_gray(arr):
    # arr: HxWx3 or HxW
    if arr.ndim == 3 and arr.shape[2] == 3:
        # convert to luminance using Rec. 601
        r, g, b = arr[...,0], arr[...,1], arr[...,2]
        y = 0.299*r + 0.587*g + 0.114*b
        return y
    return arr


def conv2d_fft(image, kernel):
    # image, kernel: 2D floats
    s1 = image.shape
    s2 = kernel.shape
    out_shape = (s1[0] + s2[0] - 1, s1[1] + s2[1] - 1)
    # FFT-based convolution
    fsize = [int(2**np.ceil(np.log2(n))) for n in out_shape]
    FI = np.fft.rfftn(image, fsize)
    FK = np.fft.rfftn(kernel, fsize)
    conv = np.fft.irfftn(FI * FK, fsize)
    # crop to valid full conv region then extract same size as image with center depending on kernel anchor
    # We'll return same size as image using 'same' mode (centered)
    start0 = (s2[0] - 1) // 2
    start1 = (s2[1] - 1) // 2
    end0 = start0 + s1[0]
    end1 = start1 + s1[1]
    return conv[start0:end0, start1:end1]


def van_cittert(g, h, k=5, alpha=1.0):
    # g, h: 2D floats. Return f_k after k iterations.
    f = g.copy().astype(np.float32)
    for i in range(k):
        conv_f = conv2d_fft(f, h)
        residual = g - conv_f
        f = f + alpha * residual
    return f


def vis_diff(diff):
    # Map difference to mid-gray visualization: center at 128
    maxabs = max(1.0, np.abs(diff).max())
    vis = ((diff / (2.0 * maxabs)) + 0.5) * 255.0
    vis = np.clip(vis, 0, 255).astype(np.uint8)
    return vis


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--alpha', type=float, default=1.0, help='Relaxation parameter alpha')
    args = parser.parse_args()

    base = os.path.dirname(__file__)
    inp = os.path.join(base, '..', 'wiewiorka_filtered.png')
    if not os.path.exists(inp):
        inp = os.path.join(base, 'wiewiorka_filtered.png')
    if not os.path.exists(inp):
        print('Input image wiewiorka_filtered.png not found')
        return

    out_dir = base
    ensure_dir(out_dir)

    img = Image.open(inp).convert('RGB')
    arr = np.asarray(img).astype(np.float32)
    # Work on luminance (grayscale) for deconvolution
    g = to_gray(arr)
    # Normalize to 0..255 float (already)

    # Define kernel h (given in task)
    h = np.array([
        [1, 4, 6, 4, 1],
        [4,16,24,16,4],
        [6,24,36,24,6],
        [4,16,24,16,4],
        [1,4,6,4,1]
    ], dtype=np.float32)
    h = h / 256.0

    ks = [2, 5, 15]
    results = {}
    for k in ks:
        f_k = van_cittert(g, h, k=k, alpha=args.alpha)
        # clip to [0,255]
        f_k_clipped = np.clip(f_k, 0, 255).astype(np.uint8)
        results[k] = f_k_clipped
        Image.fromarray(f_k_clipped).save(os.path.join(out_dir, f'wiewiorka_restored_k{k}.png'))
        np.save(os.path.join(out_dir, f'wiewiorka_restored_k{k}.npy'), f_k.astype(np.float32))

        # difference (symmetric) f_k - g visualized
        diff = f_k - g
        diff_vis = vis_diff(diff)
        Image.fromarray(diff_vis).save(os.path.join(out_dir, f'wiewiorka_diff_k{k}.png'))
        np.save(os.path.join(out_dir, f'wiewiorka_diff_k{k}.npy'), diff.astype(np.float32))

    # Save original grayscale and kernel visualization
    Image.fromarray(g.astype(np.uint8)).save(os.path.join(out_dir, 'wiewiorka_input_gray.png'))
    np.save(os.path.join(out_dir, 'wiewiorka_input_gray.npy'), g.astype(np.float32))

    # Save kernel visualization (scaled)
    kh = (h - h.min()) / (h.max() - h.min()) * 255.0
    Image.fromarray(kh.astype(np.uint8)).save(os.path.join(out_dir, 'kernel_h.png'))

    print('Saved outputs to', out_dir)
    for k in ks:
        print('k=', k, ': restored ->', os.path.join(out_dir, f'wiewiorka_restored_k{k}.png'))
        print('k=', k, ': diff    ->', os.path.join(out_dir, f'wiewiorka_diff_k{k}.png'))


if __name__ == '__main__':
    main()
