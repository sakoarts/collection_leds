import random
import time

from colour import Color

from leds.interaction import BasicLedInteraction
from utils import choose_led
from utils.animation_thread import AnimationThread
from utils.function_memory import run_function, save_and_execute, get_timestamp, set_timesamp
animation_thread = AnimationThread()


def run_continuously(function):
    def wrapper_run_continuously(*args, **kwargs):
        while True:
            function(*args, **kwargs)

    return wrapper_run_continuously


class LedAnimations:
    class __impl:
        """ Implementation of the singleton interface """

        def spam(self):
            """ Test method, return singleton id """
            return id(self)

    # storage for the instance reference
    __instance = None

    def __init__(self, pixels, exclude_leds, n_leds):
        self.pixels = pixels
        global animation_thread
        self.interaction = BasicLedInteraction(pixels, n_leds, animation_thread)
        self.exclude_leds = exclude_leds
        """ Create singleton instance """
        # Check whether we already have an instance
        if LedAnimations.__instance is None:
            # Create and remember instance
            LedAnimations.__instance = LedAnimations.__impl()

        # Store instance reference as the only member in the handle
        self.__dict__['_Singleton__instance'] = LedAnimations.__instance

    def collection_choise_leds(self, choice, r=255, g=255, b=255, factor=0.2, step=0.4):
        for x in range(choice - 2, choice):
            self.pixels[x] = (int(r * factor * factor), int(g * factor), int(b * factor * factor))
            factor += step
        for x in range(choice, choice + 3):
            self.pixels[x] = (int(r * factor * factor), int(g * factor), int(b * factor * factor))
            factor -= step

        self.pixels.show()

    def collection_picker_animation(self, choise, leds, steps=17, wait_for_restore=120):
        set_timesamp()
        last_animation_timestamp = get_timestamp()
        animation_thread.check_and_kill_animation()
        for x in range(steps):
            if last_animation_timestamp != get_timestamp():
                return
            self.pixels.fill((0, 0, 0))
            led = choose_led(leds, self.exclude_leds)
            self.collection_choise_leds(led)
            time.sleep(0.05 * x)

        for x in range(5):
            if last_animation_timestamp != get_timestamp():
                return
            self.pixels.fill((0, 0, 0))
            self.pixels.show()
            time.sleep(0.1)
            self.collection_choise_leds(choise)
            time.sleep(0.1)

        if last_animation_timestamp != get_timestamp():
            return
        time.sleep(wait_for_restore)
        run_function()

    def wheel(self, pos):
        # Input a value 0 to 255 to get a color value.
        # The colours are a transition r - g - b - back to r.
        if pos < 0 or pos > 255:
            r = g = b = 0
        elif pos < 85:
            r = int(pos * 3)
            g = int(255 - pos * 3)
            b = 0
        elif pos < 170:
            pos -= 85
            r = int(255 - pos * 3)
            g = 0
            b = int(pos * 3)
        else:
            pos -= 170
            r = 0
            g = int(pos * 3)
            b = int(255 - pos * 3)
        return r, g, b

    def color_chase(self, leds, color, wait):
        for i in leds:
            self.pixels[i] = color
            time.sleep(wait)
            self.pixels.show()
        time.sleep(0.5)

    def get_circle_color_range(self, colors, range_part_len=100):
        colors = [Color(rgb=(c / 255 for c in x)) for x in colors]
        circle_range = []
        for i, c in enumerate(colors):
            circle_range += colors[i - 1].range_to(c, range_part_len)

        circle_range = [tuple([int(l * 255) for l in c.rgb]) for c in circle_range]

        return circle_range

    def christmas_animation(self, leds, colors=None, range_part_len=50):
        if not colors:
            colors = [(255, 255, 255), (255, 0, 0), (255, 0, 0)]
        color_walk(leds, colors, range_part_len)

    def spring_animation(self, leds, colors=None, range_part_len=50):
        if not colors:
            colors = [(201, 55, 212), (255, 251, 43), (93, 255, 43)]
        color_walk(leds, colors, range_part_len)

    def color_walk(self, leds, colors, range_part_len=50):
        circle_range = self.get_circle_color_range(colors, range_part_len)
        self.walk_animation(leds, circle_range)

    @save_and_execute
    @animation_thread.start_animation
    @run_continuously
    def rainbow_cycle(self, leds, wait):
        for j in range(255):
            for i in leds:
                pixel_index = (i * 256 // len(leds)) + j
                self.pixels[i] = self.wheel(pixel_index & 255)
            self.pixels.show()
            time.sleep(wait)

    @save_and_execute
    @animation_thread.start_animation
    @run_continuously
    def fade_animate(self, leds, circle_range, sleep=0.01):
        for c in circle_range:
            for p in leds:
                self.pixels[p] = c
            self.pixels.show()
            time.sleep(sleep)

    @save_and_execute
    @animation_thread.start_animation
    @run_continuously
    def walk_animation(self, leds, circle_range, sleep=0.01):
        for i in range(len(circle_range)):
            for p in leds:
                color = circle_range[(p + i) % len(circle_range)]
                self.pixels[p] = color
            self.pixels.show()
            time.sleep(sleep)

    @save_and_execute
    @animation_thread.start_animation
    @run_continuously
    def fire_animation(self, leds, factor=1, reduce=80):
        rgb = (255, 96, 12)
        delay = random.choice(range(50, 150)) / 1000
        offset = random.choice([1, 2])

        for p in range(0, len(leds), 3):
            p += offset
            if p >= len(leds) - 1:
                p = len(leds) - 2
            flicker = random.choice(range(reduce))
            rgb_low = tuple([int((x - flicker) * factor) if x - flicker >= 0 else 0 for x in rgb])
            rgb_high = tuple([int((x - flicker/2) * factor) if x - flicker >= 0 else 0 for x in rgb])
            self.pixels[p] = rgb_low
            self.pixels[p - 1] = self.pixels[p+1] = rgb_high
        self.pixels.show()
        time.sleep(delay)

    @save_and_execute
    @animation_thread.start_animation
    @run_continuously
    def twinkle_animation(self, leds, factor=1, reduce=200, rgb=(255, 255, 255)):
        delay = random.choice(range(50, 150)) / 1000

        for p in leds:
            flicker = random.choice(range(reduce))
            rgb_r = tuple([int((x - flicker) * factor) if x - flicker >= 0 else 0 for x in rgb])
            self.pixels[p] = rgb_r
        self.pixels.show()
        time.sleep(delay)
