# Algorytm Ordered Dithering z macierzą Bayera 4x4
# Zadanie: Obliczenie obrazu wyjściowego dla palety 1-bitowej

# Fragment obrazu wejściowego (wartości szarości)
# Pozycje: m = 250-253, n = 250-253
input_image = [
    [176, 181, 194, 182],  # n=250
    [175, 176, 163, 160],  # n=251
    [172, 194, 189, 185],  # n=252
    [207, 179, 181, 205]   # n=253
]

# Macierz Bayera 4x4
# Zawiera wartości 0-15 określające kolejność progów
# Standardowa macierz Bayera D4
D = [
    [ 0,  8,  2, 10],
    [12,  4, 14,  6],
    [ 3, 11,  1,  9],
    [15,  7, 13,  5]
]

N = 4  # Rozmiar macierzy
M = N * N  # Liczba poziomów = 16

print("=== ORDERED DITHERING z MACIERZĄ BAYERA 4x4 ===\n")
print("Obraz wejściowy (wartości szarości):")
print("     m=250  m=251  m=252  m=253")
for n, row in enumerate(input_image, start=250):
    print(f"n={n}:  {row[0]:3d}    {row[1]:3d}    {row[2]:3d}    {row[3]:3d}")

print("\nMacierz Bayera D4 (4x4):")
print("    x=0  x=1  x=2  x=3")
for y, row in enumerate(D):
    print(f"y={y}:  {row[0]:2d}   {row[1]:2d}   {row[2]:2d}   {row[3]:2d}")

print("\n=== ALGORYTM ===")
print("1. Dla każdego piksela (m, n):")
print("2. Oblicz pozycję w macierzy: x_mod = m % 4, y_mod = n % 4")
print("3. Pobierz wartość z macierzy: d = D[y_mod][x_mod]")
print("4. Oblicz próg: threshold = ((d + 0.5) / 16) * 255")
print("5. Jeśli piksel > threshold -> biały (255), w przeciwnym razie -> czarny (0)")

print("\n=== Obliczenia dla każdego piksela ===\n")

output_image = []
for n in range(4):  # n = 250, 251, 252, 253
    output_row = []
    for m in range(4):  # m = 250, 251, 252, 253
        # Pozycje w macierzy ditheringu (modulo 3)
        actual_n = n + 250
        actual_m = m + 250
        y_mod = actual_n % N
        x_mod = actual_m % N
        
        # Wartość z macierzy ditheringu
        d_val = D[y_mod][x_mod]
        
        # Obliczenie progu
        threshold = ((float(d_val) + 0.5) / float(M)) * 255.0
        
        # Wartość piksela wejściowego
        pixel_val = input_image[n][m]
        
        # Decyzja: biały (255) lub czarny (0)
        output_val = 255 if pixel_val > threshold else 0
        output_char = '■' if output_val == 255 else '□'
        
        output_row.append(output_val)
        
        print(f"({actual_m},{actual_n}): g={pixel_val:3d}, D[{y_mod}][{x_mod}]={d_val}, " +
              f"T={threshold:6.2f}, {pixel_val}>{threshold:.0f}? -> {output_val:3d} {output_char}")
    
    output_image.append(output_row)

print("\n=== OBRAZ WYJŚCIOWY ===")
print("\nWartości (0 = czarny, 255 = biały):")
print("     m=250  m=251  m=252  m=253")
for n, row in enumerate(output_image, start=250):
    print(f"n={n}:  {row[0]:3d}    {row[1]:3d}    {row[2]:3d}    {row[3]:3d}")

print("\nWizualizacja (■ = biały, □ = czarny):")
print("     m=250  m=251  m=252  m=253")
for n, row in enumerate(output_image, start=250):
    chars = ['■' if val == 255 else '□' for val in row]
    print(f"n={n}:   {chars[0]}      {chars[1]}      {chars[2]}      {chars[3]}")

print("\nWzór bitowy (1 = biały, 0 = czarny):")
print("     m=250  m=251  m=252  m=253")
for n, row in enumerate(output_image, start=250):
    bits = [1 if val == 255 else 0 for val in row]
    print(f"n={n}:   {bits[0]}      {bits[1]}      {bits[2]}      {bits[3]}")

print("\n=== STATYSTYKI ===")
white_pixels = sum(row.count(255) for row in output_image)
black_pixels = sum(row.count(0) for row in output_image)
avg_input = sum(sum(row) for row in input_image) / 16

print(f"Białych pikseli: {white_pixels}/16 ({white_pixels*100/16:.1f}%)")
print(f"Czarnych pikseli: {black_pixels}/16 ({black_pixels*100/16:.1f}%)")
print(f"Średnia jasność wejścia: {avg_input:.1f}/255 ({avg_input*100/255:.1f}%)")
print(f"Różnica: {abs(white_pixels*100/16 - avg_input*100/255):.1f}%")
