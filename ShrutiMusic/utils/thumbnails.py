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
    return [text1,text2]

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
            title = result.get("title")
            if title:
                title = re.sub("\W+", " ", title).title()
            else:
                title = "Unsupported Title"
            duration = result.get("duration")
            if not duration:
                duration = "Live"
            thumbnail_data = result.get("thumbnails")
            if thumbnail_data:
                thumbnail = thumbnail_data[0]["url"].split("?")[0]
            else:
                thumbnail = None
            views_data = result.get("viewCount")
            if views_data:
                views = views_data.get("short")
                if not views:
                    views = "Unknown Views"
            else:
                views = "Unknown Views"
            channel_data = result.get("channel")
            if channel_data:
                channel = channel_data.get("name")
                if not channel:
                    channel = "Unknown Channel"
            else:
                channel = "Unknown Channel"

        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(f"cache/thumb{videoid}.png", mode="wb")
                    await f.write(await resp.read())
                    await f.close()

        # Base image setup
        youtube = Image.open(f"cache/thumb{videoid}.png")
        image1 = changeImageSize(1280, 720, youtube)
        
        # Create blurred background
        blurred_bg = image1.filter(filter=ImageFilter.GaussianBlur(20))
        enhancer = ImageEnhance.Brightness(blurred_bg)
        blurred_bg = enhancer.enhance(0.6)
        
        # Create gradient overlay
        color1 = random_color()
        color2 = random_color()
        gradient = generate_gradient(1280, 720, color1, color2)
        
        # Composite background
        background = Image.blend(blurred_bg, gradient, alpha=0.4)
        
        # Add noise texture for modern look
        noise = Image.new('RGBA', (1280, 720), (0,0,0,0))
        for x in range(1280):
            for y in range(720):
                if random.random() > 0.93:
                    noise.putpixel((x,y), (255,255,255,random.randint(5,25)))
        background = Image.alpha_composite(background, noise)
        
        draw = ImageDraw.Draw(background)
        
        # Font setup
        try:
            font_small = ImageFont.truetype("ShrutiMusic/assets/font2.ttf", 28)
            font_medium = ImageFont.truetype("ShrutiMusic/assets/font.ttf", 30)
            font_large = ImageFont.truetype("ShrutiMusic/assets/font3.ttf", 45)
        except:
            font_small = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_large = ImageFont.load_default()

        # Process thumbnail image
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
        
        # Add shadow
        shadow = Image.new('RGBA', thumb_with_border.size, (0,0,0,0))
        for i in range(20, 0, -1):
            offset = 20 - i
            temp = thumb_with_border.copy()
            temp = temp.filter(ImageFilter.GaussianBlur(i))
            shadow.paste(temp, (offset, offset), temp)
        
        # Position elements
        thumb_pos = (100, 160)
        background.paste(shadow, (thumb_pos[0]-10, thumb_pos[1]-10), shadow)
        background.paste(thumb_with_border, thumb_pos, thumb_with_border)
        
        # Text positioning
        text_x = 565
        text_y = 180
        
        # Title text with gradient
        title_parts = truncate(title)
        for i, part in enumerate(title_parts):
            if part:
                # Create text mask
                text_mask = Image.new('L', (600, 60), 0)
                text_draw = ImageDraw.Draw(text_mask)
                text_draw.text((0,0), part, font=font_large, fill=255)
                
                # Create gradient for text
                text_gradient = generate_gradient(600, 60, color1, color2)
                text_gradient.putalpha(text_mask)
                
                # Paste gradient text
                background.alpha_composite(text_gradient, (text_x, text_y + i*50))
        
        # Channel and views info
        info_text = f"{channel}  •  {views}"
        draw.text((text_x, text_y + 140), info_text, font=font_medium, fill=(220, 220, 220))
        
        # Progress bar
        bar_y = text_y + 200
        bar_width = 580
        bar_height = 8
        
        if duration != "Live":
            # Calculate progress (random position for demo)
            progress = random.uniform(0.1, 0.9)
            progress_width = int(bar_width * progress)
            
            # Draw progress bar background
            draw.rounded_rectangle((text_x, bar_y, text_x + bar_width, bar_y + bar_height), 
                                  radius=bar_height//2, fill=(70, 70, 70, 150))
            
            # Draw progress
            draw.rounded_rectangle((text_x, bar_y, text_x + progress_width, bar_y + bar_height), 
                                 radius=bar_height//2, fill=color1)
            
            # Draw progress knob
            knob_size = 15
            draw.ellipse((text_x + progress_width - knob_size//2, bar_y - knob_size//2 + bar_height//2,
                         text_x + progress_width + knob_size//2, bar_y + knob_size//2 + bar_height//2),
                        fill=color2, outline="white", width=2)
            
            # Time labels
            draw.text((text_x, bar_y + 25), "00:00", font=font_small, fill=(200, 200, 200))
            draw.text((text_x + bar_width - 60, bar_y + 25), duration, font=font_small, fill=(200, 200, 200))
        else:
            # Live version
            draw.rounded_rectangle((text_x, bar_y, text_x + bar_width, bar_y + bar_height), 
                                 radius=bar_height//2, fill=(255, 50, 50))
            
            # Live label
            live_bg_width = 80
            draw.rounded_rectangle((text_x + bar_width - live_bg_width, bar_y - 20, 
                                  text_x + bar_width, bar_y + bar_height + 20), 
                                 radius=10, fill=(255, 50, 50))
            draw.text((text_x + bar_width - live_bg_width + 15, bar_y - 10), 
                     "LIVE", font=font_small, fill="white")
        
        # Add music controls overlay
        try:
            controls = Image.open("ShrutiMusic/assets/play_icons.png")
            controls = controls.resize((580, 80))
            background.paste(controls, (text_x, bar_y + 70), controls)
        except:
            pass
        
        # Add subtle vignette
        vignette = Image.new('RGBA', (1280, 720), (0,0,0,0))
        draw_vig = ImageDraw.Draw(vignette)
        draw_vig.ellipse((-500, -500, 1780, 1220), fill=(0,0,0,100))
        background = Image.alpha_composite(background, vignette)
        
        # Final touches
        background = add_corners(background, 20)
        
        # Save and cleanup
        os.remove(f"cache/thumb{videoid}.png")
        output_path = f"cache/{videoid}_v4.png"
        background.save(output_path)
        
        return output_path

    except Exception as e:
        logging.error(f"Error generating thumbnail for video {videoid}: {e}")
        return None
