import os
import json
from threading import Thread

import board
import neopixel
import atexit
from flask import Flask, render_template
from flask import request
from colour import Color
import colorsys

from utils import choose_led
from leds.interaction import BasicLedInteraction
from leds.animations import LedAnimations, animation_thread
from utils.parse_settings import determine_segments, determine_exclude_choice_leds

app = Flask(__name__)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS = json.load(open(os.path.join(ROOT_DIR, "config", "settings.json")))
N_LEDS = SETTINGS['n_leds']
SEGMENTS = determine_segments(SETTINGS['segments'])
EXCLUDE_LEDS = determine_exclude_choice_leds(SETTINGS['exclude_picker'], SEGMENTS)

pixels = neopixel.NeoPixel(eval(f"board.{SETTINGS['data_pin']}"), N_LEDS, auto_write=False, pixel_order=eval(f"neopixel.{SETTINGS['color_order']}"))

animations = LedAnimations(pixels, EXCLUDE_LEDS, N_LEDS)
interaction = BasicLedInteraction(pixels, N_LEDS, animation_thread)


@app.route('/collection')
def index():
    return render_template('index.html')


@app.route('/collection/picker')
def collection_picker_web():
    section = check_get_default(request.args.get('section'), None)

    leds_available = range(N_LEDS)
    if section is not None and section < len(SEGMENTS):
        leds_available = SEGMENTS[section]

    led = choose_led(leds_available, exclude=EXCLUDE_LEDS)
    thread = Thread(target=animations.collection_picker_animation, args=(led, leds_available))
    thread.start()

    return f'Collection {led} was chosen'


# http://collection_led:5000/collection/collection-pixel?r=28&g=155&b=155&p=0
@app.route('/collection/collection-pixel')
def set_pixel_web():
    p = int(request.args.get('p'))
    r = int(request.args.get('r'))
    g = int(request.args.get('g'))
    b = int(request.args.get('b'))

    interaction.set_pixel(p, r, g, b, verbose=10)
    return 'done'


# http://collection_led:5000/collection/chase?r=28&g=155&b=155&speed=0.001&sled=0&eled=140
@app.route('/collection/chase')
def play_chase_web():
    leds = web_get_leds(request.args)
    rgb = web_get_rgb(request.args)
    speed = check_get_default(request.args.get('speed'), 0.001, float)

    animations.color_chase(leds, rgb, speed)

    return 'done'


# http://collection_led:5000/collection/rainbow?sled=0&eled=140
@app.route('/collection/rainbow')
def play_rainbow_web():
    leds = web_get_leds(request.args)
    animations.rainbow_cycle(leds, 0.001)

    return 'done'


# http://collection_led:5000/collection/fire?sled=0&eled=140&factor=0.75
@app.route('/collection/fire')
def play_fire_web():
    reduce = check_get_default(request.args.get('reduce'), 80)
    factor = check_get_default(request.args.get('factor'), 1, float)
    leds = web_get_leds(request.args)
    animations.fire_animation(leds, factor, reduce)

    return 'done'


# http://collection_led:5000/collection/all-off
@app.route('/collection/all-off')
def all_off_web():
    interaction.set_all_leds()
    return 'All leds are turend off'


# http://collection_led:5000/collection/leds?r=28&g=155&b=155&sled=0&eled=140&color=goldenrod
@app.route('/collection/leds')
def set_leds_web():
    leds = web_get_leds(request.args)
    r, g, b = web_get_rgb(request.args)
    color = check_get_default(request.args.get('color'), None, str)
    if color:
        r, g, b = tuple([int(l * 255) for l in Color(color).rgb])

    interaction.set_some_leds(r, g, b, leds)

    return 'done'


# http://collection_led:5000/collection/hsv?online=true&on=true&brightness=100&hue=208&saturation=0.05882352963089943&value=1
@app.route('/collection/hsv')
def set_hsv_web():
    r, g, b, brightness, on = web_get_google_hsv_to_rgb(request.args)
    leds = web_get_leds(request.args)
    if on == 'false':
        interaction.set_some_leds(0, 0, 0)
        return 'done'

    interaction.set_some_leds(r, g, b, leds)

    return 'done'


# http://collection_led:5000/collection/christmas
@app.route('/collection/christmas')
def play_christmas_web():
    leds = web_get_leds(request.args)
    animations.christmas_animation(leds, None)

    return 'done'


# http://collection_led:5000/collection/twinkle?sled=0&eled=218&factor=1&reduce=200&r=28&g=155&b=155
@app.route('/collection/twinkle')
def play_twinkle_web():
    reduce = check_get_default(request.args.get('reduce'), 200)
    factor = check_get_default(request.args.get('factor'), 1, float)
    leds = web_get_leds(request.args)

    if request.args.get('on'):
        r, g, b, brightness, on = web_get_google_hsv_to_rgb(request.args)
        if on == 'false':
            interaction.set_some_leds(0, 0, 0)
            return 'done'
    else:
        r, g, b = web_get_rgb(request.args)
    animations.twinkle_animation(leds, factor, reduce, (r, g, b))

    return 'done'


def web_get_rgb(web_args):
    r = check_get_default(web_args.get('r'), 0)
    g = check_get_default(web_args.get('g'), 0)
    b = check_get_default(web_args.get('b'), 0)
    return r, g, b


def web_get_google_hsv(web_args):
    h = check_get_default(web_args.get('hue'), 0, float)
    s = check_get_default(web_args.get('saturation'), 0, float)
    v = check_get_default(web_args.get('value'), 0, float)
    brightness = check_get_default(web_args.get('brightness'), 100, int)
    on = check_get_default(web_args.get('on'), 'false', str)
    return h, s, v, brightness, on


def web_get_google_hsv_to_rgb(web_args):
    h, s, v, brightness, on = web_get_google_hsv(web_args)
    r, g, b = (int((x * 255) * (brightness / 100)) for x in colorsys.hsv_to_rgb(h / 360, s, v))
    return r, g, b, brightness, on


def web_get_leds(web_args):
    sled = check_get_default(web_args.get('sled'), 0)
    eled = check_get_default(web_args.get('eled'), N_LEDS)
    return range(sled, eled)


def check_get_default(get_value, default, vtype=int):
    if get_value:
        return vtype(get_value)
    else:
        return default


def on_server_termination():
    interaction.set_all_leds()


@app.errorhandler(500)
def internal_error(exception):
    app.logger.error(exception)
    return exception, 500


if app.debug is not True:
    import logging
    from logging.handlers import RotatingFileHandler

    log_file = 'logs/python.log'
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    file_handler = RotatingFileHandler(log_file, maxBytes=1024 * 1024 * 100, backupCount=20)
    file_handler.setLevel(logging.WARNING)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)

if __name__ == '__main__':
    atexit.register(on_server_termination)
    app.run(host='0.0.0.0', debug=True)
