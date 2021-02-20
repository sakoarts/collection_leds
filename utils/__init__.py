import random


def choose_led(leds, exclude=[]):
    led = random.choice(leds)
    if led in exclude:
        led = choose_led(leds, exclude=exclude)
    return led
