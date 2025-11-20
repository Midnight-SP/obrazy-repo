#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zadanie 19: Steganografia LSB (Least Significant Bit)
(a) Odczytanie ukrytego obrazu z płaszczyzny bitowej
(b) Ukrycie nowego obrazu w obrazie nośnikowym
"""

import numpy as np
from PIL import Image

def extract_lsb_image(carrier_img_array, output_bits=1):
    """
    Wydobycie obrazu ukrytego w najmłodszych bitach (LSB).
    
    Args:
        carrier_img_array: Obraz nośnikowy (numpy array)
        output_bits: Liczba najmłodszych bitów do wydobycia (zazwyczaj 1)
    
    Returns:
        Wydobyty obraz (numpy array)
    """
    # Wydobądź najmłodsze bity
    if output_bits == 1:
        # Dla 1 bitu: pobierz bit LSB i rozszerz do pełnego zakresu
        lsb_plane = (carrier_img_array & 1) * 255
    else:
        # Dla wielu bitów: pobierz maską i przeskaluj
        mask = (1 << output_bits) - 1
        lsb_plane = (carrier_img_array & mask) * (255 // mask)
    
    return lsb_plane.astype(np.uint8)

def embed_lsb_image(carrier_img_array, secret_img_array, num_bits=1):
    """
    Ukrycie obrazu w najmłodszych bitach obrazu nośnikowego.
    
    Args:
        carrier_img_array: Obraz nośnikowy (numpy array)
        secret_img_array: Obraz do ukrycia (numpy array)
        num_bits: Liczba najmłodszych bitów do użycia (zazwyczaj 1)
    
    Returns:
        Obraz z ukrytą informacją (numpy array)
    """
    # Upewnij się, że obrazy mają ten sam rozmiar
    if carrier_img_array.shape != secret_img_array.shape:
        print(f"  Uwaga: Rozmiary obrazów różnią się!")
        print(f"    Carrier: {carrier_img_array.shape}")
        print(f"    Secret: {secret_img_array.shape}")
        # Dopasuj rozmiar obrazu tajnego do nośnika
        from PIL import Image as PILImage
        secret_pil = PILImage.fromarray(secret_img_array)
        secret_pil = secret_pil.resize((carrier_img_array.shape[1], carrier_img_array.shape[0]))
        secret_img_array = np.array(secret_pil)
        print(f"    Secret po resize: {secret_img_array.shape}")
    
    # Przygotuj obraz wynikowy (kopia carrier)
    stego_img = carrier_img_array.copy()
    
    # Wyczyść najmłodsze bity w obrazie nośnikowym
    mask_clear = ~((1 << num_bits) - 1)
    stego_img = stego_img & mask_clear
    
    # Przygotuj dane do ukrycia (przeskaluj do num_bits bitów)
    if num_bits == 1:
        # Dla 1 bitu: proguj obraz tajny (>127 = 1, <=127 = 0)
        secret_bits = (secret_img_array > 127).astype(np.uint8)
    else:
        # Dla wielu bitów: przeskaluj
        secret_bits = (secret_img_array >> (8 - num_bits)).astype(np.uint8)
    
    # Wstaw dane tajne do LSB
    stego_img = stego_img | secret_bits
    
    return stego_img.astype(np.uint8)

def create_sample_secret_image(width, height):
    """
    Tworzy prosty obraz testowy do ukrycia (logo/wzór).
    """
    img = np.zeros((height, width), dtype=np.uint8)
    
    # Narysuj prostą grafikę - napis "SECRET"
    # Dla uproszczenia: prostokąt z przekątną
    center_y, center_x = height // 2, width // 2
    size = min(width, height) // 3
    
    # Prostokąt
    y1, y2 = center_y - size, center_y + size
    x1, x2 = center_x - size, center_x + size
    img[y1:y2, x1:x1+20] = 255  # lewa krawędź
    img[y1:y2, x2-20:x2] = 255  # prawa krawędź
    img[y1:y1+20, x1:x2] = 255  # górna krawędź
    img[y2-20:y2, x1:x2] = 255  # dolna krawędź
    
    # Przekątne
    for i in range(size * 2):
        img[y1 + i, x1 + i] = 255
        img[y1 + i, x2 - i] = 255
    
    # Tekst "SECRET" (bardzo prosto)
    text_y = center_y
    text_x = center_x - 50
    img[text_y-10:text_y+10, text_x:text_x+100] = 255
    
    return img

def main():
    print("="*60)
    print("Zadanie 19: Steganografia LSB")
    print("="*60)
    
    # (a) Odczytanie ukrytego obrazu
    print("\n" + "="*60)
    print("(a) Odczytywanie ukrytego cytatu Einsteina")
    print("="*60)
    
    # Wczytaj obraz z ukrytą informacją
    carrier_img = Image.open('../AlbertEinstein-modified.png').convert('L')
    carrier_array = np.array(carrier_img)
    
    print(f"Wczytano obraz nośnikowy: {carrier_array.shape}")
    print(f"Zakres wartości: [{carrier_array.min()}, {carrier_array.max()}]")
    
    # Wydobądź ukryty obraz z LSB
    print("\nWydobywanie informacji z płaszczyzny LSB...")
    extracted_1bit = extract_lsb_image(carrier_array, output_bits=1)
    
    # Zapisz wydobyty obraz
    img_extracted_1bit = Image.fromarray(extracted_1bit)
    img_extracted_1bit.save('extracted_quote_1bit.png')
    print("Zapisano: extracted_quote_1bit.png")
    
    # Sprawdź również 2 bity (czasem informacja jest w 2 LSB)
    extracted_2bit = extract_lsb_image(carrier_array, output_bits=2)
    img_extracted_2bit = Image.fromarray(extracted_2bit)
    img_extracted_2bit.save('extracted_quote_2bit.png')
    print("Zapisano: extracted_quote_2bit.png (alternatywna ekstrakcja)")
    
    print("\nStatystyki wydobytego obrazu (1-bit LSB):")
    print(f"  Średnia: {extracted_1bit.mean():.2f}")
    print(f"  Unikalne wartości: {len(np.unique(extracted_1bit))}")
    print(f"  Rozkład: {np.bincount(extracted_1bit.flatten())[:10]}")
    
    # (b) Ukrycie nowego obrazu
    print("\n" + "="*60)
    print("(b) Ukrywanie nowego obrazu w obrazie nośnikowym")
    print("="*60)
    
    # Utwórz prosty obraz tajny
    print("Tworzenie przykładowego obrazu tajnego...")
    height, width = carrier_array.shape
    secret_img = create_sample_secret_image(width, height)
    
    # Zapisz obraz tajny dla dokumentacji
    img_secret = Image.fromarray(secret_img)
    img_secret.save('secret_image_to_hide.png')
    print(f"Utworzono obraz tajny: {secret_img.shape}")
    print("Zapisano: secret_image_to_hide.png")
    
    # Ukryj obraz tajny w obrazie nośnikowym
    print("\nUkrywanie obrazu tajnego w płaszczyźnie LSB...")
    stego_img = embed_lsb_image(carrier_array, secret_img, num_bits=1)
    
    # Zapisz obraz wynikowy (steganogram)
    img_stego = Image.fromarray(stego_img)
    img_stego.save('AlbertEinstein_with_secret.png')
    print("Zapisano steganogram: AlbertEinstein_with_secret.png")
    
    # Sprawdź różnicę między oryginałem a steganogramem
    diff = np.abs(carrier_array.astype(np.int16) - stego_img.astype(np.int16))
    print(f"\nRóżnica między oryginałem a steganogramem:")
    print(f"  Maksymalna różnica: {diff.max()} (powinna być ≤1 dla 1-bit LSB)")
    print(f"  Liczba zmienionych pikseli: {np.sum(diff > 0)}")
    print(f"  Procent zmienionych pikseli: {100 * np.sum(diff > 0) / diff.size:.2f}%")
    
    # Weryfikacja: wydobądź ukryty obraz ze steganogramu
    print("\nWeryfikacja: wydobywanie ukrytego obrazu ze steganogramu...")
    extracted_secret = extract_lsb_image(stego_img, output_bits=1)
    img_extracted_secret = Image.fromarray(extracted_secret)
    img_extracted_secret.save('extracted_secret_verification.png')
    print("Zapisano: extracted_secret_verification.png")
    
    # Sprawdź poprawność
    match = np.array_equal(extracted_secret, (secret_img > 127).astype(np.uint8) * 255)
    print(f"Weryfikacja poprawności: {'✓ SUKCES' if match else '✗ BŁĄD'}")
    
    print("\n" + "="*60)
    print("PODSUMOWANIE")
    print("="*60)
    print("\nTechnika LSB (Least Significant Bit):")
    print("  - Ukrywa informację w najmłodszych bitach pikseli")
    print("  - Zmiana ≤1 w wartości piksela (niewidoczna dla oka)")
    print("  - Pojemność: 1 bit na piksel = 1/8 rozmiaru obrazu")
    print("  - Wrażliwa na kompresję stratną (JPEG)")
    print("\n(a) Wydobyto ukryty cytat z AlbertEinstein-modified.png")
    print("(b) Ukryto nowy obraz i zapisano jako AlbertEinstein_with_secret.png")
    print("\n✓ Steganografia zakończona pomyślnie!")

if __name__ == '__main__':
    main()
