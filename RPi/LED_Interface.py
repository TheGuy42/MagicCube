from time import sleep
import neopixel
import board
from config import Color


class LED:

    def __init__(self, NumOfPixels):
        pixel_pin = board.D18
        self.NumOfPixels = NumOfPixels
        ORDER = neopixel.GRB
        self.Settings = Color()
        self.CurrentBrightness = self.Settings.DefaultBrightness
        self.pixel = neopixel.NeoPixel(pixel_pin, self.NumOfPixels, brightness=self.Settings.DefaultBrightness,
                                       auto_write=False, pixel_order=ORDER)
        self.startup_effect()

    def startup_effect(self):
        self.set_preset(self.Settings.PRST_Default)
        self.brightness_rainbow_effect()

    def update(self):
        self.pixel.show()

    def change_brightness(self, Brightness):
        self.pixel.brightness = Brightness
        self.update()
        self.CurrentBrightness = Brightness

    def set_Color(self, axis, color):
        self.pixel[axis] = color
        self.update()

    def set_preset(self, preset, change_brightness=False):
        for axis in range(self.NumOfPixels):
            self.pixel[axis] = preset['Color'][axis]
        if change_brightness:
            self.change_brightness(preset['Brightness'])
        self.update()

    def brightness_fade_down(self, threshold=0.0, delay=0.03, step=0.1):
        br = self.CurrentBrightness
        while br > threshold:
            self.change_brightness(br)
            sleep(delay)
            br -= step
        self.change_brightness(threshold)

    def brightness_fade_up(self, threshold, delay=0.03, step=0.1):
        br = self.CurrentBrightness
        while br < threshold:
            self.change_brightness(br)
            sleep(delay)
            br += step
        self.change_brightness(threshold)

    def brightness_rainbow_effect(self, count=1, delay=0.03, step=0.1):
        current_brightness = self.CurrentBrightness
        for i in range(count):
            self.brightness_fade_up(1.0, delay=delay, step=step)
            self.brightness_fade_down(delay=delay, step=step)
            self.brightness_fade_up(current_brightness, delay=delay, step=step)

