import time

settings = {
    'default_topics': {
        '__STARTUP_TIME__': time.time(),
    },
    'basic_path': [
        {
            "translation": {"x": 0.0, "y": 0.5}, 
            "rotation": {"x": 0},
            "water": 0,
            "duration": 2.5,
        },
        {
            "translation": {"x": 0, "y": 0}, 
            "rotation": {"x": 0},
            "water": 0,
            "duration": 0.5,
        },
        {
            "translation": {"x": 0, "y": 0}, 
            "rotation": {"x": 0.5},
            "water": 0,
            "duration": 0.95,
        },
    ],
}
