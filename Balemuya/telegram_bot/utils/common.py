from datetime import datetime
import pytz
from PIL import Image, ImageDraw
import requests


def create_circular_image(image, size=(100, 100)):
    """Create a circular image from the original image."""
    img = image.resize(size, Image.LANCZOS)  # Use LANCZOS for high-quality resizing
    circle = Image.new('L', size, 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, size[0], size[1]), fill=255)

    mask = Image.new('L', size, 0)
    mask.paste(circle, (0, 0))
    img.putalpha(mask)
    
    return img