# Przetwarzanie obrazów cyfrowych - Zestaw 3

## Zadanie 4
### Treść
Binaryzacja histogramu ⋆ (0.5 + 1.0 + 1.0)

Dla obrazu `kwiatki.png` proszę wyznaczyć obrazy wyjściowe w przypadku:

![kwiatki.png](kwiatki.png)

(a) progowania obrazu wartością progową T obliczoną metodą Otsu (progowanie globalne),

(b) iteracyjnego trójklasowego progowania obrazu w oparciu o metodę
Otsu z warunkiem Δ < 2,

(c) progowania wartościami lokalnymi progów obliczonych metodą Otsu
w sąsiedztwie 11×11 dla każdego piksela. Jeżeli sąsiedztwo wykracza
poza obszar obrazu należy przyjąć w obliczeniach symetryczne odbicie obrazu.

### Rozwiązania

Skrypt: `zad4/otsu.py` (Python, NumPy/PIL). Obraz wejściowy: `kwiatki.png` (1024×1024 px).

#### (a) Progowanie globalne metodą Otsu

Wyznaczono optymalny próg globalny metodą Otsu (maksymalizacja wariancji międzyklasowej):

**T = 166**

![Wynik progowania globalnego Otsu](zad4/kwiatki_otsu_global.png)

#### (b) Trójklasowe iteracyjne progowanie Otsu

Iteracyjny algorytm dzieli obraz na 3 klasy (ciemna, średnia, jasna) i aktualizuje progi T1 i T2 do zbieżności (Δ < 2):

**T1 = 104, T2 = 200**

Obraz wyjściowy z trzema poziomami intensywności: 0 (ciemna), 128 (średnia), 255 (jasna).

![Wynik trójklasowego Otsu](zad4/kwiatki_otsu_3class.png)

#### (c) Progowanie lokalne Otsu w oknie 11×11

Dla każdego piksela obliczono lokalny próg Otsu w sąsiedztwie 11×11 (z symetrycznym odbiciem na brzegach). Każdy piksel progowany osobno na podstawie lokalnego histogramu.

![Wynik lokalnego progowania Otsu 11×11](zad4/kwiatki_otsu_local11x11.png)

**Interpretacja:**
- **Globalne Otsu**: jednolity próg dla całego obrazu → dobre dla obrazów o równomiernym oświetleniu.
- **Trójklasowe Otsu**: wyodrębnia 3 regiony (tło, kwiaty, jasne akcenty) → lepsze rozróżnienie struktur o różnej intensywności.
- **Lokalne Otsu**: adaptacyjne progowanie uwzględniające lokalne zmiany oświetlenia → lepiej radzi sobie z nierównomiernym oświetleniem, szczegóły zachowane w ciemnych/jasnych obszarach.

## Zadanie 7
### Treść
Wyrównanie histogramu ⋆ (0.5 + 1.0 + 1.0)

Poniższy obraz to kadr z filmu „Le Manoir du Diable" („Rezydencja diabła")
– pierwszego, trwającego 3 minuty horroru w dziejach kinematografii (1896 r.).

![RezydencjaDiabla.png](RezydencjaDiabla.png)

Dla obrazu `RezydencjaDiabla.png` proszę:

(a) wyznaczyć skumulowany histogram,

(b) wykonać wyrównanie histogramu i podać wartość szarości w obrazie
wyjściowym H_equal(g) dla g = 40, g = 45 i g = 50,

(c) wykonać hiperbolizację histogramu z parametrem α = -1/3 i podać
wartość szarości w obrazie wyjściowym H_hyper(g) dla g = 40, g = 45
i g = 50.

Do rozwiązań b) i c) proszę załączyć obrazy wyjściowe i ich histogramy.

### Rozwiązania

Skrypt: `zad7/histogram_enhancement.py` (Python, NumPy/PIL/Matplotlib). Obraz wejściowy: `RezydencjaDiabla.png` (683×1024 px, zakres: [14, 228]).

#### (a) Skumulowany histogram

Wyznaczono histogram oryginalny i jego skumulowaną postać (CDF - Cumulative Distribution Function):

![Histogram oryginalny](zad7/histogram_original.png)

![Skumulowany histogram](zad7/histogram_cumulative.png)

Oryginalny obraz ma ograniczony zakres wartości szarości, co powoduje niski kontrast.

#### (b) Wyrównanie histogramu

Zastosowano transformację wyrównującą histogram: **H_equal(g) = round(255 × CDF(g) / N)**

Wartości wyjściowe dla wskazanych poziomów szarości:
- **H_equal(40) = 24**
- **H_equal(45) = 36**
- **H_equal(50) = 48**

![Obraz po wyrównaniu histogramu](zad7/RezydencjaDiabla_equalized.png)

![Histogram wyrównanego obrazu](zad7/histogram_equalized.png)

**Interpretacja:** Wyrównanie histogramu rozciąga zakres wartości na pełny przedział [0, 255], poprawiając kontrast. Histogram staje się bardziej równomierny, szczegóły w ciemnych i jasnych obszarach są lepiej widoczne.

#### (c) Hiperbolizacja histogramu (α = -1/3)

Zastosowano transformację hiperbolizującą: **H_hyper(g) = round(255 × [CDF(g)/N]^(1/(1+α)))**

Dla α = -1/3, wykładnik potęgi wynosi 1/(1-1/3) = 3/2 = 1.5.

Wartości wyjściowe dla wskazanych poziomów szarości:
- **H_hyper(40) = 7**
- **H_hyper(45) = 13**
- **H_hyper(50) = 21**

![Obraz po hiperbolizacji](zad7/RezydencjaDiabla_hyperbolized.png)

![Histogram zhiperbolizowanego obrazu](zad7/histogram_hyperbolized.png)

**Interpretacja:** Hiperbolizacja z α = -1/3 silniej rozciąga ciemne obszary (niskie wartości szarości) niż jasne. Wykładnik > 1 powoduje „wypychanie" wartości w kierunku ciemnych tonów, zwiększając kontrast w cieniach. Obraz wydaje się ciemniejszy, ale detale w ciemnych partiach są bardziej wyeksponowane niż przy standardowym wyrównaniu.

**Porównanie metod:**
- **Wyrównanie**: zbalansowane rozciągnięcie całego zakresu, równomierne rozłożenie wartości
- **Hiperbolizacja (α < 0)**: preferencja dla ciemnych tonów, silniejsze podkreślenie detali w cieniach

## Zadanie 9
### Treść
Zwiększenie kontrastu poprzez zastosowanie kolorów ⋆ (1)

Dla jednego z obrazów wyjściowych (przetworzonego obrazu `RezydencjaDiabla.png`) z zadania 7 proszę wykonać transformację obrazu zgodnie z
poniższym diagramem (zwiększenie kontrastu poprzez zastosowanie trzech
funkcji mapowania wartości szarości):

![mapowanie wartości szarości](image.png)

## Zadanie 10
### Treść
Zwiększenie kontrastu poprzez operacje punktowe oparte na histogramie ⋆ (1)

Zdjęcie poniżej (`CalunTurynski.png`, autor: Giuseppe Enrie, 1931 r., pozytyw) przedstawia odwzorowanie twarzy postaci na Całunie Turyńskim.

![CalunTurynski.png](CalunTurynski.png)

Proszę zaproponować i wykonać etapy przetwarzania obrazu oparte na
histogramie, które poprawią efekt wizualny (widoczność) postaci na zdjęciu. Do rozwiązania należy załączyć wyniki poszczególnych kroków metody
wraz z histogramami.

## Zadanie 14
### Treść
Operacje logiczne i arytmetyczne na obrazach ⋆ (0.5 + 0.5)

(a) Jakie operacje arytmetyczne należy wykonać, by podkreślić w kolorze
czerwonym krawędzie obiektów (obraz `bakterie_krawedzie.png`) na
obrazie `bakterie.png`?

![bakterie.png](bakterie.png) ![bakterie_krawedzie.png](bakterie_krawedzie.png)

(b) Jakie operacje logiczne należy wykonać, by podkreślić w kolorze cyjan (turkusowym, (R, G, B) = (0, 255, 255)) krawędzie obiektów na
obrazie `bakterieRGB.png`?

![bakterieRGB.png](bakterieRGB.png) ![bakterie_krawedzie.png](bakterie_krawedzie.png)

## Zadanie 17
### Treść
Okienkowanie obrazu ⋆ (0.5 + 0.5 + 0.5)

Zaszumiony obraz `ptaki.png`:

![ptaki.png](ptaki.png)

Proszę:

(a) przetworzyć oknem sinusoidalnym,

(b) obraz wyjściowy z (a) wygładzić filtrem uśredniającym:

g'(m, n) = (1/9) Σ_{i=-1}^{1} Σ_{j=-1}^{1} g(m - i, n - j).

(c) dokonać korekty gamma obrazu z (b) z odpowiednio dobranym współczynnikiem γ tak, by średnie wartości jasności skorygowanego obrazu
i obrazu `ptaki.png` były do siebie zbliżone.

Wskazówka: Transformacja gamma w ImageJ: Process → Math.

(d) Proszę wykonać uśrednienie bezpośrednio na obrazie `ptaki.png` i opisowo porównać wynik z wynikiem z (c).

## Zadanie 19
### Treść
Steganografia ⋆ (0.5 + 0.5)

W obrazie `AlbertEinstein-modified.png`:

![AlbertEinstein-modified.png](AlbertEinstein-modified.png)

Proszę:

(a) odczytać cytat Einsteina (obraz) schowany w płaszczyźnie bitowej,

(b) zastąpić informację innym obrazem i ukryć go w obrazie wejściowym. (Obraz wyjściowy należy załączyć do rozwiązań jako oddzielny plik.)
