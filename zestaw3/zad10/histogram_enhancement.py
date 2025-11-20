#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zadanie 10: Zwiększenie kontrastu poprzez operacje punktowe oparte na histogramie
Pipeline przetwarzania obrazu Całunu Turyńskiego w celu poprawy widoczności twarzy.
"""

import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from scipy import ndimage

def compute_histogram(img_array):
    """Oblicz histogram dla obrazu w skali szarości (0-255)."""
    hist = np.zeros(256, dtype=int)
    for value in range(256):
        hist[value] = np.sum(img_array == value)
    return hist

def plot_histogram(img_array, title, filename, show_stats=True):
    """Rysuj histogram obrazu z opcjonalnymi statystykami."""
    hist = compute_histogram(img_array)
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(range(256), hist, width=1.0, color='gray', edgecolor='black', linewidth=0.3)
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.set_xlabel('Wartość szarości')
    ax.set_ylabel('Liczba pikseli')
    ax.set_xlim([0, 255])
    ax.grid(True, alpha=0.3)
    
    if show_stats:
        # Dodaj statystyki jako tekst
        stats_text = f"Min: {img_array.min()}\n"
        stats_text += f"Max: {img_array.max()}\n"
        stats_text += f"Mean: {img_array.mean():.2f}\n"
        stats_text += f"Std: {img_array.std():.2f}"
        ax.text(0.98, 0.97, stats_text, transform=ax.transAxes,
                verticalalignment='top', horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
                fontsize=9, family='monospace')
    
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close()
    print(f"Zapisano histogram: {filename}")

def save_image_with_histogram(img_array, img_filename, hist_filename, title):
    """Zapisz obraz i jego histogram."""
    # Zapisz obraz
    img_pil = Image.fromarray(img_array)
    img_pil.save(img_filename)
    print(f"Zapisano obraz: {img_filename}")
    
    # Zapisz histogram
    plot_histogram(img_array, title, hist_filename)

def contrast_stretching(img_array, lower_percentile=1, upper_percentile=99):
    """
    Rozciąganie kontrastu - mapowanie zakresu wartości na [0, 255].
    Używa percentyli zamiast min/max by uniknąć wpływu pojedynczych outlierów.
    """
    p_low = np.percentile(img_array, lower_percentile)
    p_high = np.percentile(img_array, upper_percentile)
    
    print(f"  Percentyl {lower_percentile}%: {p_low:.2f}")
    print(f"  Percentyl {upper_percentile}%: {p_high:.2f}")
    
    # Mapowanie liniowe
    img_stretched = np.clip((img_array - p_low) * 255.0 / (p_high - p_low), 0, 255)
    
    return img_stretched.astype(np.uint8)

def histogram_equalization(img_array):
    """Wyrównanie histogramu."""
    hist = compute_histogram(img_array)
    cdf = np.cumsum(hist)
    
    # Normalizacja CDF do zakresu [0, 255]
    cdf_normalized = (255 * cdf / cdf[-1]).astype(np.uint8)
    
    # Mapowanie
    img_equalized = cdf_normalized[img_array]
    
    return img_equalized

def clahe(img_array, clip_limit=2.0, tile_size=8):
    """
    Contrast Limited Adaptive Histogram Equalization (CLAHE).
    Lokalne wyrównanie histogramu z ograniczeniem wzmocnienia szumu.
    """
    from skimage import exposure
    
    # CLAHE wymaga wartości float w [0, 1]
    img_float = img_array.astype(float) / 255.0
    
    # Zastosuj CLAHE
    img_clahe = exposure.equalize_adapthist(img_float, 
                                            clip_limit=clip_limit,
                                            nbins=256)
    
    # Przywróć do uint8
    return (img_clahe * 255).astype(np.uint8)

def gamma_correction(img_array, gamma=1.5):
    """
    Korekcja gamma - nieliniowa transformacja jasności.
    gamma < 1: rozjaśnia ciemne obszary
    gamma > 1: przyciemnia jasne obszary
    """
    # Normalizacja do [0, 1]
    img_normalized = img_array.astype(float) / 255.0
    
    # Zastosuj transformację gamma
    img_gamma = np.power(img_normalized, gamma)
    
    # Przywróć do uint8
    return (img_gamma * 255).astype(np.uint8)

def main():
    # Wczytaj obraz
    img_path = '../CalunTurynski.png'
    img = Image.open(img_path).convert('L')
    img_original = np.array(img)
    
    print("="*60)
    print("Zadanie 10: Pipeline przetwarzania Całunu Turyńskiego")
    print("="*60)
    print(f"\nWczytano obraz: {img_original.shape}")
    print(f"Zakres wartości: [{img_original.min()}, {img_original.max()}]")
    print(f"Średnia: {img_original.mean():.2f}")
    print(f"Odchylenie std: {img_original.std():.2f}")
    
    # Krok 0: Oryginalny obraz i histogram
    print("\n" + "="*60)
    print("Krok 0: Oryginalny obraz")
    print("="*60)
    save_image_with_histogram(img_original, 
                               'step0_original.png',
                               'step0_histogram.png',
                               'Histogram - Obraz oryginalny')
    
    # Krok 1: Rozciąganie kontrastu
    print("\n" + "="*60)
    print("Krok 1: Rozciąganie kontrastu (percentyle 1-99)")
    print("="*60)
    img_stretched = contrast_stretching(img_original, lower_percentile=1, upper_percentile=99)
    save_image_with_histogram(img_stretched,
                               'step1_contrast_stretched.png',
                               'step1_histogram.png',
                               'Histogram - Po rozciągnięciu kontrastu')
    
    # Krok 2: Wyrównanie histogramu
    print("\n" + "="*60)
    print("Krok 2: Wyrównanie histogramu (Histogram Equalization)")
    print("="*60)
    img_equalized = histogram_equalization(img_stretched)
    save_image_with_histogram(img_equalized,
                               'step2_equalized.png',
                               'step2_histogram.png',
                               'Histogram - Po wyrównaniu histogramu')
    
    # Krok 3: CLAHE (opcjonalne, jeśli scikit-image dostępne)
    print("\n" + "="*60)
    print("Krok 3: CLAHE (Contrast Limited Adaptive HE)")
    print("="*60)
    try:
        img_clahe = clahe(img_original, clip_limit=3.0, tile_size=8)
        save_image_with_histogram(img_clahe,
                                   'step3_clahe.png',
                                   'step3_histogram.png',
                                   'Histogram - Po CLAHE (clip_limit=3.0)')
        print("  CLAHE wykonane pomyślnie (alternatywna metoda)")
    except ImportError:
        print("  scikit-image nie dostępne, pomijam CLAHE")
        print("  (CLAHE jest alternatywną metodą, nie jest wymagane)")
    
    # Krok 4: Korekcja gamma na wyrównanym obrazie
    print("\n" + "="*60)
    print("Krok 4: Korekcja gamma (γ=0.7) na wyrównanym obrazie")
    print("="*60)
    img_gamma = gamma_correction(img_equalized, gamma=0.7)
    save_image_with_histogram(img_gamma,
                               'step4_gamma_corrected.png',
                               'step4_histogram.png',
                               'Histogram - Po korekcji gamma (γ=0.7)')
    
    # Podsumowanie
    print("\n" + "="*60)
    print("PODSUMOWANIE")
    print("="*60)
    print("Wygenerowane kroki przetwarzania:")
    print("  0. Oryginalny obraz (niski kontrast, wąski zakres)")
    print("  1. Rozciąganie kontrastu (rozszerza zakres do [0, 255])")
    print("  2. Wyrównanie histogramu (równomierne rozłożenie wartości)")
    print("  3. CLAHE (lokalne wyrównanie z ograniczeniem szumu) *opcjonalne*")
    print("  4. Korekcja gamma (rozjaśnienie ciemnych obszarów)")
    print("\nNajlepszy rezultat: Krok 2 lub 4 (w zależności od preferencji)")
    print("\n✓ Wszystkie obrazy i histogramy wygenerowane pomyślnie!")

if __name__ == '__main__':
    main()
