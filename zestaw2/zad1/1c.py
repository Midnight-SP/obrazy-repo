#!/usr/bin/env jython
"""
Zadanie 1c (Jython/ImageJ): Próbkowanie obrazu z częstotliwością f_min i rekonstrukcja bez interpolacji.
- Domyślnie f_min = 1/20 px (krok step=20)
- Wejście: zestaw2/zad1/PlytkaFresnela.png
- Wyjścia: zestaw2/zad1/PlytkaFresnela-fmin.png (rekonstrukcja)
           zestaw2/zad1/PlytkaFresnela-fmin-side-by-side.png (porównanie)
"""
from ij import IJ, ImagePlus
from ij.process import ByteProcessor
from ij.process import Blitter

# Ustawienia (dopasuj ścieżki jeśli uruchamiasz poza repo)
input_path = "/home/mryduchowski1/obrazy repo/zestaw2/zad1/PlytkaFresnela.png"
output_path = "/home/mryduchowski1/obrazy repo/zestaw2/zad1/PlytkaFresnela-fmin.png"
side_by_side_path = "/home/mryduchowski1/obrazy repo/zestaw2/zad1/PlytkaFresnela-fmin-side-by-side.png"

# f_min = 1/step
f_min = 1.0/20.0
step = int(round(1.0 / f_min))  # 20
if step < 1:
    step = 1

# Wczytaj obraz i przygotuj do 8-bit
imp = IJ.openImage(input_path)
if imp is None:
    print("Cannot open image: " + input_path)
else:
    IJ.run(imp, "8-bit", "")
    ip = imp.getProcessor()
    w = ip.getWidth()
    h = ip.getHeight()

    # Rozmiar siatki próbkowania (ceiling dla brzegów)
    sample_w = (w + step - 1) // step
    sample_h = (h + step - 1) // step

    # 1) PRÓBKOWANIE: pobierz co 'step'-ty piksel do siatki sample
    sample = [[0 for _ in range(sample_w)] for __ in range(sample_h)]
    for ys in range(sample_h):
        y_src = ys * step
        if y_src >= h:
            y_src = h - 1
        for xs in range(sample_w):
            x_src = xs * step
            if x_src >= w:
                x_src = w - 1
            sample[ys][xs] = ip.getPixel(x_src, y_src)

    # 2) REKONSTRUKCJA: replikacja pikseli siatki do rozmiaru oryginału
    out_ip = ByteProcessor(w, h)
    for y in range(h):
        ys = y // step
        if ys >= sample_h:
            ys = sample_h - 1
        for x in range(w):
            xs = x // step
            if xs >= sample_w:
                xs = sample_w - 1
            out_ip.putPixel(x, y, sample[ys][xs])

    # Zapis wyniku
    out_imp = ImagePlus("PlytkaFresnela-fmin", out_ip)
    IJ.saveAs(out_imp, "PNG", output_path)

    # 3) PORÓWNANIE obok siebie (z prostymi etykietami)
    pad = 40
    coll_ip = ByteProcessor(w * 2, h + pad)
    coll_ip.setValue(255)  # tło białe
    coll_ip.fill()
    # wklej oryginał (poniżej marginesu)
    coll_ip.copyBits(ip, 0, pad, Blitter.COPY)
    # wklej rekonstrukcję po prawej stronie
    coll_ip.copyBits(out_ip, w, pad, Blitter.COPY)
    # podpisy
    coll_ip.setValue(0)
    try:
        coll_ip.drawString("oryginał", 10, 20)
        coll_ip.drawString("rekonstrukcja (step=%d)" % step, w + 10, 20)
    except:
        pass
    coll_imp = ImagePlus("PlytkaFresnela f_min - porównanie", coll_ip)
    IJ.saveAs(coll_imp, "PNG", side_by_side_path)

    # Podsumowanie w konsoli
    print("Wejście: %s (%dx%d)" % (input_path, w, h))
    print("f_min=%.5f -> step=%d px" % (f_min, step))
    print("Siatka próbkowania: %d x %d (bez interpolacji)" % (sample_w, sample_h))
    print("Zapisano: %s" % output_path)
    print("Zapisano: %s" % side_by_side_path)
