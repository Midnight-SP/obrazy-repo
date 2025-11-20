#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zadanie 9: Zwiększenie kontrastu poprzez zastosowanie kolorów (pseudokolorowanie)
Zastosowanie trzech funkcji mapowania wartości szarości (R, G, B) do obrazu wyrównanego z zadania 7.
"""

import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

def create_blue_mapping():
    """
    Niebieski kanał:
    - [0, 64]: liniowo od 0 do 64
    - [64, 128]: liniowo od 64 do 0
    - [128, 255]: liniowo od 0 do 255
    """
    mapping = np.zeros(256, dtype=np.uint8)
    
    # [0, 64]: y = x
    for x in range(0, 65):
        mapping[x] = x
    
    # [64, 128]: od 64 do 0 (liniowo)
    for i, x in enumerate(range(64, 129)):
        mapping[x] = int(64 - (64 * i / 64))
    
    # [128, 255]: od 0 do 255 (liniowo)
    for i, x in enumerate(range(128, 256)):
        mapping[x] = int(255 * i / 127)
    
    return mapping

def create_red_mapping():
    """
    Czerwony kanał:
    - [0, 64]: stała wartość 0
    - [64, 128]: liniowo od 0 do 128
    - [128, 192]: liniowo od 128 do 0
    - [192, 255]: liniowo od 0 do 255
    """
    mapping = np.zeros(256, dtype=np.uint8)
    
    # [0, 64]: y = 0
    for x in range(0, 64):
        mapping[x] = 0
    
    # [64, 128]: od 0 do 128 (liniowo)
    for i, x in enumerate(range(64, 129)):
        mapping[x] = int(128 * i / 64)
    
    # [128, 192]: od 128 do 0 (liniowo)
    for i, x in enumerate(range(128, 193)):
        mapping[x] = int(128 - (128 * i / 64))
    
    # [192, 255]: od 0 do 255 (liniowo)
    for i, x in enumerate(range(192, 256)):
        mapping[x] = int(255 * i / 63)
    
    return mapping

def create_green_mapping():
    """
    Zielony kanał:
    - [0, 64]: stała wartość 0
    - [64, 192]: liniowo od 0 do 255
    - [192, 255]: stała wartość 255
    """
    mapping = np.zeros(256, dtype=np.uint8)
    
    # [0, 64]: y = 0
    for x in range(0, 64):
        mapping[x] = 0
    
    # [64, 192]: od 0 do 255 (liniowo)
    for i, x in enumerate(range(64, 193)):
        mapping[x] = int(255 * i / 128)
    
    # [192, 255]: y = 255
    for x in range(192, 256):
        mapping[x] = 255
    
    return mapping

def apply_pseudocoloring(img_gray, r_map, g_map, b_map):
    """
    Zastosuj pseudokolorowanie do obrazu w skali szarości.
    Każda wartość szarości jest mapowana niezależnie na R, G, B.
    """
    img_array = np.array(img_gray)
    
    # Utwórz trzy kanały RGB przez mapowanie wartości szarości
    r_channel = r_map[img_array]
    g_channel = g_map[img_array]
    b_channel = b_map[img_array]
    
    # Złóż kanały w obraz RGB
    img_rgb = np.stack([r_channel, g_channel, b_channel], axis=-1)
    
    return img_rgb

def plot_mapping_functions(r_map, g_map, b_map, filename):
    """Wizualizuj funkcje mapowania RGB."""
    plt.figure(figsize=(10, 6))
    
    x = np.arange(256)
    plt.plot(x, r_map, color='red', linewidth=2, label='Czerwony (R)')
    plt.plot(x, g_map, color='green', linewidth=2, label='Zielony (G)')
    plt.plot(x, b_map, color='blue', linewidth=2, label='Niebieski (B)')
    
    plt.title('Funkcje mapowania wartości szarości na kanały RGB')
    plt.xlabel('Wartość wejściowa (szarość)')
    plt.ylabel('Wartość wyjściowa (kanał koloru)')
    plt.xlim([0, 255])
    plt.ylim([0, 255])
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close()
    print(f"Zapisano wykres funkcji mapowania: {filename}")

def main():
    # Wczytaj wyrównany obraz z zadania 7
    img_path = '../zad7/RezydencjaDiabla_equalized.png'
    img_gray = Image.open(img_path).convert('L')
    img_array = np.array(img_gray)
    
    print(f"Wczytano obraz wyrównany: {img_array.shape}")
    print(f"Zakres wartości: [{img_array.min()}, {img_array.max()}]")
    
    # Utwórz funkcje mapowania dla trzech kanałów
    print("\nTworzenie funkcji mapowania RGB...")
    r_mapping = create_red_mapping()
    g_mapping = create_green_mapping()
    b_mapping = create_blue_mapping()
    
    # Wizualizuj funkcje mapowania
    plot_mapping_functions(r_mapping, g_mapping, b_mapping, 'mapping_functions.png')
    
    # Zastosuj pseudokolorowanie
    print("Stosowanie pseudokolorowania...")
    img_colored = apply_pseudocoloring(img_gray, r_mapping, g_mapping, b_mapping)
    
    # Zapisz wynik
    img_colored_pil = Image.fromarray(img_colored.astype(np.uint8))
    img_colored_pil.save('RezydencjaDiabla_pseudocolored.png')
    print("Zapisano obraz pseudokolorowany: RezydencjaDiabla_pseudocolored.png")
    
    # Przykładowe wartości mapowania dla kilku punktów
    print("\nPrzykładowe wartości mapowania:")
    test_values = [0, 64, 128, 192, 255]
    for val in test_values:
        r, g, b = r_mapping[val], g_mapping[val], b_mapping[val]
        print(f"  Szarość {val:3d} → RGB({r:3d}, {g:3d}, {b:3d})")
    
    print("\n✓ Pseudokolorowanie zakończone pomyślnie!")

if __name__ == '__main__':
    main()
