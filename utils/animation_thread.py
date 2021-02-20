import multiprocessing

animation_thread = None

class AnimationThread:
    class __impl:
        """ Implementation of the singleton interface """

        def spam(self):
            """ Test method, return singleton id """
            return id(self)

    # storage for the instance reference
    __instance = None

    def __init__(self):
        global animation_thread
        self.animation_thread = animation_thread
        """ Create singleton instance """
        # Check whether we already have an instance
        if AnimationThread.__instance is None:
            # Create and remember instance
            AnimationThread.__instance = AnimationThread.__impl()

        # Store instance reference as the only member in the handle
        self.__dict__['_Singleton__instance'] = AnimationThread.__instance

    def start_animation(self, function):
        def wrapper(*args, **kwargs):
            global animation_thread
            self.check_and_kill_animation()
            self.animation_thread = multiprocessing.Process(target=function, args=args, kwargs=kwargs)
            self.animation_thread.start()

        return wrapper

    def check_and_kill_animation(self):
        global animation_thread
        if self.animation_thread:
            try:
                if self.animation_thread.is_alive():
                    try:
                        self.animation_thread.terminate()
                        self.animation_thread.kill()
                        self.animation_thread.join()
                        #self.animation_thread = None
                    except AttributeError as e:
                        print(f'Thread probably already killed: {e}')
            except AssertionError as e:
                print(f'Probably no animation thread running: {e}')