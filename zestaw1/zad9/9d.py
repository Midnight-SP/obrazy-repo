from ij import IJ, ImagePlus
from ij.process import ColorProcessor
from java.lang import Math

# Full paths to input and output files
input_path = "/home/mryduchowski1/obrazy repo/zestaw1/zad9/potworek_pixelart.png"
output_path = "/home/mryduchowski1/obrazy repo/zestaw1/zad9/potworek_pixelart_scaled.png"
target_width, target_height = 500, 650

def custom_interpolate(pixels, w_in, h_in, new_w, new_h):
    result = [0] * (new_w * new_h)
    scale_x = float(w_in) / new_w
    scale_y = float(h_in) / new_h
    
    for y_out in range(new_h):
        for x_out in range(new_w):
            src_x = x_out * scale_x
            src_y = y_out * scale_y
            x0 = int(Math.floor(src_x))
            y0 = int(Math.floor(src_y))
            x1 = min(x0 + 1, w_in - 1)
            y1 = min(y0 + 1, h_in - 1)
            
            # Get 4 neighbor values
            neighbors = [
                float(pixels[y0 * w_in + x0]),
                float(pixels[y0 * w_in + x1]),
                float(pixels[y1 * w_in + x0]),
                float(pixels[y1 * w_in + x1])
            ]
            
            # Calculate (max + min) / 2
            max_val = max(neighbors)
            min_val = min(neighbors)
            val = (max_val + min_val) / 2.0
            
            result[y_out * new_w + x_out] = int(max(0, min(255, val)))
    
    return result

# Load image
imp = IJ.openImage(input_path)
if imp is None:
    print("Cannot open image: " + input_path)
else:
    ip = imp.getProcessor()
    w_in = ip.getWidth()
    h_in = ip.getHeight()
    
    # Get pixel array directly from ColorProcessor
    pixels_in = ip.getPixels()
    
    # Extract RGB channels from packed int pixels
    r_pixels = [0] * (w_in * h_in)
    g_pixels = [0] * (w_in * h_in)
    b_pixels = [0] * (w_in * h_in)
    
    for i in range(len(pixels_in)):
        rgb = pixels_in[i]
        r_pixels[i] = (rgb >> 16) & 0xff
        g_pixels[i] = (rgb >> 8) & 0xff
        b_pixels[i] = rgb & 0xff
    
    # Scale each channel using custom interpolation
    r_scaled = custom_interpolate(r_pixels, w_in, h_in, target_width, target_height)
    g_scaled = custom_interpolate(g_pixels, w_in, h_in, target_width, target_height)
    b_scaled = custom_interpolate(b_pixels, w_in, h_in, target_width, target_height)
    
    # Create ColorProcessor and set pixels directly
    cp = ColorProcessor(target_width, target_height)
    for i in range(len(r_scaled)):
        r_val = r_scaled[i]
        g_val = g_scaled[i]
        b_val = b_scaled[i]
        rgb = ((r_val & 0xff) << 16) | ((g_val & 0xff) << 8) | (b_val & 0xff)
        x = i % target_width
        y = i / target_width
        cp.putPixel(x, y, rgb)
    
    # Save result
    result_imp = ImagePlus("Scaled", cp)
    IJ.saveAs(result_imp, "PNG", output_path)
    print("Saved scaled image to " + output_path)