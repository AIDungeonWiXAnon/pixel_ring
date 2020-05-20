"""
LED patterns
"""

import time

from itertools import cycle


class Custom(object):

    def __init__(self, primary_color, secondary_color, show, num_pixels=12):
        self.pixels_count = num_pixels
        self.main_color = primary_color
        self.second_color = secondary_color

        if not callable(show):
            raise ValueError('show parameter is not callable')

        self.show = show
        self.stop = False

    def wakeup(self, direction=0):
        position = int((direction + 15) / (360 / self.pixels_count)) % self.pixels_count

        pixels = self.main_color * self.pixels_count
        pixels[position * 3 + 0] = self.second_color[0]
        pixels[position * 3 + 1] = self.second_color[1]
        pixels[position * 3 + 2] = self.second_color[2]

        self.show(pixels)

    def listen(self):
        pixels = self.main_color * self.pixels_count

        self.show(pixels)

    def think(self):
        pixels = (self.second_color + self.main_color) * self.pixels_count

        while not self.stop:
            self.show(pixels)
            time.sleep(0.25)
            pixels = pixels[-3:] + pixels[:-3]

    def speak(self):
        pixels = cycle([
            self.main_color * self.pixels_count,
            self.second_color * self.pixels_count])
        while not self.stop:
            self.show(next(pixels))
            time.sleep(0.5)

    def off(self):
        self.show([0, 0, 0] * self.pixels_count)

class GoogleHome(object):
   
    def __init__(self, show, num_leds=12):
        self.pixels_count = num_leds
        self.basis = [0, 0, 0] * num_leds
        self.basis[0 * 3 + 0] = 8
        self.basis[3 * 3 + 0] = 4
        self.basis[3 * 3 + 1] = 4
        self.basis[6 * 3 + 1] = 8
        self.basis[9 * 3 + 2] = 8

        self.pixels = self.basis

        if not callable(show):
            raise ValueError('show parameter is not callable')

        self.show = show
        self.stop = False

    def wakeup(self, direction=0):
        position = int((direction + 90 + 15) / 30) % 12

        basis = self.basis[position * -3:] + self.basis[:position * -3]
        
        pixels = [v * 25 for v in basis]
        self.show(pixels)
        time.sleep(0.1)

        pixels = pixels[-3:] + pixels[:-3]
        self.show(pixels)
        time.sleep(0.1)

        for i in range(2):
            new_pixels = pixels[-3:] + pixels[:-3]
            
            self.show([v / 2 + pixels[index] for index, v in enumerate(new_pixels)])
            pixels = new_pixels
            time.sleep(0.1)

        self.show(pixels)
        self.pixels = pixels

    def listen(self):
        pixels = self.pixels
        for i in range(1, 25):
            self.show([(v * i / 24) for v in pixels])
            time.sleep(0.01)

    def think(self):
        pixels = self.pixels

        while not self.stop:
            pixels = pixels[-3:] + pixels[:-3]
            self.show(pixels)
            time.sleep(0.25)

        t = 0.1
        for i in range(0, 5):
            pixels = pixels[-3:] + pixels[:-3]
            self.show([(v * (4 - i) / 4) for v in pixels])
            time.sleep(t)
            t /= 2

        self.pixels = pixels

    def speak(self):
        pixels = self.pixels
        step = 1
        brightness = 5
        while not self.stop:
            self.show([(v * brightness / 24) for v in pixels])
            time.sleep(0.02)

            if brightness <= 5:
                step = 1
                time.sleep(0.48)
            elif brightness >= 24:
                step = -1
                time.sleep(0.48)

            brightness += step

    def off(self):
        self.show([0, 0, 0] * self.pixels_count)
