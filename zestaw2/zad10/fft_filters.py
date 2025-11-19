#!/usr/bin/env python3
"""
Zadanie 10: DFT (FFT) i filtracja widma A/B/C/D

- Wejście: koszulaA.png, koszulaB.png (skala szarości zalecana; konwersja robiona wczytywaniem)
- Maski: A.png, B.png, C.png, D.png — czarne obszary są wycinane (0), białe przepuszczane (1).
- Wyjście: widmo mocy (log), użyta maska (po dopasowaniu rozmiaru) i obraz po filtracji (IFFT).

Uwaga: Maski są dopasowywane rozmiarem do obrazu (nearest). Po stronie widma pracujemy na fftshift (DC w centrum),
więc maski A..D powinny być narysowane z założeniem, że centrum obrazu to częstotliwości niskie.
"""
import os
import sys
import numpy as np
from PIL import Image


def load_gray(path):
    img = Image.open(path).convert('L')
    return np.asarray(img, dtype=np.float32)


def save_gray(arr, path, normalize=True):
    a = np.asarray(arr, dtype=np.float32)
    if normalize:
        mn, mx = float(np.min(a)), float(np.max(a))
        if mx > mn:
            a = (a - mn) / (mx - mn)
        else:
            a[:] = 0
        a = (a * 255.0).clip(0, 255).astype(np.uint8)
    else:
        a = np.clip(a, 0, 255).astype(np.uint8)
    Image.fromarray(a, mode='L').save(path)


def fft2_log_spectrum(gray):
    F = np.fft.fft2(gray)
    Fshift = np.fft.fftshift(F)
    mag = np.abs(Fshift)
    spec = np.log1p(mag)
    return F, Fshift, spec


def ifft2_from_shift(Fshift):
    F = np.fft.ifftshift(Fshift)
    img = np.fft.ifft2(F)
    return np.real(img)


def load_mask(mask_path, target_shape):
    """Load mask image and convert to binary keep-mask (1=pass, 0=block), resized to target_shape (h,w)."""
    m = Image.open(mask_path).convert('L')
    # Resize to match spectrum shape
    h, w = target_shape
    m = m.resize((w, h), resample=Image.NEAREST)
    m_arr = np.asarray(m, dtype=np.float32)
    # Threshold: white->1 (keep), black->0 (remove). Tolerate antialiasing by >128
    keep = (m_arr > 128).astype(np.float32)
    return keep


def process_image(img_path, masks_dir):
    base = os.path.splitext(os.path.basename(img_path))[0]
    gray = load_gray(img_path)
    F, Fshift, spec = fft2_log_spectrum(gray)

    out_dir = os.path.join(os.path.dirname(img_path), 'out')
    os.makedirs(out_dir, exist_ok=True)

    # Save spectrum for reference
    save_gray(spec, os.path.join(out_dir, f'{base}-spectrum.png'), normalize=True)

    # Apply each mask A..D
    for label in ['A', 'B', 'C', 'D']:
        mask_path = os.path.join(masks_dir, f'{label}.png')
        if not os.path.exists(mask_path):
            print(f'Brak maski: {mask_path} — pomijam {label}')
            continue
        M = load_mask(mask_path, Fshift.shape[:2])
        # Save the resized/thresholded mask visualization
        save_gray(M * 255.0, os.path.join(out_dir, f'{base}-mask-{label}.png'), normalize=False)

        Fmasked = Fshift * M
        spec_masked = np.log1p(np.abs(Fmasked))
        save_gray(spec_masked, os.path.join(out_dir, f'{base}-spectrum-{label}.png'), normalize=True)

        recon = ifft2_from_shift(Fmasked)
        # Normalize reconstruction to 0..255 for saving
        save_gray(recon, os.path.join(out_dir, f'{base}-filtered-{label}.png'), normalize=True)

        print(f'{base}: przetworzono maskę {label}')


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    folder = os.path.dirname(os.path.abspath(__file__))
    imgs = [os.path.join(folder, 'koszulaA.png'), os.path.join(folder, 'koszulaB.png')]
    for p in imgs:
        if not os.path.exists(p):
            print('Brak pliku:', p)
            return 1
    # Masks assumed in same folder: A.png, B.png, C.png, D.png
    for m in ['A.png', 'B.png', 'C.png', 'D.png']:
        if not os.path.exists(os.path.join(folder, m)):
            print('Brak maski:', m)
            return 1

    for p in imgs:
        process_image(p, folder)
    print('Zakończono przetwarzanie FFT i filtrację dla koszulaA/B.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
