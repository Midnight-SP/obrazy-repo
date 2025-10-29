from ij import IJ, ImagePlus
from ij.process import ByteProcessor
from ij.gui import GenericDialog

# === USER INPUT ===
input_path = "/home/mryduchowski1/obrazy repo/zestaw1/zad11/lwy.png"
output_path = "/home/mryduchowski1/obrazy repo/zestaw1/zad11/lwy_dithered.png"

# Dialog for threshold input
gd = GenericDialog("Floyd-Steinberg Dithering")
gd.addNumericField("Enter threshold T (0-255):", 128, 0)
gd.showDialog()
if gd.wasCanceled():
    print("Canceled by user")
else:
    T = gd.getNextNumber()
    
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
        
        # Create a float array for processing
        pixels = [[0.0 for x in range(w)] for y in range(h)]
        
        # Copy pixels to float array
        for y in range(h):
            for x in range(w):
                pixels[y][x] = float(ip.getPixel(x, y))
        
        # === FLOYD-STEINBERG DITHERING ===
        for y in range(h):
            for x in range(w):
                old_pixel = pixels[y][x]
                new_pixel = 255 if old_pixel >= T else 0
                pixels[y][x] = new_pixel
                error = old_pixel - new_pixel
                
                # Distribute the error to neighbors
                if x + 1 < w:
                    pixels[y][x + 1] += error * 7.0 / 16.0
                if x - 1 >= 0 and y + 1 < h:
                    pixels[y + 1][x - 1] += error * 3.0 / 16.0
                if y + 1 < h:
                    pixels[y + 1][x] += error * 5.0 / 16.0
                if x + 1 < w and y + 1 < h:
                    pixels[y + 1][x + 1] += error * 1.0 / 16.0
        
        # === SAVE OUTPUT ===
        # Create new ByteProcessor and set pixels
        result_ip = ByteProcessor(w, h)
        for y in range(h):
            for x in range(w):
                val = int(max(0, min(255, pixels[y][x])))
                result_ip.putPixel(x, y, val)
        
        result_imp = ImagePlus("Dithered", result_ip)
        IJ.saveAs(result_imp, "PNG", output_path)
        print("Dithering complete. Saved to " + output_path)