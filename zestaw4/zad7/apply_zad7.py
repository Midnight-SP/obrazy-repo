#!/usr/bin/env python3
"""Zadanie 7: 2D signal convolution (Splot sygnałów 2D)

Part (a): Compute f * h1 and f * h2 and analyze edge detection.
Part (b): Interpret differences between 8-bit and 32-bit convolution in ImageJ.

f (7×7 matrix with a 3×3 block of zeros in center):
    255 255 255 255 255 255 255
    255 255 255 255 255 255 255
    255 255   0   0   0 255 255
    255 255   0   0   0 255 255
    255 255   0   0   0 255 255
    255 255 255 255 255 255 255
    255 255 255 255 255 255 255

h1 = [1, -1, 0]^T (vertical gradient: top derivative)
h2 = [0, 1, -1]^T (vertical gradient: bottom derivative)
"""
import numpy as np
import os
from PIL import Image


def convolve_1d_vertical(f, h):
    """Apply 1D vertical convolution (h applied to rows).
    
    f: 2D array (H×W)
    h: 1D array (column vector, applied vertically to each row)
    
    Returns: 2D array (H×W) with same size as f (symmetric padding).
    """
    H, W = f.shape
    h_len = len(h)
    result = np.zeros_like(f, dtype=np.float32)
    
    # Apply h vertically: for each column, convolve the column with h
    for j in range(W):
        col = f[:, j].astype(np.float32)
        # Pad column with symmetric boundary (reflect mode)
        pad_size = h_len // 2
        if pad_size > 0:
            padded_col = np.pad(col, pad_size, mode='symmetric')
        else:
            padded_col = col
        
        # Convolve
        conv_col = np.convolve(padded_col, h, mode='valid')
        result[:, j] = conv_col[:H]  # Ensure we take only H elements
    
    return result


def format_matrix_for_display(arr, name="Matrix"):
    """Print a matrix in a nice format with row/col labels."""
    print(f"\n{name}:")
    H, W = arr.shape
    # Print header (column indices)
    print("     ", end="")
    for j in range(W):
        print(f"{j:6d}", end="")
    print()
    
    # Print rows
    for i in range(H):
        print(f"Row {i}: ", end="")
        for j in range(W):
            val = arr[i, j]
            # Format: right-aligned integer if whole number, else float
            if isinstance(val, (int, np.integer)) or val == int(val):
                print(f"{int(val):6d}", end="")
            else:
                print(f"{val:6.1f}", end="")
        print()


def format_kernel(h, name="h"):
    """Print a 1D kernel."""
    print(f"\n{name} = {h}")


def save_matrix_as_image(arr, filename, scale=50):
    """Save a matrix as a PNG image with upscaling for visibility.
    
    arr: 2D array (values can be negative)
    filename: output filename
    scale: pixel size for each matrix cell
    """
    H, W = arr.shape
    
    # Map values to [0, 255] range for visualization
    # For values with negatives, center at 128 (mid-gray)
    if arr.min() < 0 or arr.max() > 255:
        # Symmetric range around zero
        maxabs = max(abs(arr.min()), abs(arr.max()), 1.0)
        # Map [-maxabs, maxabs] to [0, 255]
        normalized = ((arr / maxabs) * 0.5 + 0.5) * 255.0
    else:
        # Direct mapping
        normalized = arr.copy()
    
    normalized = np.clip(normalized, 0, 255).astype(np.uint8)
    
    # Create upscaled image
    img_scaled = np.repeat(np.repeat(normalized, scale, axis=0), scale, axis=1)
    Image.fromarray(img_scaled).save(filename)
    print(f"Saved image: {filename}")


def main():
    # Define signal f (7×7 with 3×3 black square in center)
    f = np.full((7, 7), 255, dtype=np.float32)
    f[2:5, 2:5] = 0
    
    # Define kernels
    h1 = np.array([1, -1, 0], dtype=np.float32)  # Top derivative
    h2 = np.array([0, 1, -1], dtype=np.float32)  # Bottom derivative
    
    print("=" * 70)
    print("ZADANIE 7: Splot sygnałów 2D")
    print("=" * 70)
    
    print("\n### CZĘŚĆ (a): Sploty w dziedzinie liczb rzeczywistych ###\n")
    
    format_matrix_for_display(f, "Sygnał f (7×7)")
    format_kernel(h1, "Kernel h1 (vertical top derivative)")
    format_kernel(h2, "Kernel h2 (vertical bottom derivative)")
    
    # Compute convolutions
    result_h1 = convolve_1d_vertical(f, h1)
    result_h2 = convolve_1d_vertical(f, h2)
    
    format_matrix_for_display(result_h1, "f * h1 (top edge detection)")
    format_matrix_for_display(result_h2, "f * h2 (bottom edge detection)")
    
    print("\n### ANALIZA WYNIKU (część a) ###\n")
    print(f"h1 = {h1}")
    print("  → detektuje przejście z jasnego (255) na ciemne (0) jako +255 (jasne)")
    print("  → detektuje przejście z ciemnego (0) na jasne (255) jako -255 (ciemne)")
    print("  → odpowiada górnej krawędzi czarnego kwadratu (wiersz 1→2)")
    
    print(f"\nh2 = {h2}")
    print("  → detektuje przejście z jasnego (255) na ciemne (0) jako -255 (ciemne)")
    print("  → detektuje przejście z ciemnego (0) na jasne (255) jako +255 (jasne)")
    print("  → odpowiada dolnej krawędzi czarnego kwadratu (wiersz 4→5)")
    
    print("\nCzy oba sploty wykrywają te same krawędzie?")
    print("  NIE — h1 i h2 to różne operatory (przesunięte względem siebie).")
    print("  h1 detektuje górną krawędź (zmiana 255→0 w wierszu 1→2)")
    print("  h2 detektuje dolną krawędź (zmiana 0→255 w wierszu 4→5)")
    print("  Znaki są przeciwne (h1 daje +255 na górze, h2 daje +255 na dole)")
    
    print("\n" + "=" * 70)
    print("### CZĘŚĆ (b): Różnice między 8-bitami a 32-bitami w ImageJ ###\n")
    
    print("OBSERWACJA OCZEKIWANA:")
    print("  W systemach 8-bit operacje na pixelach są ograniczone do zakresu [0, 255].")
    print("  Wyniki splotu mogą wychodzić poza ten zakres:")
    print(f"    - f * h1 produkuje wartości: min={result_h1.min():.0f}, max={result_h1.max():.0f}")
    print(f"    - f * h2 produkuje wartości: min={result_h2.min():.0f}, max={result_h2.max():.0f}")
    
    print("\n  W ImageJ na 8 bitach:")
    print("    - Wartości > 255 są cięte (clipped) do 255")
    print("    - Wartości < 0 są cięte do 0")
    print("    - To prowadzi do utraty informacji (detale zmienią się w całkowite czarno/biel)")
    
    print("\n  W ImageJ na 32 bitach (float):")
    print("    - Nie ma clippingu — wyniki są zachowywane bez zmian")
    print("    - Możliwe są wartości ujemne i wartości > 255")
    print("    - Umożliwia późniejszą normalizację (np. do [0, 255] lub [-1, 1])")
    
    print("\n  RÓŻNICE WZGLĘDEM CZĘŚCI (a):")
    print("    - Część (a) wykonana na liczbach rzeczywistych (float) — dokładne wyniki")
    print("    - ImageJ 8-bit: sploty będą clippingiem → krańcowe białe/czarne piksele")
    print("    - ImageJ 32-bit: sploty będą bliskie wynikom z części (a)")
    
    print("\n" + "=" * 70)
    
    # Save results to file
    base_dir = os.path.dirname(__file__)
    output_file = os.path.join(base_dir, 'zadanie7_results.txt')
    
    # Save images (scaled up for visibility)
    save_matrix_as_image(f, os.path.join(base_dir, 'signal_f.png'), scale=50)
    save_matrix_as_image(result_h1, os.path.join(base_dir, 'f_conv_h1.png'), scale=50)
    save_matrix_as_image(result_h2, os.path.join(base_dir, 'f_conv_h2.png'), scale=50)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("ZADANIE 7: Splot sygnałów 2D\n")
        f.write("=" * 70 + "\n\n")
        f.write("CZĘŚĆ (a): Sploty\n\n")
        f.write("Sygnał f:\n")
        f.write(repr(f) + "\n\n")
        f.write("f * h1:\n")
        f.write(str(result_h1) + "\n\n")
        f.write("f * h2:\n")
        f.write(str(result_h2) + "\n\n")
        f.write("CZĘŚĆ (b): Analiza 8-bit vs 32-bit\n")
        f.write("Zbiory wartości:\n")
        f.write(f"  f * h1: min={result_h1.min():.0f}, max={result_h1.max():.0f}\n")
        f.write(f"  f * h2: min={result_h2.min():.0f}, max={result_h2.max():.0f}\n")
    
    print(f"\nWyniki zapisane do: {output_file}")


if __name__ == '__main__':
    main()
