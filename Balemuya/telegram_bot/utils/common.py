from datetime import datetime
import pytz
from PIL import Image, ImageDraw
import requests

def format_date(date_str):
    """
    Converts the given ISO 8601 date string to a human-readable format.

    Parameters:
    - date_str (str): The ISO 8601 date string to convert.

    Returns:
    - str: Formatted date or 'N/A' if the input is None or empty.
    """
    if date_str:
        try:
            # Try parsing with milliseconds
            date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            try:
                # Fallback to parsing without milliseconds
                date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
            except ValueError:
                return 'Invalid date format'
        
        # Format the date in a user-friendly format
        return date_obj.strftime("%d %B %Y, %H:%M")  # Example: "23 May 2025, 00:00"
    return 'N/A'  # Default value if date is not available

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