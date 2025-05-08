import json

def generate_keyboard(options):
    return json.dumps({
        "keyboard": options,
        "resize_keyboard": True,
        "one_time_keyboard": True
    })