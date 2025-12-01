#!/usr/bin/env python3
"""Zadanie 22: Highboost filtering (unsharp masking) for `nosorozec.png`.

Produces:
- zad22/nosorozec_blurred.png       (Gaussian blurred image)
- zad22/nosorozec_unsharp_mask.png  (visualized mask: centered at mid-gray)
- zad22/nosorozec_highboost.png     (highboost result)

Usage: python3 apply_zad22.py [--sigma 2] [--amount 1.5]
"""
import os
import argparse
from PIL import Image, ImageFilter
import numpy as np


def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def highboost_pil(image, sigma=2.0, amount=1.5):
    """Apply Gaussian blur via PIL, compute unsharp mask, and return (blurred_pil, mask_vis_pil, result_pil).

    image: PIL Image (mode L or RGB)
    sigma: Gaussian blur radius
    amount: multiplier for mask in highboost (result = orig + amount * (orig - blurred))
    """
    blurred = image.filter(ImageFilter.GaussianBlur(radius=sigma))

    orig = np.asarray(image).astype(np.float32)
    blur = np.asarray(blurred).astype(np.float32)

    mask = orig - blur
    result = orig + amount * mask
    result = np.clip(result, 0, 255).astype(np.uint8)

    # Visualize mask: map negative/positive around mid-gray (128)
    maxabs = float(np.maximum(1.0, np.abs(mask).max()))
    # scale mask to [-0.5, 0.5] then shift to [0,1], then to [0,255]
    mask_vis = ((mask / (2.0 * maxabs)) + 0.5) * 255.0
    mask_vis = np.clip(mask_vis, 0, 255).astype(np.uint8)

    # Convert back to PIL images
    blurred_pil = Image.fromarray(blur.astype(np.uint8)) if isinstance(blur, np.ndarray) else blurred
    mask_pil = Image.fromarray(mask_vis)
    result_pil = Image.fromarray(result)
    return blurred_pil, mask_pil, result_pil


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sigma', type=float, default=2.0, help='Gaussian blur sigma / radius')
    parser.add_argument('--amount', type=float, default=1.5, help='Highboost amount (multiplier for mask)')
    args = parser.parse_args()

    base_dir = os.path.dirname(__file__)
    input_path = os.path.join(base_dir, '..', 'nosorozec.png')
    # fallback: try same folder
    if not os.path.exists(input_path):
        input_path = os.path.join(base_dir, 'nosorozec.png')

    if not os.path.exists(input_path):
        print('ERROR: input image not found: nosorozec.png')
        return

    out_dir = base_dir
    ensure_dir(out_dir)

    img = Image.open(input_path).convert('RGB')

    blurred_pil, mask_pil, result_pil = highboost_pil(img, sigma=args.sigma, amount=args.amount)

    blurred_path = os.path.join(out_dir, 'nosorozec_blurred.png')
    mask_path = os.path.join(out_dir, 'nosorozec_unsharp_mask.png')
    result_path = os.path.join(out_dir, 'nosorozec_highboost.png')

    blurred_pil.save(blurred_path)
    mask_pil.save(mask_path)
    result_pil.save(result_path)

    # Print simple statistics
    arr_orig = np.asarray(img).astype(np.float32)
    arr_res = np.asarray(result_pil).astype(np.float32)
    diff = arr_res - arr_orig
    print('Input:', input_path)
    print('Saved blurred :', blurred_path)
    print('Saved mask    :', mask_path)
    print('Saved result  :', result_path)
    print('Result stats (min,max,mean,std):', float(arr_res.min()), float(arr_res.max()), float(arr_res.mean()), float(arr_res.std()))
    print('Diff stats   (min,max,mean,std):', float(diff.min()), float(diff.max()), float(diff.mean()), float(diff.std()))


if __name__ == '__main__':
    main()
