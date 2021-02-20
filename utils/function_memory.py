import time

most_recent_function = lambda: None
most_recent_args = ()
most_recent_kwargs = {}
most_recent_timestamp = 0


# Decorator function that saves the properties of the decorated function
def save_and_execute(function):
    def wrapper(*args, **kwargs):
        set_function(function, args=args, kwargs=kwargs)
        return function(*args, **kwargs)

    # Renaming the function name
    wrapper.__name__ = function.__name__
    return wrapper


def set_function(function, args=(), kwargs={}):
    global most_recent_function
    global most_recent_args
    global most_recent_kwargs
    most_recent_function = function
    most_recent_args = args
    most_recent_kwargs = kwargs
    set_timesamp()


def set_timesamp():
    global most_recent_timestamp
    most_recent_timestamp = time.time()


def get_timestamp():
    return most_recent_timestamp


def run_function():
    return most_recent_function(*most_recent_args, **most_recent_kwargs)
