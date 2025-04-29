import json

def generate_keyboard(options):
    """
    Generates a custom keyboard layout for Telegram bot options
    """
    return json.dumps({
        "keyboard": options,
        "resize_keyboard": True,
        "one_time_keyboard": True
    })

def validate_email(email):
    """
    Basic email validation
    """
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError

    try:
        validate_email(email)
        return True
    except ValidationError:
        return False
