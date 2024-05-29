from pathlib import Path
from collections import defaultdict
import logging
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

def visualize(args, timecrawler):

    N = len(timecrawler)

    images = []
    for i, day in enumerate(timecrawler):
        
        img = Image.new('RGB', (64, 64), color = (255, 255, 255))

        if "get_files" in day.channels:
            try:
                img_path = day.channels["get_files"].json()["files"][0]
                _img = Image.open(img_path)
                img.paste(_img, (0, 0))
            except Exception as e: 
                logging.error(f"Error loading image: {e}")
            

        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()

        text = f"{day.timestamp}"
        draw.text((0, 0), text, (0,0,0), font=font)

        if "death" in day.channels:
            death_data = day.channels["death"].json()["data"]
            text = death_data["name"] 
            draw.text((0, 16), text, (0,0,0), font=font)
            print(death_data)

            
            files = day.channels["death"].json()["files"]
            if len(files) > 0:
                img_path = files[0]
                _img = Image.open(img_path)
                _img.thumbnail((64, 64))
                img.paste(_img, (0, 32))

        images.append(img)

    # Compositie images in a grid with 7 Columns
    width = 64 * 7
    height = 64 * (N // 7 + 1)
    collage = Image.new('RGB', (width, height), color = (0, 0, 0))
    for i, img in enumerate(images):
        x = 64 * (i % 7)
        y = 64 * (i // 7)
        collage.paste(img, (x, y))

    collage.save("collage.png")