"""Purpose: Coordinate user function calls between APA102, PixelRing, and pattern.py objects"""
import threading
import queue as Queue
import collections
from .doa import get_direction
from .apa102 import APA102
from .pattern import Custom, GoogleHome


class PixelRing(object):
    """Creates a PixelRing object for actioning various function calls.

    Essentially serves as the frontend of the pixel ring, handling the communication between the
    user and their calls to the LED patterns, and between the pattern object and the APA102 driver.
    """
    
    PIXELS_N = 12   # All supported ReSpeaker arrays have 12 APA102 LEDs

    def __init__(self):
        """Inits PixelRing with a thread queue, AP102 driver object, and default pattern object."""
        self.pattern = Custom([0,0,0], [0,0,0], show=self.show)
        self.dev = APA102(num_led=self.PIXELS_N)
        self.queue = Queue.Queue()
        self.main_thread = threading.Thread(target=self._run)
        self.main_thread.daemon = True
        self.main_thread.start()
        self.mic_thread = threading.Thread(target=self.doa_listen)
        self.mic_thread.daemon = True
        self.mic_thread.start()
        self.off()

    def set_brightness(self, brightness):
        """Sets global brightness for APA102 driver.

        Note that maximum brightness cannot exceed 31 (0b11111) for LEDs' safety.

        Args:
            brightness: A number repersenting a percentage of maximum brightness.
        """
        brightness = min(max(brightness, 1), 100)   # Clamp brightness from 1-100%
        self.dev.global_brightness = int(0b11111 * (brightness / 100))

    def change_pattern(self, pattern, primary_color=[0, 0, 255], secondary_color=[255, 255, 255]):
        """Sets color patterns for all LED functions.

        Args:
            pattern: A string containing a valid class name from pattern.py
            primary_color: A list formatted as [R, G, B] for the main LED color.
            secondary_color: A list formatted as [R, G, B] for the second LED color.
        """
        if pattern == 'google':
            self.pattern = GoogleHome(show=self.show)
        else:
            self.pattern = Custom(primary_color, secondary_color, show=self.show)

    def wakeup(self):
        """Activates pattern's wakeup function."""    
        direction = get_direction();
        def queue_wrapper():
            """Passes self.pattern.wakeup() into queue_wrapper().

            This prevents a NoneType runtime error from occurring where Queue sees
            self.pattern.wakeup() as a function instead of as an object.
            """
            self.pattern.wakeup(direction)

        self.put(queue_wrapper)

    def listen(self):
        """Activates pattern's listen function."""
        self.put(self.pattern.listen)

    def think(self, speed=0.25):
        """Activates pattern's think function."""
        def queue_wrapper():
            """Passes self.pattern.think() into queue_wrapper().

            This prevents a NoneType runtime error from occurring where Queue sees
            self.pattern.think() as a function instead of as an object.
            """
            self.pattern.think(speed)

        self.put(queue_wrapper)

    wait = think    # Assignment of pixel_ring.wait() as pixel_ring.think()

    def speak(self, speed=0.5):
        """Activates pattern's speak function."""
        def queue_wrapper():
            """Passes self.pattern.speak() into queue_wrapper().

            This prevents a NoneType runtime error from occurring where Queue sees
            self.pattern.speak() as a function instead of as an object.
            """
            self.pattern.speak(speed)

        self.put(queue_wrapper)

    def off(self):
        """Queues LEDs to be shut off.

        Doesn't properly turn LEDs off (i.e. set LED(5) to off).
        Instead passes [0, 0, 0] to all LEDs, which has the same visual effect.
        Care should be taken to set LED(5) to off through gpiozero when finished with the LEDs.
        """
        self.put(self.pattern.off)

    def put(self, func):
        """Manages queueing function calls for execution."""
        self.pattern.stop = True
        self.queue.put(func)

    def _run(self):
        """Controls running passed functions to the LEDs."""
        while True:
            func = self.queue.get()
            self.pattern.stop = False
            func()

    def show(self, data):
        """Sends data array for displaying to APA102 driver.

        Args:
            data: A list containing all RGB values for all LEDs in [R, G, B] format.
        """
        # TODO: Rewrite to not require PIXELS_N cross-file function calls
        for pixel in range(self.PIXELS_N):
            self.dev.set_pixel(
                pixel,
                int(data[3 * pixel + 0]),
                int(data[3 * pixel + 1]),
                int(data[3 * pixel + 2]))

        self.dev.show()

    def doa_listen():



if __name__ == '__main__':
    import time

    pixel_ring = PixelRing()
    while True:
        try:
            pixel_ring.wakeup()
            time.sleep(3)
            pixel_ring.think()
            time.sleep(3)
            pixel_ring.speak()
            time.sleep(6)
            pixel_ring.off()
            time.sleep(3)
        except KeyboardInterrupt:
            break


    pixel_ring.off()
    time.sleep(1)
