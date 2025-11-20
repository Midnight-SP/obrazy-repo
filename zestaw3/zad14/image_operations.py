#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zadanie 14: Operacje logiczne i arytmetyczne na obrazach
(a) Operacje arytmetyczne - podkreślenie czerwonych krawędzi na obrazie w skali szarości
(b) Operacje logiczne - podkreślenie cyjanowych krawędzi na obrazie RGB
"""

import numpy as np
from PIL import Image

def arithmetic_red_overlay(img_gray, edges):
    """
    (a) Operacje arytmetyczne do podkreślenia krawędzi w kolorze czerwonym.
    
    Strategia:
    1. Konwersja obrazu szarości na RGB (wszystkie kanały identyczne)
    2. Tam gdzie są krawędzie (białe piksele = 255), ustaw R=255, G=0, B=0
    3. Użyj operacji arytmetycznych do połączenia
    
    Operacje:
    - R_out = R_gray + edges  (dodanie krawędzi do kanału czerwonego)
    - G_out = G_gray - edges  (odjęcie krawędzi od kanału zielonego)
    - B_out = B_gray - edges  (odjęcie krawędzi od kanału niebieskiego)
    
    Gdzie edges to znormalizowana maska (0 lub 1).
    """
    # Konwertuj obraz szarości na RGB
    img_rgb = np.stack([img_gray, img_gray, img_gray], axis=-1).astype(np.float32)
    
    # Normalizuj krawędzie do [0, 1]
    edges_norm = edges.astype(np.float32) / 255.0
    
    # Operacje arytmetyczne
    # R: dodaj krawędzie (białe krawędzie stają się czerwone)
    r_channel = np.clip(img_rgb[:, :, 0] + edges_norm * 255, 0, 255)
    
    # G i B: odejmij krawędzie (zmniejsz zielony i niebieski tam gdzie są krawędzie)
    g_channel = np.clip(img_rgb[:, :, 1] - edges_norm * 255, 0, 255)
    b_channel = np.clip(img_rgb[:, :, 2] - edges_norm * 255, 0, 255)
    
    # Złóż z powrotem
    result = np.stack([r_channel, g_channel, b_channel], axis=-1).astype(np.uint8)
    
    return result

def logical_cyan_overlay(img_rgb, edges):
    """
    (b) Operacje logiczne do podkreślenia krawędzi w kolorze cyjan (R=0, G=255, B=255).
    
    Strategia:
    1. Cyjan = NOT czerwony = Green AND Blue
    2. Tam gdzie są krawędzie, ustaw R=0, G=255, B=255
    
    Operacje logiczne:
    - R_out = R_orig AND (NOT edges)  (wyzeruj R tam gdzie są krawędzie)
    - G_out = G_orig OR edges         (ustaw G=255 tam gdzie są krawędzie)
    - B_out = B_orig OR edges         (ustaw B=255 tam gdzie są krawędzie)
    
    Gdzie edges to binarna maska (0 lub 255).
    """
    # Konwersja do uint8 jeśli potrzeba
    img_rgb = img_rgb.astype(np.uint8)
    edges = edges.astype(np.uint8)
    
    # Operacje logiczne (bitowe)
    # R: AND z NOT edges (wyzeruj tam gdzie są krawędzie)
    r_channel = np.bitwise_and(img_rgb[:, :, 0], np.bitwise_not(edges))
    
    # G i B: OR z edges (ustaw na 255 tam gdzie są krawędzie)
    g_channel = np.bitwise_or(img_rgb[:, :, 1], edges)
    b_channel = np.bitwise_or(img_rgb[:, :, 2], edges)
    
    # Złóż z powrotem
    result = np.stack([r_channel, g_channel, b_channel], axis=-1).astype(np.uint8)
    
    return result

def main():
    print("="*60)
    print("Zadanie 14: Operacje arytmetyczne i logiczne")
    print("="*60)
    
    # (a) Operacje arytmetyczne - bakterie.png (grayscale) + czerwone krawędzie
    print("\n(a) Operacje arytmetyczne - czerwone krawędzie")
    print("-"*60)
    
    # Wczytaj obrazy
    img_bakterie = Image.open('../bakterie.png').convert('L')
    img_edges = Image.open('../bakterie_krawedzie.png').convert('L')
    
    bakterie_array = np.array(img_bakterie)
    edges_array = np.array(img_edges)
    
    print(f"Wczytano bakterie.png: {bakterie_array.shape}")
    print(f"Wczytano bakterie_krawedzie.png: {edges_array.shape}")
    
    # Zastosuj operacje arytmetyczne
    result_arithmetic = arithmetic_red_overlay(bakterie_array, edges_array)
    
    # Zapisz wynik
    img_result_a = Image.fromarray(result_arithmetic)
    img_result_a.save('bakterie_red_edges.png')
    print("Zapisano: bakterie_red_edges.png")
    
    print("\nOperacje arytmetyczne:")
    print("  R_out = R_gray + edges")
    print("  G_out = G_gray - edges")
    print("  B_out = B_gray - edges")
    print("gdzie edges ∈ [0, 1] (znormalizowane)")
    
    # (b) Operacje logiczne - bakterieRGB.png + cyjanowe krawędzie
    print("\n" + "="*60)
    print("(b) Operacje logiczne - cyjanowe krawędzie")
    print("-"*60)
    
    # Wczytaj obraz RGB
    img_bakterie_rgb = Image.open('../bakterieRGB.png').convert('RGB')
    bakterie_rgb_array = np.array(img_bakterie_rgb)
    
    print(f"Wczytano bakterieRGB.png: {bakterie_rgb_array.shape}")
    
    # Zastosuj operacje logiczne
    result_logical = logical_cyan_overlay(bakterie_rgb_array, edges_array)
    
    # Zapisz wynik
    img_result_b = Image.fromarray(result_logical)
    img_result_b.save('bakterieRGB_cyan_edges.png')
    print("Zapisano: bakterieRGB_cyan_edges.png")
    
    print("\nOperacje logiczne (bitowe):")
    print("  R_out = R_orig AND (NOT edges)")
    print("  G_out = G_orig OR edges")
    print("  B_out = B_orig OR edges")
    print("Cyjan = (R=0, G=255, B=255)")
    
    print("\n" + "="*60)
    print("✓ Oba zadania wykonane pomyślnie!")
    print("="*60)

if __name__ == '__main__':
    main()
