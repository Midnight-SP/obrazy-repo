#!/usr/bin/env python3
"""
Zadanie 4: Binaryzacja histogramu - metoda Otsu
(a) Progowanie globalne Otsu
(b) Iteracyjne trójklasowe progowanie Otsu z warunkiem Δ < 2
(c) Progowanie lokalne Otsu w oknie 11×11 (symetryczne odbicie na brzegach)
"""
import os
import sys
import numpy as np
from PIL import Image


def load_gray(path):
    img = Image.open(path).convert('L')
    return np.asarray(img, dtype=np.uint8)


def save_binary(arr, path):
    """Save binary image (0 or 255)."""
    a = np.asarray(arr, dtype=np.uint8)
    Image.fromarray(a, mode='L').save(path)


def otsu_threshold(gray):
    """
    Compute Otsu's threshold for grayscale image.
    Returns optimal threshold T (0-255).
    """
    hist, _ = np.histogram(gray.flatten(), bins=256, range=(0, 256))
    total = gray.size
    
    # Normalizuj histogram (prawdopodobieństwa)
    hist = hist.astype(np.float64) / total
    
    #累積 sum i mean
    cum_sum = np.cumsum(hist)
    cum_mean = np.cumsum(hist * np.arange(256))
    global_mean = cum_mean[-1]
    
    # Between-class variance dla każdego możliwego progu
    w0 = cum_sum
    w1 = 1.0 - w0
    
    # Unikaj dzielenia przez zero
    mean0 = np.zeros(256)
    mean1 = np.zeros(256)
    
    mask0 = w0 > 0
    mask1 = w1 > 0
    
    mean0[mask0] = cum_mean[mask0] / w0[mask0]
    mean1[mask1] = (global_mean - cum_mean[mask1]) / w1[mask1]
    
    # Between-class variance
    var_between = w0 * w1 * (mean0 - mean1) ** 2
    
    # Znajdź prog maksymalizujący wariancję międzyklasową
    threshold = np.argmax(var_between)
    return int(threshold)


def apply_threshold(gray, T):
    """Apply binary threshold: pixel >= T -> 255, else 0."""
    binary = np.where(gray >= T, 255, 0).astype(np.uint8)
    return binary


def otsu_three_class_iterative(gray, delta_threshold=2):
    """
    Iteracyjne trójklasowe progowanie Otsu.
    Dzieli obraz na 3 klasy: ciemne, średnie, jasne.
    Iteruje aż różnica progów między iteracjami < delta_threshold.
    
    Zwraca tuple (T1, T2, result_image) gdzie:
    - T1: próg między klasą ciemną a średnią
    - T2: próg między klasą średnią a jasną
    - result_image: obraz z wartościami 0 (ciemna), 128 (średnia), 255 (jasna)
    """
    # Inicjalizacja progów (1/3 i 2/3 zakresu)
    T1_old, T2_old = 85, 170
    max_iter = 100
    
    for iteration in range(max_iter):
        # Podziel na 3 klasy
        class0 = gray[gray < T1_old]           # ciemna
        class1 = gray[(gray >= T1_old) & (gray < T2_old)]  # średnia
        class2 = gray[gray >= T2_old]          # jasna
        
        # Oblicz nowe progi jako średnie między średnimi klas
        if len(class0) > 0 and len(class1) > 0:
            mean0 = np.mean(class0)
            mean1 = np.mean(class1)
            T1_new = int((mean0 + mean1) / 2)
        else:
            T1_new = T1_old
        
        if len(class1) > 0 and len(class2) > 0:
            mean1 = np.mean(class1)
            mean2 = np.mean(class2)
            T2_new = int((mean1 + mean2) / 2)
        else:
            T2_new = T2_old
        
        # Sprawdź warunek stopu
        delta = max(abs(T1_new - T1_old), abs(T2_new - T2_old))
        if delta < delta_threshold:
            T1_old, T2_old = T1_new, T2_new
            break
        
        T1_old, T2_old = T1_new, T2_new
    
    # Utwórz obraz wynikowy z 3 poziomami
    result = np.zeros_like(gray, dtype=np.uint8)
    result[gray < T1_old] = 0
    result[(gray >= T1_old) & (gray < T2_old)] = 128
    result[gray >= T2_old] = 255
    
    return T1_old, T2_old, result


def otsu_local(gray, window_size=11):
    """
    Lokalne progowanie Otsu w oknie window_size×window_size.
    Symetryczne odbicie na brzegach (np.pad mode='reflect').
    """
    h, w = gray.shape
    half = window_size // 2
    
    # Padding symetryczny
    padded = np.pad(gray, pad_width=half, mode='reflect')
    
    result = np.zeros_like(gray, dtype=np.uint8)
    
    for y in range(h):
        for x in range(w):
            # Wytnij lokalne okno (współrzędne w padded)
            window = padded[y:y+window_size, x:x+window_size]
            
            # Oblicz lokalny próg Otsu
            T_local = otsu_threshold(window)
            
            # Zastosuj próg do centralnego piksela
            result[y, x] = 255 if gray[y, x] >= T_local else 0
    
    return result


def main():
    folder = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(folder, '..', 'kwiatki.png')
    
    if not os.path.exists(img_path):
        print(f'Brak pliku: {img_path}')
        return 1
    
    gray = load_gray(img_path)
    print(f'Wczytano obraz: {gray.shape}')
    
    # (a) Globalne Otsu
    T_global = otsu_threshold(gray)
    binary_global = apply_threshold(gray, T_global)
    save_binary(binary_global, os.path.join(folder, 'kwiatki_otsu_global.png'))
    print(f'(a) Globalne Otsu: T = {T_global}')
    
    # (b) Trójklasowe iteracyjne Otsu
    T1, T2, three_class = otsu_three_class_iterative(gray, delta_threshold=2)
    save_binary(three_class, os.path.join(folder, 'kwiatki_otsu_3class.png'))
    print(f'(b) Trójklasowe Otsu: T1 = {T1}, T2 = {T2}')
    
    # (c) Lokalne Otsu 11×11
    print('(c) Lokalne Otsu 11×11: przetwarzanie (może zająć chwilę)...')
    binary_local = otsu_local(gray, window_size=11)
    save_binary(binary_local, os.path.join(folder, 'kwiatki_otsu_local11x11.png'))
    print('(c) Lokalne Otsu 11×11: gotowe')
    
    print('\nZakończono progowanie Otsu dla kwiatki.png')
    return 0


if __name__ == '__main__':
    sys.exit(main())
