import random
import logging
import os
import re
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps
from youtubesearchpython.__future__ import VideosSearch

logging.basicConfig(level=logging.INFO)

def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage

def truncate(text):
    list = text.split(" ")
    text1 = ""
    text2 = ""    
    for i in list:
        if len(text1) + len(i) < 30:        
            text1 += " " + i
        elif len(text2) + len(i) < 30:       
            text2 += " " + i

    text1 = text1.strip()
    text2 = text2.strip()     
    return [text1, text2]

def random_color():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

def generate_gradient(width, height, start_color, end_color):
    base = Image.new('RGBA', (width, height), start_color)
    top = Image.new('RGBA', (width, height), end_color)
    mask = Image.new('L', (width, height))
    mask_data = []
    for y in range(height):
        mask_data.extend([int(255 * (y / height))] * width)
    mask.putdata(mask_data)
    base.paste(top, (0, 0), mask)
    return base

def add_corners(im, rad):
    circle = Image.new('L', (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2, rad * 2), fill=255)
    alpha = Image.new('L', im.size, 255)
    w, h = im.size
    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
    im.putalpha(alpha)
    return im

async def gen_thumb(videoid: str):
    try:
        if os.path.isfile(f"cache/{videoid}_v4.png"):
            return f"cache/{videoid}_v4.png"

        url = f"https://www.youtube.com/watch?v={videoid}"
        results = VideosSearch(url, limit=1)
        for result in (await results.next())["result"]:
            try:
                title = result.get("title", "Unsupported Title")
                title = re.sub("\W+", " ", title).title()
            except:
                title = "Unsupported Title"
                
            try:
                duration = result.get("duration", "Live")
            except:
                duration = "Live"
                
            try:
                thumbnail = result.get("thumbnails", [{}])[0].get("url", "")
            except:
                thumbnail = ""
                
            try:
                views = result.get("viewCount", {}).get("short", "Unknown Views")
            except:
                views = "Unknown Views"
                
            try:
                channel = result.get("channel", {}).get("name", "Unknown Channel")
            except:
                channel = "Unknown Channel"

        if not thumbnail:
            logging.error("No thumbnail URL found")
            return None

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(thumbnail) as resp:
                    if resp.status == 200:
                        f = await aiofiles.open(f"cache/thumb{videoid}.png", mode="wb")
                        await f.write(await resp.read())
                        await f.close()
                    else:
                        logging.error(f"Failed to download thumbnail: HTTP {resp.status}")
                        return None
            except Exception as e:
                logging.error(f"Error downloading thumbnail: {str(e)}")
                return None

        try:
            youtube = Image.open(f"cache/thumb{videoid}.png")
            image1 = changeImageSize(1280, 720, youtube)
        except Exception as e:
            logging.error(f"Error processing image: {str(e)}")
            return None

        # Create blurred background
        try:
            blurred_bg = image1.filter(filter=ImageFilter.GaussianBlur(20))
            enhancer = ImageEnhance.Brightness(blurred_bg)
            blurred_bg = enhancer.enhance(0.6)
        except Exception as e:
            logging.error(f"Error creating background: {str(e)}")
            return None

        # Create gradient overlay
        try:
            color1 = random_color()
            color2 = random_color()
            gradient = generate_gradient(1280, 720, color1, color2)
            background = Image.blend(blurred_bg, gradient, alpha=0.4)
        except Exception as e:
            logging.error(f"Error creating gradient: {str(e)}")
            return None

        draw = ImageDraw.Draw(background)
        
        # Font setup with fallbacks
        try:
            font_small = ImageFont.truetype("ShrutiMusic/assets/font2.ttf", 28)
        except:
            font_small = ImageFont.load_default()
            
        try:
            font_medium = ImageFont.truetype("ShrutiMusic/assets/font.ttf", 30)
        except:
            font_medium = ImageFont.load_default()
            
        try:
            font_large = ImageFont.truetype("ShrutiMusic/assets/font3.ttf", 45)
        except:
            font_large = ImageFont.load_default()

        # Process thumbnail image
        try:
            thumb_size = 400
            thumb = image1.copy()
            thumb = thumb.resize((thumb_size, thumb_size))
            
            # Create circular mask
            mask = Image.new('L', (thumb_size, thumb_size), 0)
            draw_mask = ImageDraw.Draw(mask)
            draw_mask.ellipse((0, 0, thumb_size, thumb_size), fill=255)
            
            # Add border to thumbnail
            border_size = 15
            border_color = color1
            thumb_with_border = Image.new('RGBA', (thumb_size + border_size*2, thumb_size + border_size*2), (0,0,0,0))
            thumb_with_border.paste(thumb, (border_size, border_size), mask)
            
            # Draw outer circle
            draw_border = ImageDraw.Draw(thumb_with_border)
            draw_border.ellipse([(0,0), (thumb_size + border_size*2, thumb_size + border_size*2)], 
                              outline=border_color, width=border_size)
            
            # Position elements
            thumb_pos = (100, 160)
            background.paste(thumb_with_border, thumb_pos, thumb_with_border)
        except Exception as e:
            logging.error(f"Error processing thumbnail: {str(e)}")
            return None

        # Text positioning
        text_x = 565
        text_y = 180
        
        # Title text
        try:
            title_parts = truncate(title)
            for i, part in enumerate(title_parts):
                if part:
                    draw.text((text_x, text_y + i*50), part, font=font_large, fill="white")
        except Exception as e:
            logging.error(f"Error drawing title: {str(e)}")

        # Channel and views info
        try:
            info_text = f"{channel}  •  {views}"
            draw.text((text_x, text_y + 140), info_text, font=font_medium, fill=(220, 220, 220))
        except Exception as e:
            logging.error(f"Error drawing info text: {str(e)}")

        # Progress bar
        try:
            bar_y = text_y + 200
            bar_width = 580
            bar_height = 8
            
            if duration != "Live":
                progress = random.uniform(0.1, 0.9)
                progress_width = int(bar_width * progress)
                
                # Draw progress bar background
                draw.rectangle((text_x, bar_y, text_x + bar_width, bar_y + bar_height), 
                              fill=(70, 70, 70, 150))
                
                # Draw progress
                draw.rectangle((text_x, bar_y, text_x + progress_width, bar_y + bar_height), 
                             fill=color1)
                
                # Time labels
                draw.text((text_x, bar_y + 25), "00:00", font=font_small, fill=(200, 200, 200))
                draw.text((text_x + bar_width - 60, bar_y + 25), duration, font=font_small, fill=(200, 200, 200))
            else:
                # Live version
                draw.rectangle((text_x, bar_y, text_x + bar_width, bar_y + bar_height), 
                             fill=(255, 50, 50))
                
                # Live label
                live_bg_width = 80
                draw.rectangle((text_x + bar_width - live_bg_width, bar_y - 20, 
                              text_x + bar_width, bar_y + bar_height + 20), 
                             fill=(255, 50, 50))
                draw.text((text_x + bar_width - live_bg_width + 15, bar_y - 10), 
                         "LIVE", font=font_small, fill="white")
        except Exception as e:
            logging.error(f"Error drawing progress bar: {str(e)}")

        # Add music controls overlay
        try:
            controls = Image.open("ShrutiMusic/assets/play_icons.png")
            controls = controls.resize((580, 80))
            background.paste(controls, (text_x, bar_y + 70), controls)
        except Exception as e:
            logging.error(f"Error adding controls: {str(e)}")

        # Save and cleanup
        try:
            os.remove(f"cache/thumb{videoid}.png")
            output_path = f"cache/{videoid}_v4.png"
            background.save(output_path)
            return output_path
        except Exception as e:
            logging.error(f"Error saving thumbnail: {str(e)}")
            return None

    except Exception as e:
        logging.error(f"Error generating thumbnail: {str(e)}")
        return None
