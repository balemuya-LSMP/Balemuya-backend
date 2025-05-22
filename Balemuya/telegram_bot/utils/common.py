from datetime import datetime
import pytz
from PIL import Image, ImageDraw
import requests

def create_circular_image(image_path, output_path):
    """Create a circular image from the original image."""
    img = Image.open(image_path)
    img = img.resize((100, 100))  # Resize to desired size
    
    # Create a new image with a transparent background
    circle = Image.new('L', (100, 100), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, 100, 100), fill=255)
    
    # Create a mask
    mask = Image.new('L', (100, 100), 0)
    mask.paste(circle, (0, 0))

    # Apply the mask to the image
    img.putalpha(mask)

    # Save the circular image
    img.save(output_path)
