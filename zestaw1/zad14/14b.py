from ij import IJ, ImagePlus
from ij.process import ByteProcessor

# === Load grayscale image ===
input_path = "/home/mryduchowski1/obrazy repo/zestaw1/zad14/lwy.png"
output_path = "/home/mryduchowski1/obrazy repo/zestaw1/zad14/lwy_dithered.png"

imp = IJ.openImage(input_path)
if imp is None:
    print("Cannot open image: " + input_path)
else:
    # Convert to grayscale
    IJ.run(imp, "8-bit", "")
    ip = imp.getProcessor()
    width = ip.getWidth()
    height = ip.getHeight()
    
    # === 3x3 Dithering matrix ===
    D = [
        [7, 1, 5],
        [3, 0, 2],
        [4, 8, 6]
    ]
    N = 3
    M = N * N  # 9
    
    # === Apply ordered dithering ===
    result_ip = ByteProcessor(width, height)
    
    for y in range(height):
        for x in range(width):
            pixel_val = float(ip.getPixel(x, y))
            # Find threshold from D
            threshold = ((float(D[y % N][x % N]) + 0.5) / float(M)) * 255.0
            new_val = 255 if pixel_val > threshold else 0
            result_ip.putPixel(x, y, new_val)
    
    # === Save result ===
    result_imp = ImagePlus("Dithered", result_ip)
    IJ.saveAs(result_imp, "PNG", output_path)
    print("Saved '" + output_path + "'")
