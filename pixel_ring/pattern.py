"""Purpose: Provide template classes with preset LED patterns for use with Respeaker LED rings."""

import time

from itertools import cycle


class Custom(object):
    """Creates a Custom object with preset LED patterns built-in.

    Previously the Echo class, this now supports custom LED colors for its various patterns.
    Changing colors is possible, but presently unintuitive. This is a TODO for later. Moreover,
    this class will serve as the testbed for any future functionality additions.
    """

    def __init__(self, primary_color, secondary_color, show, num_pixels=12):
        """Inits Custom object with two colors and 12 LEDS, plus tests ability to affect LEDs."""
        self.pixels_count = num_pixels
        self.main_color = primary_color
        self.second_color = secondary_color

        if not callable(show):
            raise ValueError('show parameter is not callable')

        self.show = show
        self.stop = False

    def wakeup(self, direction=0):
        """Sets all LEDs to the main color plus a DOA LED set to the second color.

        Args:
            direction: DOA in degrees for DOA LED's positioning. Defaults to LED 1.
        """
        # TODO: Program DOA functionality
        position = int((direction + 15) / (360 / self.pixels_count)) % self.pixels_count

        pixels = self.main_color * self.pixels_count
        pixels[position * 3 + 0] = self.second_color[0]
        pixels[position * 3 + 1] = self.second_color[1]
        pixels[position * 3 + 2] = self.second_color[2]

        self.show(pixels)

    def listen(self):
        """Sets all LEDs to main color."""
        pixels = self.main_color * self.pixels_count

        self.show(pixels)

    def think(self, speed=0.25):
        """Rotates an alteration of the main color and second color on all LEDs.

        Args:
            speed: speed of rotation in seconds.
        """
        pixels = (self.second_color + self.main_color) * self.pixels_count
        while not self.stop:
            self.show(pixels)
            time.sleep(speed)
            pixels = pixels[-3:] + pixels[:-3]

    def speak(self, speed=0.5):
        """Cycles all LEDs between the main and second colors.
        
        Args:
            speed: speed of cycling in seconds.
        """
        pixels = cycle([
            self.main_color * self.pixels_count,
            self.second_color * self.pixels_count])
        while not self.stop:
            self.show(next(pixels))
            time.sleep(speed)

    # TODO: Add function to change colors    

    def off(self):
        """Turns off all LEDs.

        Does not actually turn off the LEDs through the power pin, but instead passes [0, 0, 0] to
        all LEDs. The visual result is the same, however. Importantly, this currently needs to be
        run BEFORE changing the pattern, or the old pattern will be unremoveable.
        """
        self.show([0, 0, 0] * self.pixels_count)

class GoogleHome(object):
    """Creates a GoogleHome object with preset LED patterns built-in that mimic a Google Home.

    Only preliminary edits have been done here where they were obvious, but this class is otherwise
    untested. Not presently a huge focus since most users would like a custom color scheme for their
    Mycroft-based AIs.
    This library is being built with uses other than Mycroft in mind, but when they require work
    that is tangential to Mycroft, they will be done secondarily.
    """
    # FIXME: Refactor and test existing code with new PixelRing class.
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

    def think(self, speed=0.25):
        pixels = self.pixels

        while not self.stop:
            pixels = pixels[-3:] + pixels[:-3]
            self.show(pixels)
            time.sleep(speed)

        t = 0.1
        for i in range(0, 5):
            pixels = pixels[-3:] + pixels[:-3]
            self.show([(v * (4 - i) / 4) for v in pixels])
            time.sleep(t)
            t /= 2

        self.pixels = pixels

    def speak(self, speed=0.5):
        pixels = self.pixels
        step = 1
        brightness = 5
        while not self.stop:
            self.show([(v * brightness / 24) for v in pixels])

            if brightness <= 5:
                step = 1
                time.sleep(speed)
            elif brightness >= 24:
                step = -1
                time.sleep(speed)

            brightness += step

    def off(self):
        self.show([0, 0, 0] * self.pixels_count)
