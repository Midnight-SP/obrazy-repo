#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zadanie 7: Wyrównanie histogramu i hiperbolizacja
Dla obrazu RezydencjaDiabla.png:
(a) Wyznaczenie skumulowanego histogramu
(b) Wyrównanie histogramu + wartości H_equal(40/45/50)
(c) Hiperbolizacja z α=-1/3 + wartości H_hyper(40/45/50)
"""

import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

def compute_histogram(img_array):
    """Oblicz histogram dla obrazu w skali szarości (0-255)."""
    hist = np.zeros(256, dtype=int)
    for value in range(256):
        hist[value] = np.sum(img_array == value)
    return hist

def compute_cumulative_histogram(hist):
    """Oblicz skumulowany histogram."""
    return np.cumsum(hist)

def histogram_equalization(img_array):
    """
    Wyrównanie histogramu.
    Transformacja: H_equal(g) = round((L-1) * CDF(g) / N)
    gdzie L=256, CDF - skumulowany histogram, N - liczba pikseli
    """
    hist = compute_histogram(img_array)
    cdf = compute_cumulative_histogram(hist)
    
    # Normalizacja CDF do zakresu [0, 255]
    N = img_array.size  # całkowita liczba pikseli
    cdf_normalized = (255 * cdf / N).astype(np.uint8)
    
    # Mapowanie: dla każdego piksela o wartości g -> H_equal(g) = cdf_normalized[g]
    img_equalized = cdf_normalized[img_array]
    
    return img_equalized, cdf_normalized

def histogram_hyperbolization(img_array, alpha=-1/3):
    """
    Hiperbolizacja histogramu z parametrem α.
    Transformacja: H_hyper(g) = round((L-1) * [CDF(g)/N]^(1/(1+α)))
    """
    hist = compute_histogram(img_array)
    cdf = compute_cumulative_histogram(hist)
    
    N = img_array.size
    # Normalizacja CDF do [0, 1]
    cdf_norm = cdf / N
    
    # Hiperbolizacja: podnieś do potęgi 1/(1+α)
    exponent = 1 / (1 + alpha)
    cdf_hyper = np.power(cdf_norm, exponent)
    
    # Skalowanie do [0, 255]
    cdf_hyper_scaled = (255 * cdf_hyper).astype(np.uint8)
    
    # Mapowanie
    img_hyper = cdf_hyper_scaled[img_array]
    
    return img_hyper, cdf_hyper_scaled

def plot_histogram(img_array, title, filename):
    """Rysuj histogram obrazu."""
    hist = compute_histogram(img_array)
    
    plt.figure(figsize=(10, 4))
    plt.bar(range(256), hist, width=1.0, color='gray', edgecolor='black', linewidth=0.5)
    plt.title(title)
    plt.xlabel('Wartość szarości')
    plt.ylabel('Liczba pikseli')
    plt.xlim([0, 255])
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close()
    print(f"Zapisano histogram: {filename}")

def main():
    # Wczytaj obraz
    img_path = '../RezydencjaDiabla.png'
    img = Image.open(img_path).convert('L')  # konwersja do skali szarości
    img_array = np.array(img)
    
    print(f"Wczytano obraz: {img_array.shape}")
    print(f"Zakres wartości: [{img_array.min()}, {img_array.max()}]")
    
    # (a) Skumulowany histogram
    hist_original = compute_histogram(img_array)
    cdf_original = compute_cumulative_histogram(hist_original)
    
    # Zapisz oryginalny histogram
    plot_histogram(img_array, 'Histogram oryginalny - RezydencjaDiabla.png', 
                   'histogram_original.png')
    
    # Zapisz skumulowany histogram
    plt.figure(figsize=(10, 4))
    plt.plot(range(256), cdf_original, color='blue', linewidth=2)
    plt.title('Skumulowany histogram - RezydencjaDiabla.png')
    plt.xlabel('Wartość szarości')
    plt.ylabel('Liczba pikseli (skumulowana)')
    plt.xlim([0, 255])
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('histogram_cumulative.png', dpi=150)
    plt.close()
    print("Zapisano skumulowany histogram: histogram_cumulative.png")
    
    # (b) Wyrównanie histogramu
    print("\n(b) Wyrównanie histogramu:")
    img_equalized, mapping_equal = histogram_equalization(img_array)
    
    # Raportuj wartości dla g = 40, 45, 50
    print(f"  H_equal(40) = {mapping_equal[40]}")
    print(f"  H_equal(45) = {mapping_equal[45]}")
    print(f"  H_equal(50) = {mapping_equal[50]}")
    
    # Zapisz wyrównany obraz
    img_equal_pil = Image.fromarray(img_equalized)
    img_equal_pil.save('RezydencjaDiabla_equalized.png')
    print("Zapisano wyrównany obraz: RezydencjaDiabla_equalized.png")
    
    # Zapisz histogram wyrównanego obrazu
    plot_histogram(img_equalized, 'Histogram po wyrównaniu', 
                   'histogram_equalized.png')
    
    # (c) Hiperbolizacja histogramu
    print("\n(c) Hiperbolizacja histogramu (α = -1/3):")
    alpha = -1/3
    img_hyper, mapping_hyper = histogram_hyperbolization(img_array, alpha)
    
    # Raportuj wartości dla g = 40, 45, 50
    print(f"  H_hyper(40) = {mapping_hyper[40]}")
    print(f"  H_hyper(45) = {mapping_hyper[45]}")
    print(f"  H_hyper(50) = {mapping_hyper[50]}")
    
    # Zapisz zhiperbolizowany obraz
    img_hyper_pil = Image.fromarray(img_hyper)
    img_hyper_pil.save('RezydencjaDiabla_hyperbolized.png')
    print("Zapisano zhiperbolizowany obraz: RezydencjaDiabla_hyperbolized.png")
    
    # Zapisz histogram zhiperbolizowanego obrazu
    plot_histogram(img_hyper, f'Histogram po hiperbolizacji (α={alpha:.3f})', 
                   'histogram_hyperbolized.png')
    
    print("\n✓ Wszystkie obrazy i histogramy wygenerowane pomyślnie!")

if __name__ == '__main__':
    main()
