import threading
import queue as Queue
from .apa102 import APA102
from .pattern import Custom, GoogleHome


class PixelRing(object):
    PIXELS_N = 12

    def __init__(self):
        self.pattern = Custom([0,0,0], [0,0,0], show=self.show)
        self.dev = APA102(num_led=self.PIXELS_N)
        self.queue = Queue.Queue()
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()
        self.off()

    def set_brightness(self, brightness):
        if brightness > 100:
            brightness = 100

        if brightness > 0:
            self.dev.global_brightness = int(0b11111 * brightness / 100)

    def set_pattern(self, pattern, primary_color, secondary_color):
        if pattern == 'google':
            self.pattern = GoogleHome(show=self.show)
        else:
            self.pattern = Custom(primary_color, secondary_color, show=self.show)

    def wakeup(self, direction=0):
        def f():
            self.pattern.wakeup(direction)

        self.put(f)

    def listen(self):
        self.put(self.pattern.listen)

    def think(self):
        self.put(self.pattern.think)
    wait = think

    def speak(self):
        self.put(self.pattern.speak)

    def off(self):
        self.put(self.pattern.off)

    def put(self, func):
        self.pattern.stop = True
        self.queue.put(func)

    def _run(self):
        while True:
            func = self.queue.get()
            self.pattern.stop = False
            func()

    def show(self, data):
        for pixel in range(self.PIXELS_N):
            self.dev.set_pixel(
                pixel,
                int(data[3 * pixel + 0]),
                int(data[3 * pixel + 1]),
                int(data[3 * pixel + 2]))

        self.dev.show()


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
