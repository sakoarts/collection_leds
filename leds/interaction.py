from utils.function_memory import save_and_execute

class BasicLedInteraction:
    class __impl:
        """ Implementation of the singleton interface """

        def spam(self):
            """ Test method, return singleton id """
            return id(self)

    # storage for the instance reference
    __instance = None

    def __init__(self, pixels, n_leds, animation_thread):
        self.pixels = pixels
        self.animation_thread = animation_thread
        self.n_leds = n_leds
        """ Create singleton instance """
        # Check whether we already have an instance
        if BasicLedInteraction.__instance is None:
            # Create and remember instance
            BasicLedInteraction.__instance = BasicLedInteraction.__impl()

        # Store instance reference as the only member in the handle
        self.__dict__['_Singleton__instance'] = BasicLedInteraction.__instance

    def set_pixel(self, p, r, g, b, verbose=0):
        self.animation_thread.check_and_kill_animation()
        if verbose > 9:
            print(f'Setting pixel {p} to ({r},{g},{b})')
        self.pixels[p] = (r, g, b)
        self.pixels.show()

    @save_and_execute
    def set_only_pixel(self, p, r, g, b, verbose=10):
        self.animation_thread.check_and_kill_animation()
        self.pixels.fill((0, 0, 0))
        self.set_pixel(p, r, g, b, verbose=verbose)

    @save_and_execute
    def set_all_leds(self, r=0, g=0, b=0):
        self.animation_thread.check_and_kill_animation()
        for p in range(self.n_leds):
            self.pixels[p] = (r, g, b)
        self.pixels.show()

    @save_and_execute
    def set_some_leds(self, r=0, g=0, b=0, leds=None, sled=0, eled=None):
        self.animation_thread.check_and_kill_animation()
        if not eled:
            eled = self.n_leds
        if not leds:
            leds = range(sled, eled)
        for p in leds:
            self.pixels[p] = (r, g, b)
        self.pixels.show()
