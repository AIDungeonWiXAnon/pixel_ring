USAGE='''
Purpose: Determine version of attached mic array.

Notes: If you are using the ReSpeaker 4 Mic Array, ReSpeaker 6-Mic Circular Array, or ReSpeaker V2,
there is a power-enable pin which needs to be enabled before the array's LEDs can be used. Example:

    ReSpeaker 4 Mic Array for Pi & ReSpeaker 6-Mic Circular Array:
        from gpiozero import LED
        power = LED(5)
        power.on()

    Respeaker V2:
        import mraa
        power = mraa.Gpio(12)
        power.dir(mraa.DIR_OUT)
        power.write(0)

Additionally, a full-fledged example of how to begin useing the library:
    ReSpeaker 4 Mic Array for Pi & ReSpeaker 6-Mic Circular Array:
        from pixel_ring import pixel_ring
        from gpiozero import LED
        power = LED(5)
        power.on()
        pixel_ring.set_brightness(10)
        pixel_ring.set_pattern('custom', [0, 0, 255], [0, 192, 255])
        pixel_ring.wait()
    Respeaker V2:
        # TODO: Add working example for ReSpeaker V2
'''
# TODO: Build a new example.py
from . import usb_pixel_ring_v1
from . import usb_pixel_ring_v2
from .apa102_pixel_ring import PixelRing

pixel_ring = usb_pixel_ring_v2.find()

if not pixel_ring:
    pixel_ring = usb_pixel_ring_v1.find()

if not pixel_ring:
    pixel_ring = PixelRing()


def main():
    if isinstance(pixel_ring, usb_pixel_ring_v2.PixelRing):
        print('Found ReSpeaker USB 4 Mic Array')
    elif isinstance(pixel_ring, usb_pixel_ring_v1.UsbPixelRing):
        print('Found ReSpeaker USB 6+1 Mic Array')
    else:
        print('Control APA102 RGB LEDs via SPI')
        print(USAGE)


if __name__ == '__main__':
    main()
