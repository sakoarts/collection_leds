import board
import neopixel

N_LEDS = 216
data_pin = "D18"

pixels = neopixel.NeoPixel(eval(f"board.{data_pin'}"), N_LEDS, auto_write=False, pixel_order=neopixel.RGB)

def set_pixel(p, r, g, b, verbose=10):
	if verbose > 9:
            print(f'Setting pixel {p} to ({r},{g},{b})')
	pixels[p] = (r, g, b)
	pixels.show()

r = 255
b = 255
g = 255
p = 10

set_pixel(p, r, g, b)