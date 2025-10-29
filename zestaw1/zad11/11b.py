from ij import IJ, ImagePlus
from ij.process import ByteProcessor

# === CONFIGURATION ===
input_path = "/home/mryduchowski1/obrazy repo/zestaw1/zad11/lwy.png"
output_a_path = "/home/mryduchowski1/obrazy repo/zestaw1/zad11/lwy_dithered_109.png"
output_b_path = "/home/mryduchowski1/obrazy repo/zestaw1/zad11/lwy_dithered_5levels.png"

# --- (a) 1-bit threshold ---
T = 109

# --- (b) 5-level quantization ranges ---
def quantize_5_levels(val):
    if val < 20:
        return 0
    elif val < 40:
        return 64
    elif val < 60:
        return 128
    elif val < 120:
        return 192
    else:
        return 255

# === Jarvis-Judice-Ninke kernel ===
# Relative positions (dx, dy) and their weights
JJN_KERNEL = [
    (1, 0, 7), (2, 0, 5),
    (-2, 1, 3), (-1, 1, 5), (0, 1, 7), (1, 1, 5), (2, 1, 3),
    (-2, 2, 1), (-1, 2, 3), (0, 2, 5), (1, 2, 3), (2, 2, 1)
]
JJN_DIVISOR = 48.0

def apply_jjn_dither(img_array, w, h, quantize_fn):
    """Apply JJN dithering using a given quantization function."""
    # Create a copy of pixels as 2D list
    pixels = [[0.0 for x in range(w)] for y in range(h)]
    for y in range(h):
        for x in range(w):
            pixels[y][x] = float(img_array[y][x])
    
    for y in range(h):
        for x in range(w):
            old_pixel = pixels[y][x]
            new_pixel = quantize_fn(old_pixel)
            pixels[y][x] = new_pixel
            error = old_pixel - new_pixel
            
            # Diffuse error according to JJN
            for dx, dy, weight in JJN_KERNEL:
                nx = x + dx
                ny = y + dy
                if 0 <= nx < w and 0 <= ny < h:
                    pixels[ny][nx] += error * (float(weight) / JJN_DIVISOR)
    
    # Clip and return as 1D list
    result = []
    for y in range(h):
        for x in range(w):
            val = int(max(0, min(255, pixels[y][x])))
            result.append(val)
    return result

# === LOAD IMAGE ===
imp = IJ.openImage(input_path)
if imp is None:
    print("Cannot open image: " + input_path)
else:
    # Convert to grayscale
    IJ.run(imp, "8-bit", "")
    ip = imp.getProcessor()
    w = ip.getWidth()
    h = ip.getHeight()
    
    # Get pixels as 2D list
    gray = [[0 for x in range(w)] for y in range(h)]
    for y in range(h):
        for x in range(w):
            gray[y][x] = ip.getPixel(x, y)
    
    # --- (a) 1-bit reduction using threshold T = 109 ---
    def quantize_1bit(val):
        return 255 if val >= T else 0
    
    result_a = apply_jjn_dither(gray, w, h, quantize_1bit)
    
    # Create output image for (a)
    result_a_ip = ByteProcessor(w, h)
    for y in range(h):
        for x in range(w):
            result_a_ip.putPixel(x, y, result_a[y * w + x])
    
    result_a_imp = ImagePlus("Dithered_1bit", result_a_ip)
    IJ.saveAs(result_a_imp, "PNG", output_a_path)
    print("Saved 1-bit JJN dithered image (T=" + str(T) + ") -> " + output_a_path)
    
    # --- (b) 5-level quantization ---
    result_b = apply_jjn_dither(gray, w, h, quantize_5_levels)
    
    # Create output image for (b)
    result_b_ip = ByteProcessor(w, h)
    for y in range(h):
        for x in range(w):
            result_b_ip.putPixel(x, y, result_b[y * w + x])
    
    result_b_imp = ImagePlus("Dithered_5level", result_b_ip)
    IJ.saveAs(result_b_imp, "PNG", output_b_path)
    print("Saved 5-level JJN dithered image -> " + output_b_path)