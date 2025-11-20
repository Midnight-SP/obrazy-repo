#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zadanie 17: Okienkowanie obrazu
Pipeline przetwarzania zaszumionego obrazu ptaki.png:
(a) Okno sinusoidalne
(b) Filtr uśredniający 3×3
(c) Korekcja gamma dla dopasowania średniej jasności
(d) Bezpośrednie uśrednianie dla porównania
"""

import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from scipy import ndimage

def sinusoidal_window_2d(height, width):
    """
    Utworzenie 2D okna sinusoidalnego (okna Hanna).
    Okno sinusoidalne: w(x, y) = sin²(πx/W) × sin²(πy/H)
    gdzie x ∈ [0, W-1], y ∈ [0, H-1]
    """
    # Wektory 1D
    x = np.arange(width)
    y = np.arange(height)
    
    # Okna 1D sinusoidalne (sin²)
    window_x = np.sin(np.pi * x / (width - 1)) ** 2
    window_y = np.sin(np.pi * y / (height - 1)) ** 2
    
    # Rozszerzenie do 2D przez iloczyn zewnętrzny
    window_2d = np.outer(window_y, window_x)
    
    return window_2d

def apply_window(img_array, window):
    """Zastosowanie okna do obrazu (mnożenie)."""
    return (img_array.astype(np.float32) * window).astype(np.uint8)

def averaging_filter_3x3(img_array):
    """
    Filtr uśredniający 3×3.
    g'(m, n) = (1/9) × Σ_{i=-1}^{1} Σ_{j=-1}^{1} g(m-i, n-j)
    """
    # Kernel uśredniający 3×3
    kernel = np.ones((3, 3)) / 9.0
    
    # Konwolucja
    img_filtered = ndimage.convolve(img_array.astype(np.float32), kernel, mode='reflect')
    
    return img_filtered.astype(np.uint8)

def gamma_correction(img_array, gamma):
    """
    Korekcja gamma: g_out = 255 × (g_in / 255)^γ
    """
    # Normalizacja do [0, 1]
    img_normalized = img_array.astype(np.float32) / 255.0
    
    # Zastosuj transformację gamma
    img_gamma = np.power(img_normalized, gamma)
    
    # Przywróć do [0, 255]
    return (img_gamma * 255).astype(np.uint8)

def find_gamma_for_mean(img_array, target_mean, tolerance=0.5):
    """
    Znajdź współczynnik gamma, który da średnią jasność zbliżoną do target_mean.
    Używa prostej metody bisekcji.
    """
    gamma_low = 0.1
    gamma_high = 5.0
    gamma_mid = 1.0
    mean_test = target_mean
    
    for _ in range(50):  # maksymalnie 50 iteracji
        gamma_mid = (gamma_low + gamma_high) / 2
        img_test = gamma_correction(img_array, gamma_mid)
        mean_test = img_test.mean()
        
        if abs(mean_test - target_mean) < tolerance:
            return gamma_mid, mean_test
        
        if mean_test < target_mean:
            gamma_high = gamma_mid
        else:
            gamma_low = gamma_mid
    
    # Zwróć najlepsze przybliżenie
    return gamma_mid, mean_test

def save_image_with_stats(img_array, filename, title):
    """Zapisz obraz wraz z statystykami."""
    img_pil = Image.fromarray(img_array)
    img_pil.save(filename)
    
    mean = img_array.mean()
    std = img_array.std()
    print(f"  {title}:")
    print(f"    - Plik: {filename}")
    print(f"    - Średnia: {mean:.2f}")
    print(f"    - Odchylenie std: {std:.2f}")

def visualize_window(window, filename):
    """Wizualizacja okna 2D."""
    plt.figure(figsize=(8, 6))
    plt.imshow(window, cmap='hot', interpolation='nearest')
    plt.colorbar(label='Wartość okna')
    plt.title('Okno sinusoidalne (sin²(πx/W) × sin²(πy/H))')
    plt.xlabel('x (kolumny)')
    plt.ylabel('y (wiersze)')
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close()
    print(f"  Zapisano wizualizację okna: {filename}")

def main():
    print("="*60)
    print("Zadanie 17: Okienkowanie obrazu")
    print("="*60)
    
    # Wczytaj obraz
    img_path = '../ptaki.png'
    img = Image.open(img_path).convert('L')
    img_original = np.array(img)
    
    print(f"\nWczytano obraz: {img_original.shape}")
    print(f"Zakres wartości: [{img_original.min()}, {img_original.max()}]")
    print(f"Średnia: {img_original.mean():.2f}")
    print(f"Odchylenie std: {img_original.std():.2f}")
    
    height, width = img_original.shape
    original_mean = img_original.mean()
    
    # (a) Okno sinusoidalne
    print("\n" + "="*60)
    print("(a) Przetwarzanie oknem sinusoidalnym")
    print("="*60)
    
    window = sinusoidal_window_2d(height, width)
    print(f"Utworzono okno sinusoidalne {height}×{width}")
    print(f"Zakres wartości okna: [{window.min():.4f}, {window.max():.4f}]")
    
    # Wizualizacja okna
    visualize_window(window, 'window_sinusoidal.png')
    
    # Zastosuj okno
    img_windowed = apply_window(img_original, window)
    save_image_with_stats(img_windowed, 'step_a_windowed.png', 
                          'Obraz po zastosowaniu okna sinusoidalnego')
    
    # (b) Filtr uśredniający 3×3
    print("\n" + "="*60)
    print("(b) Filtr uśredniający 3×3 na obrazie z oknem")
    print("="*60)
    print("Kernel: (1/9) × [[1,1,1], [1,1,1], [1,1,1]]")
    
    img_filtered = averaging_filter_3x3(img_windowed)
    save_image_with_stats(img_filtered, 'step_b_averaged.png',
                          'Obraz po filtrze uśredniającym')
    
    # (c) Korekcja gamma
    print("\n" + "="*60)
    print("(c) Korekcja gamma dla dopasowania średniej jasności")
    print("="*60)
    print(f"Średnia oryginalna: {original_mean:.2f}")
    print(f"Średnia przed korektą: {img_filtered.mean():.2f}")
    print("Szukanie optymalnego współczynnika gamma...")
    
    optimal_gamma, achieved_mean = find_gamma_for_mean(img_filtered, original_mean)
    img_gamma = gamma_correction(img_filtered, optimal_gamma)
    
    print(f"\nZnaleziony współczynnik: γ = {optimal_gamma:.4f}")
    print(f"Osiągnięta średnia: {achieved_mean:.2f}")
    print(f"Różnica od oryginału: {abs(achieved_mean - original_mean):.2f}")
    
    save_image_with_stats(img_gamma, 'step_c_gamma_corrected.png',
                          'Obraz po korekcji gamma')
    
    # (d) Bezpośrednie uśrednianie na oryginale
    print("\n" + "="*60)
    print("(d) Bezpośrednie uśrednianie na obrazie oryginalnym")
    print("="*60)
    
    img_direct_avg = averaging_filter_3x3(img_original)
    save_image_with_stats(img_direct_avg, 'step_d_direct_averaged.png',
                          'Obraz po bezpośrednim uśrednianiu')
    
    # Porównanie
    print("\n" + "="*60)
    print("PORÓWNANIE METOD")
    print("="*60)
    print("\nStatystyki:")
    print(f"  Oryginalny:                  mean={img_original.mean():.2f}, std={img_original.std():.2f}")
    print(f"  Po oknie+filtr+gamma (c):    mean={img_gamma.mean():.2f}, std={img_gamma.std():.2f}")
    print(f"  Po bezpośrednim filtrze (d): mean={img_direct_avg.mean():.2f}, std={img_direct_avg.std():.2f}")
    
    print("\nInterpretacja:")
    print("  (c) Okienkowanie przed filtrowaniem:")
    print("      - Okno sinusoidalne redukuje artefakty na brzegach")
    print("      - Zmniejsza wagę zaszumionych obszarów brzegowych")
    print("      - Korekcja gamma przywraca oryginalną jasność")
    print("      - Lepsze zachowanie jakości w centrum obrazu")
    print("\n  (d) Bezpośrednie filtrowanie:")
    print("      - Prostsze, szybsze")
    print("      - Równomierne traktowanie całego obrazu")
    print("      - Możliwe artefakty na brzegach jeśli szum nierównomierny")
    print("      - Zachowuje pełną jasność bez korekcji")
    
    print("\n✓ Wszystkie kroki przetwarzania zakończone pomyślnie!")

if __name__ == '__main__':
    main()
