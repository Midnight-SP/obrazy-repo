#!/usr/bin/env python3
"""Zadanie 14: splot jąder filtrów (Odd_Moon.png)

Skrypt wykonuje:
 - h1 = averaging 3x3 (uśredniający)
 - h2 = [0, 1, -1] (poziomy filtr gradientowy)
 - g1 = g * h1
 - g2 = g1 * h2
 - h3 = h1 * h2 (splot jąder)
 - g3 = g * h3

Wyniki zapisane do: ../zad14_outputs/
"""

import os
import numpy as np
from PIL import Image

def load_image(path):
    return np.array(Image.open(path).convert('L'), dtype=np.float32)

def save_uint8(arr, path):
    # rescale linearly for visualization
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
            # fallback naive
            kh, kw = k.shape
            ph = kh // 2
            pw = kw // 2
            padded = np.pad(im, ((ph, ph), (pw, pw)), mode='reflect')
            out = np.zeros_like(im)
            for i in range(im.shape[0]):
                for j in range(im.shape[1]):
                    out[i,j] = np.sum(padded[i:i+kh, j:j+kw] * k)
            return out

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    img_path = os.path.join(base_dir, 'Odd_Moon.png')
    out_dir = os.path.join(base_dir, 'zad14_outputs')
    os.makedirs(out_dir, exist_ok=True)

    if not os.path.exists(img_path):
        print('Input image not found:', img_path)
        return

    g = load_image(img_path)

    # define kernels
    h1 = np.ones((3,3), dtype=np.float32)  # 3x3 averaging (unnormalized)
    h2 = np.array([[0, 1, -1]], dtype=np.float32)  # 1x3 horizontal

    conv = convolve2d

    # g1 = g * h1
    g1 = conv(g, h1)
    save_uint8(g1, os.path.join(out_dir, 'g1_g_conv_h1.png'))

    # g2 = g1 * h2
    g2 = conv(g1, h2)
    save_uint8(g2, os.path.join(out_dir, 'g2_g1_conv_h2.png'))

    # h3 = h1 * h2 (convolution of kernels). Use FULL convolution to get true result size
    # h1 is 3x3, h2 is 1x3 horizontal [0,1,-1]
    # For full 2D convolution: h1(3x3) * h2(1x3) -> result is (3+1-1)x(3+3-1) = 3x5
    
    try:
        from scipy.signal import convolve2d as conv_full
        h3 = conv_full(h1, h2, mode='full')
    except:
        # fallback: manual full convolution
        kh1, kw1 = h1.shape
        kh2, kw2 = h2.shape
        out_h = kh1 + kh2 - 1
        out_w = kw1 + kw2 - 1
        h3 = np.zeros((out_h, out_w), dtype=np.float32)
        for i in range(out_h):
            for j in range(out_w):
                for ki in range(kh2):
                    for kj in range(kw2):
                        i1 = i - ki
                        j1 = j - kj
                        if 0 <= i1 < kh1 and 0 <= j1 < kw1:
                            h3[i,j] += h1[i1,j1] * h2[ki,kj]
    
    # print kernel values for debugging
    np.set_printoptions(precision=6, suppress=True)
    print('h3 kernel (raw):')
    print(h3)
    # save h3 as text for inspection
    np.savetxt(os.path.join(out_dir, 'h3_kernel_values.txt'), h3, fmt='%0.8f')
    # save h3 as image (visualize kernel values)
    # Two visualizations:
    # 1) normalized to 0-255 (may be all-black if min==max)
    h3_min = h3.min()
    h3_max = h3.max()
    if abs(h3_max - h3_min) < 1e-12:
        h3_vis = np.zeros_like(h3)
    else:
        h3_vis = (h3 - h3_min) / (h3_max - h3_min) * 255.0
    Image.fromarray(h3_vis.astype(np.uint8)).save(os.path.join(out_dir, 'h3_kernel_visualization.png'))
    # 2) centered visualization (zero -> 128) scaled by max absolute value
    maxabs = np.max(np.abs(h3))
    if maxabs < 1e-12:
        h3_center = np.full_like(h3, 128.0)
    else:
        h3_center = 128.0 + (h3 / maxabs) * 127.0
    Image.fromarray(np.clip(h3_center, 0, 255).astype(np.uint8)).save(os.path.join(out_dir, 'h3_kernel_visualization_centered.png'))

    # g3 = g * h3
    g3 = conv(g, h3)
    save_uint8(g3, os.path.join(out_dir, 'g3_g_conv_h3.png'))

    # also save the original for comparison
    Image.fromarray(np.clip(g,0,255).astype(np.uint8)).save(os.path.join(out_dir, 'original.png'))

    # print basic stats
    def stats(name, arr):
        print(f"{name}: min={arr.min():.2f}, max={arr.max():.2f}, mean={arr.mean():.2f}, std={arr.std():.2f}")

    stats('g (orig)', g)
    stats('g1 (g*h1)', g1)
    stats('g2 (g1*h2)', g2)
    stats('h3 kernel', h3)
    stats('g3 (g*h3)', g3)

    print('Saved outputs to', out_dir)

if __name__ == '__main__':
    main()
