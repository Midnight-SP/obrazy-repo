from ij import IJ, ImagePlus
from ij.process import ByteProcessor

# Algorytm Ordered Dithering z macierzą Bayera 4x4
# Kwantyzacja do 5 poziomów szarości: 0, 64, 128, 192, 255

# Ścieżki do plików
input_path = "/home/mryduchowski1/obrazy repo/zestaw1/zad15/lwy.png"
output_path = "/home/mryduchowski1/obrazy repo/zestaw1/zad15/lwy_dithered_5levels.png"

# Macierz Bayera 4x4
bayer = [
    [0,  8,  2, 10],
    [12, 4, 14, 6],
    [3, 11, 1, 9],
    [15, 7, 13, 5]
]

# 5 poziomów szarości
gray_levels = [0, 64, 128, 192, 255]
n_levels = len(gray_levels)

print("=== ORDERED DITHERING - 5 poziomów szarości ===\n")
print("Macierz Bayera 4x4:")
for row in bayer:
    print(row)
print("\nPoziomy szarości: " + str(gray_levels))
print("Liczba poziomów: " + str(n_levels))

# Wczytaj obraz
imp = IJ.openImage(input_path)
if imp is None:
    print("Cannot open image: " + input_path)
else:
    # Konwersja do skali szarości
    IJ.run(imp, "8-bit", "")
    ip = imp.getProcessor()
    width = ip.getWidth()
    height = ip.getHeight()
    
    print("\nRozmiar obrazu: " + str(width) + "x" + str(height))
    
    # Przygotuj obraz wyjściowy
    result_ip = ByteProcessor(width, height)
    
    print("\n=== ALGORYTM ===")
    print("1. Normalizuj wartość piksela: norm = pixel / 255.0")
    print("2. Pobierz próg z macierzy Bayera: t = (bayer[y%4][x%4] + 0.5) / 16.0")
    print("3. Zastosuj próg zmienny: val = floor((norm + t / (n_levels-1)) * (n_levels-1))")
    print("4. Przypisz poziom szarości: output = gray_levels[val]")
    print("\nPrzetwarzanie...")
    
    # Przetwarzaj każdy piksel
    for y in range(height):
        for x in range(width):
            # Pobierz wartość piksela i znormalizuj do 0-1
            pixel_val = float(ip.getPixel(x, y))
            norm = pixel_val / 255.0
            
            # Pobierz próg z macierzy Bayera (tile repeating)
            bayer_val = float(bayer[y % 4][x % 4])
            t = (bayer_val + 0.5) / 16.0
            
            # Zastosuj próg zmienny i skaluj
            val = (norm + t / float(n_levels - 1)) * float(n_levels - 1)
            val = int(val)  # floor
            
            # Ogranicz do zakresu 0 - (n_levels-1)
            if val < 0:
                val = 0
            if val >= n_levels:
                val = n_levels - 1
            
            # Przypisz odpowiedni poziom szarości
            output_val = gray_levels[val]
            result_ip.putPixel(x, y, output_val)
    
    # Zapisz wynik
    result_imp = ImagePlus("Dithered_5levels", result_ip)
    IJ.saveAs(result_imp, "PNG", output_path)
    print("\nZapisano obraz do: " + output_path)
    
    # Statystyki
    print("\n=== STATYSTYKI ===")
    level_counts = [0] * n_levels
    for y in range(height):
        for x in range(width):
            val = result_ip.getPixel(x, y)
            for i, level in enumerate(gray_levels):
                if val == level:
                    level_counts[i] += 1
                    break
    
    total_pixels = width * height
    print("Liczba pikseli na poziom:")
    for i, level in enumerate(gray_levels):
        count = level_counts[i]
        percent = (count * 100.0) / total_pixels
        print("  Poziom " + str(level) + ": " + str(count) + " (" + str(round(percent, 1)) + "%)")
    
    print("\nGotowe!")
