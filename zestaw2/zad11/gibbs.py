#!/usr/bin/env python3
"""
Zadanie 11: Efekt Gibbsa
a) Utworzyć kwadratowy obraz (potęga 2) z białym paskiem na czarnym tle.
b) Aproksymacja widma przez dwa skończone szeregi Fouriera o różnych długościach,
   rekonstrukcja obrazów (IFFT) i profile liniowe → pokazanie efektu Gibbsa.

Obraz: pionowy biały pasek (poziomy też możliwy), rozm. 256×256.
Fale płaskie mają kierunek prostopadły do paska (dla pionowego paska → fale poziome).

Skrypt:
- generuje obraz paska
- oblicza FFT
- tworzy dwie aproksymacje: zatrzymując niskie częstotliwości (małe i większe "pudełko")
- wykonuje IFFT
- tworzy profile liniowe poziome przez środek obrazu (rząd 128) dla oryginału i rekonstrukcji
- wizualizuje efekt Gibbsa (oscylacje przy ostrych krawędziach)
"""
import os
import sys
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def create_stripe_image(size=256, stripe_width=40):
    """Create vertical white stripe on black background."""
    img = np.zeros((size, size), dtype=np.uint8)
    c = size // 2
    half = stripe_width // 2
    img[:, c - half:c + half] = 255
    return img


def bandlimit_spectrum(Fshift, keep_fraction):
    """Zero out all but central keep_fraction of spectrum (box filter in freq domain)."""
    h, w = Fshift.shape
    mask = np.zeros_like(Fshift, dtype=np.float32)
    cy, cx = h // 2, w // 2
    hy = int(h * keep_fraction / 2)
    hx = int(w * keep_fraction / 2)
    mask[cy - hy:cy + hy, cx - hx:cx + hx] = 1.0
    return Fshift * mask


def reconstruct(Fshift):
    """Inverse FFT from shifted spectrum."""
    F = np.fft.ifftshift(Fshift)
    img = np.fft.ifft2(F)
    return np.real(img)


def save_image(arr, path, normalize=True):
    a = np.asarray(arr, dtype=np.float32)
    if normalize:
        mn, mx = float(np.min(a)), float(np.max(a))
        if mx > mn:
            a = (a - mn) / (mx - mn) * 255.0
        else:
            a[:] = 0
    a = np.clip(a, 0, 255).astype(np.uint8)
    Image.fromarray(a, mode='L').save(path)


def plot_profiles(profiles_dict, out_path, title="Profile liniowe poziome"):
    """Plot line profiles (horizontal through center) for comparison."""
    plt.figure(figsize=(10, 6))
    for label, prof in profiles_dict.items():
        plt.plot(prof, label=label, linewidth=1.5)
    plt.xlabel('Pozycja x [px]')
    plt.ylabel('Intensywność')
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def main():
    folder = os.path.dirname(os.path.abspath(__file__))
    size = 256
    stripe_w = 40

    # 1) Generuj obraz paska
    stripe = create_stripe_image(size, stripe_w)
    save_image(stripe, os.path.join(folder, 'stripe_original.png'), normalize=False)
    print(f"Utworzono obraz paska: {size}x{size}, pionowy pasek szerokości {stripe_w} px")

    # Kierunek fal płaskich: prostopadły do paska → dla pionowego paska są to fale POZIOME
    # (w widmie FFT silne linie poziome odpowiadają strukturom pionowym w obrazie i na odwrót)

    # 2) FFT
    F = np.fft.fft2(stripe.astype(np.float32))
    Fshift = np.fft.fftshift(F)
    mag = np.abs(Fshift)
    spec_log = np.log1p(mag)
    save_image(spec_log, os.path.join(folder, 'stripe_spectrum.png'), normalize=True)
    print("Obliczono widmo FFT")

    # 3) Aproksymacje: zatrzymaj tylko niskie częstotliwości (dwie różne frakcje)
    # Mniejsza frakcja → mniej składowych → silniejszy efekt Gibbsa
    fracs = [0.2, 0.5]  # np. 20% i 50% widma (10% i 25% promienia)
    recons = {}
    profiles = {'Oryginał': stripe[size // 2, :]}

    for frac in fracs:
        Fapprox = bandlimit_spectrum(Fshift, frac)
        spec_approx_log = np.log1p(np.abs(Fapprox))
        save_image(spec_approx_log, os.path.join(folder, f'stripe_spectrum_frac{int(frac*100)}.png'), normalize=True)

        recon = reconstruct(Fapprox)
        label = f'Rekonstrukcja {int(frac*100)}%'
        recons[label] = recon
        save_image(recon, os.path.join(folder, f'stripe_recon_frac{int(frac*100)}.png'), normalize=True)
        profiles[label] = recon[size // 2, :]
        print(f"Rekonstrukcja z {int(frac*100)}% widma zapisana")

    # 4) Profile liniowe poziome przez środek (rząd 128)
    plot_profiles(profiles, os.path.join(folder, 'profiles.png'), title="Profile poziome przez środek obrazu")
    print("Wygenerowano profile liniowe")

    # 5) Zoom na krawędź (lewy brzeg paska) dla lepszej widoczności oscylacji Gibbsa
    c = size // 2
    hw = stripe_w // 2
    left_edge = c - hw
    zoom_range = range(max(0, left_edge - 30), min(size, left_edge + 30))
    profiles_zoom = {k: v[zoom_range] for k, v in profiles.items()}
    plot_profiles(profiles_zoom, os.path.join(folder, 'profiles_zoom.png'), title="Profile (zoom na lewą krawędź paska)")
    print("Wygenerowano zoom profili na krawędź")

    print("\nZakończono zadanie 11. Efekt Gibbsa widoczny jako oscylacje (over/undershoot) przy ostrych krawędziach.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
