import asyncio
import logging
import os
import re
import aiofiles
import aiohttp
import random
import traceback
from io import BytesIO
from datetime import datetime
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps
from youtubesearchpython.__future__ import VideosSearch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ThumbnailGenerator")

# Constants for thumbnail design
THUMBNAIL_SIZE = (1280, 720)
CACHE_DIR = "cache"
ASSETS_DIR = "ShrutiMusic/assets"

FONTS = {
    "title": os.path.join(ASSETS_DIR, "font3.ttf"),
    "artist": os.path.join(ASSETS_DIR, "font2.ttf"),
    "info": os.path.join(ASSETS_DIR, "font.ttf")
}

# Modern theme colors - Elegant dark theme with accent colors
THEMES = [
    {
        "name": "Midnight Blue",
        "background": (10, 15, 30, 180),
        "accent": (65, 105, 225),
        "text": (255, 255, 255),
        "gradient": [(10, 15, 30), (20, 40, 80)]
    },
    {
        "name": "Deep Purple",
        "background": (25, 10, 40, 180),
        "accent": (147, 112, 219),
        "text": (255, 255, 255),
        "gradient": [(25, 10, 40), (75, 30, 100)]
    },
    {
        "name": "Crimson",
        "background": (40, 10, 20, 180),
        "accent": (220, 53, 69),
        "text": (255, 255, 255),
        "gradient": [(40, 10, 20), (100, 30, 40)]
    },
    {
        "name": "Emerald",
        "background": (10, 40, 30, 180),
        "accent": (46, 204, 113),
        "text": (255, 255, 255),
        "gradient": [(10, 40, 30), (20, 80, 60)]
    },
    {
        "name": "Amber",
        "background": (40, 30, 10, 180),
        "accent": (255, 193, 7),
        "text": (255, 255, 255),
        "gradient": [(40, 30, 10), (80, 60, 20)]
    }
]

# Ensure cache directory exists
os.makedirs(CACHE_DIR, exist_ok=True)

def truncate_text(text, max_length=30, lines=2):
    """Split text into lines with maximum length per line."""
    words = text.split(" ")
    result = [""]
    
    for word in words:
        if len(result[-1]) + len(word) + 1 <= max_length:
            if result[-1]:
                result[-1] += " " + word
            else:
                result[-1] = word
        elif len(result) < lines:
            result.append(word)
        else:
            # If we've reached the maximum number of lines, add ellipsis to the last line
            if not result[-1].endswith("..."):
                result[-1] = result[-1][:max_length-3] + "..."
            break
    
    # Ensure we only return the requested number of lines
    return result[:lines]

def apply_glass_effect(image, blur=15, opacity=0.8):
    """Apply a translucent glass effect to an image."""
    # Blur the image
    blurred = image.filter(ImageFilter.GaussianBlur(blur))
    
    # Reduce brightness
    enhancer = ImageEnhance.Brightness(blurred)
    darkened = enhancer.enhance(0.7)
    
    # Convert to RGBA if not already
    if darkened.mode != 'RGBA':
        darkened = darkened.convert('RGBA')
    
    # Adjust opacity
    data = darkened.getdata()
    new_data = []
    for item in data:
        # Change all non-fully transparent pixels
        if item[3] > 0:
            new_data.append((item[0], item[1], item[2], int(item[3] * opacity)))
        else:
            new_data.append(item)
    
    darkened.putdata(new_data)
    return darkened

def generate_gradient(width, height, start_color, end_color, direction="vertical"):
    """Generate a gradient image."""
    base = Image.new('RGBA', (width, height), start_color)
    top = Image.new('RGBA', (width, height), end_color)
    mask = Image.new('L', (width, height))
    mask_data = []
    
    if direction == "vertical":
        for y in range(height):
            mask_data.extend([int(255 * (y / height))] * width)
    elif direction == "horizontal":
        for y in range(height):
            for x in range(width):
                mask_data.append(int(255 * (x / width)))
    elif direction == "radial":
        center_x, center_y = width // 2, height // 2
        max_distance = ((width//2)**2 + (height//2)**2)**0.5
        for y in range(height):
            for x in range(width):
                distance = ((x - center_x)**2 + (y - center_y)**2)**0.5
                mask_data.append(int(255 * (distance / max_distance)))
    
    mask.putdata(mask_data)
    base.paste(top, (0, 0), mask)
    return base

def create_rounded_rectangle(width, height, radius, color):
    """Create a rounded rectangle mask."""
    rectangle = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(rectangle)
    
    # Draw four corners and connecting rectangles
    draw.rounded_rectangle([(0, 0), (width, height)], radius, fill=color)
    return rectangle

def create_circular_mask(size, offset=0, blur_radius=0):
    """Create a circular mask."""
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((offset, offset, size[0]-offset, size[1]-offset), fill=255)
    
    if blur_radius > 0:
        mask = mask.filter(ImageFilter.GaussianBlur(blur_radius))
    
    return mask

def apply_text_with_shadow(img, text, position, font, fill, shadow_color=(0, 0, 0), shadow_offset=(2, 2)):
    """Draw text with a drop shadow effect."""
    draw = ImageDraw.Draw(img)
    
    # Draw shadow
    draw.text((position[0] + shadow_offset[0], position[1] + shadow_offset[1]), text, font=font, fill=shadow_color)
    
    # Draw text
    draw.text(position, text, font=font, fill=fill)
    
    return img

def draw_progress_bar(img, x, y, width, height, progress, accent_color, bg_color=(255, 255, 255, 80)):
    """Draw a progress bar with given dimensions and colors."""
    draw = ImageDraw.Draw(img, 'RGBA')
    
    # Draw background bar
    draw.rounded_rectangle([(x, y), (x + width, y + height)], height // 2, fill=bg_color)
    
    # Calculate progress width
    progress_width = int(width * progress)
    
    # Draw progress bar if there's any progress
    if progress_width > 0:
        # Ensure progress bar has at least rounded ends
        radius = min(height // 2, progress_width)
        draw.rounded_rectangle([(x, y), (x + progress_width, y + height)], radius, fill=accent_color)
    
    return img

def format_duration(seconds):
    """Format seconds to MM:SS format."""
    if seconds == "Live":
        return "LIVE"
    
    try:
        # Convert duration string (MM:SS) to seconds for calculation
        if ':' in seconds:
            parts = seconds.split(':')
            if len(parts) == 2:  # MM:SS
                mins, secs = map(int, parts)
                seconds = mins * 60 + secs
            elif len(parts) == 3:  # HH:MM:SS
                hours, mins, secs = map(int, parts)
                seconds = hours * 3600 + mins * 60 + secs
        else:
            seconds = int(seconds)
        
        minutes, seconds = divmod(seconds, 60)
        return f"{minutes:02}:{seconds:02}"
    except (ValueError, TypeError):
        return "00:00"

def create_glowing_circle(size, color, glow_size=20):
    """Create a circle with a glowing effect."""
    # Create base circle image with transparent background
    base_size = size + glow_size * 2
    circle_img = Image.new('RGBA', (base_size, base_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(circle_img)
    
    # Draw the main circle
    draw.ellipse((glow_size, glow_size, base_size - glow_size, base_size - glow_size), fill=color)
    
    # Apply blur for the glow effect
    circle_img = circle_img.filter(ImageFilter.GaussianBlur(glow_size // 2))
    
    # Draw a sharper circle in the center
    draw = ImageDraw.Draw(circle_img)
    draw.ellipse((glow_size, glow_size, base_size - glow_size, base_size - glow_size), fill=color)
    
    return circle_img

def add_reflection(image, reflection_height=100, opacity=0.3):
    """Add a reflection effect below the image."""
    width, height = image.size
    
    # Create a flipped copy of the image for reflection
    reflection = image.crop((0, height - reflection_height, width, height)).transpose(Image.FLIP_TOP_BOTTOM)
    
    # Create a gradient mask for the reflection (transparent at the bottom)
    mask = Image.new('L', (width, reflection_height))
    mask_data = []
    for y in range(reflection_height):
        # The further down we go, the more transparent it gets
        mask_data.extend([int(255 * (1 - y / reflection_height * opacity))] * width)
    mask.putdata(mask_data)
    
    # Apply the mask to the reflection
    reflection.putalpha(mask)
    
    # Create a new image with space for the reflection
    result = Image.new('RGBA', (width, height + reflection_height), (0, 0, 0, 0))
    result.paste(image, (0, 0))
    result.paste(reflection, (0, height), reflection)
    
    return result

async def fetch_image(url, session):
    """Fetch an image from a URL using aiohttp."""
    try:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.read()
                return Image.open(BytesIO(data))
            else:
                logger.error(f"Failed to fetch image: {response.status}")
                return None
    except Exception as e:
        logger.error(f"Error fetching image: {e}")
        return None

async def get_video_info(videoid):
    """Get video information from YouTube."""
    url = f"https://www.youtube.com/watch?v={videoid}"
    results = VideosSearch(url, limit=1)
    video_results = await results.next()
    
    if not video_results.get("result"):
        logger.error(f"No results found for video ID: {videoid}")
        return None
    
    result = video_results["result"][0]
    
    # Extract and clean title
    title = result.get("title", "Unknown Title")
    title = re.sub(r"\W+", " ", title).title()
    
    # Extract other metadata
    duration = result.get("duration", "00:00")
    thumbnail_url = None
    if result.get("thumbnails"):
        thumbnail_url = result["thumbnails"][0]["url"].split("?")[0]
    
    channel = "Unknown Artist"
    if result.get("channel"):
        channel = result["channel"].get("name", "Unknown Artist")
    
    views = "No views"
    if result.get("viewCount"):
        views = result["viewCount"].get("short", "No views")
    
    # Get publication date for calculating if it's a new release
    publish_time = result.get("publishedTime", "")
    is_new = False
    if publish_time and "day" in publish_time and "month" not in publish_time:
        # If published days ago (not months or years), mark as new
        try:
            days = int(re.search(r"(\d+)", publish_time).group(1))
            is_new = days <= 30  # New if less than a month old
        except (AttributeError, ValueError):
            pass
    
    return {
        "title": title,
        "duration": duration,
        "thumbnail_url": thumbnail_url,
        "channel": channel,
        "views": views,
        "is_new": is_new
    }

async def create_modern_thumbnail(video_info, output_path, theme=None):
    """Create a modern thumbnail with glass morphism effect."""
    if not theme:
        theme = random.choice(THEMES)
    
    # Create a blank canvas with the right dimensions
    thumbnail = Image.new('RGBA', THUMBNAIL_SIZE, (0, 0, 0, 0))
    
    # Generate a gradient background
    gradient = generate_gradient(
        THUMBNAIL_SIZE[0], 
        THUMBNAIL_SIZE[1], 
        theme["gradient"][0], 
        theme["gradient"][1], 
        direction="radial"
    )
    thumbnail.paste(gradient, (0, 0))
    
    # Load and resize the YouTube thumbnail
    async with aiohttp.ClientSession() as session:
        yt_thumb = await fetch_image(video_info["thumbnail_url"], session)
        
        if yt_thumb:
            # Resize to fill the background
            yt_thumb = yt_thumb.resize(
                (THUMBNAIL_SIZE[0], int(yt_thumb.height * THUMBNAIL_SIZE[0] / yt_thumb.width)),
                Image.LANCZOS
            )
            
            # Center crop if needed
            if yt_thumb.height > THUMBNAIL_SIZE[1]:
                top = (yt_thumb.height - THUMBNAIL_SIZE[1]) // 2
                yt_thumb = yt_thumb.crop((0, top, THUMBNAIL_SIZE[0], top + THUMBNAIL_SIZE[1]))
            
            # Apply blur and overlay
            yt_thumb = apply_glass_effect(yt_thumb, blur=8, opacity=0.6)
            thumbnail.paste(yt_thumb, (0, 0), yt_thumb)
    
    # Add a semi-transparent overlay
    overlay = Image.new('RGBA', THUMBNAIL_SIZE, theme["background"])
    thumbnail = Image.alpha_composite(thumbnail, overlay)
    
    # Create a circular album art from the YouTube thumbnail
    if yt_thumb:
        # Get the center portion of the YouTube thumbnail for the album art
        album_size = 320
        album_art = yt_thumb.copy()
        
        # Try to focus on the center part of the image
        width, height = album_art.size
        left = (width - min(width, height)) // 2
        top = (height - min(width, height)) // 2
        right = left + min(width, height)
        bottom = top + min(width, height)
        album_art = album_art.crop((left, top, right, bottom))
        
        # Resize to our target album size
        album_art = album_art.resize((album_size, album_size), Image.LANCZOS)
        
        # Create a circular mask
        mask = create_circular_mask((album_size, album_size))
        
        # Apply the mask
        album_art.putalpha(mask)
        
        # Add a glowing accent around the album art
        glow = create_glowing_circle(album_size, theme["accent"], glow_size=15)
        
        # Position the album art and glow
        album_pos = (120, 200)  # Positioned on the left side
        thumbnail.paste(glow, (album_pos[0] - 15, album_pos[1] - 15), glow)
        thumbnail.paste(album_art, album_pos, album_art)
    
    # Load fonts
    try:
        title_font = ImageFont.truetype(FONTS["title"], 42)
        subtitle_font = ImageFont.truetype(FONTS["artist"], 32)
        info_font = ImageFont.truetype(FONTS["info"], 28)
    except Exception as e:
        logger.error(f"Error loading fonts: {e}")
        # Fall back to default font
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        info_font = ImageFont.load_default()
    
    # Calculate text positions - positioned to the right of the album art
    text_x = 480
    title_y = 200
    artist_y = 300
    info_y = 350
    
    # Create a content panel with glass effect
    panel_width = 700
    panel_height = 320
    panel_x = text_x - 40
    panel_y = title_y - 40
    
    panel = create_rounded_rectangle(panel_width, panel_height, 20, (*theme["background"][:3], 150))
    thumbnail.paste(panel, (panel_x, panel_y), panel)
    
    # Draw title text
    draw = ImageDraw.Draw(thumbnail)
    
    # Split title into two lines if needed
    title_lines = truncate_text(video_info["title"], max_length=35, lines=2)
    
    for i, line in enumerate(title_lines):
        apply_text_with_shadow(
            thumbnail, 
            line,
            (text_x, title_y + i * 50),
            title_font,
            theme["text"]
        )
    
    # Draw artist/channel name
    apply_text_with_shadow(
        thumbnail,
        f"Artist: {video_info['channel']}",
        (text_x, artist_y),
        subtitle_font,
        theme["text"]
    )
    
    # Draw views info
    apply_text_with_shadow(
        thumbnail,
        f"Views: {video_info['views']}",
        (text_x, info_y),
        info_font,
        theme["text"]
    )
    
    # Add "NEW" badge if it's a new release
    if video_info.get("is_new"):
        badge_width = 80
        badge_height = 30
        badge = create_rounded_rectangle(badge_width, badge_height, 15, theme["accent"])
        badge_pos = (text_x + 300, title_y - 20)
        thumbnail.paste(badge, badge_pos, badge)
        
        # Add "NEW" text to badge
        apply_text_with_shadow(
            thumbnail,
            "NEW",
            (badge_pos[0] + 20, badge_pos[1] + 5),
            info_font,
            theme["text"]
        )
    
    # Add the current date/time
    now = datetime.now().strftime("%d-%m-%Y")
    apply_text_with_shadow(
        thumbnail,
        now,
        (THUMBNAIL_SIZE[0] - 150, THUMBNAIL_SIZE[1] - 40),
        info_font,
        theme["text"]
    )
    
    # Progress bar section
    progress_y = panel_y + panel_height + 20
    progress_width = 700
    progress_height = 10
    
    # Add a semi-transparent panel for the player controls
    player_panel = create_rounded_rectangle(progress_width + 80, 120, 20, (*theme["background"][:3], 150))
    thumbnail.paste(player_panel, (panel_x, progress_y - 30), player_panel)
    
    # Position for progress timer texts
    current_time_pos = (panel_x + 10, progress_y + 30)
    total_time_pos = (panel_x + progress_width + 30, progress_y + 30)
    
    # Draw the progress bar (random position for thumbnail)
    if video_info["duration"] == "Live":
        # For live streams, show a pulsing red bar
        progress_percent = 1.0
        draw_progress_bar(
            thumbnail, 
            panel_x + 10, 
            progress_y, 
            progress_width, 
            progress_height, 
            progress_percent, 
            (255, 0, 0, 255)
        )
        
        # Show LIVE text
        apply_text_with_shadow(
            thumbnail,
            "LIVE",
            current_time_pos,
            info_font,
            (255, 0, 0)
        )
    else:
        # Random progress for the thumbnail
        progress_percent = random.uniform(0.1, 0.9)
        draw_progress_bar(
            thumbnail, 
            panel_x + 10, 
            progress_y, 
            progress_width, 
            progress_height, 
            progress_percent, 
            theme["accent"]
        )
        
        # Calculate and display time values
        try:
            duration_seconds = sum(int(x) * 60 ** i for i, x in enumerate(reversed(video_info["duration"].split(":"))))
            current_seconds = int(duration_seconds * progress_percent)
            
            current_time = format_duration(current_seconds)
            total_time = format_duration(video_info["duration"])
            
            apply_text_with_shadow(
                thumbnail,
                current_time,
                current_time_pos,
                info_font,
                theme["text"]
            )
            
            apply_text_with_shadow(
                thumbnail,
                total_time,
                total_time_pos,
                info_font,
                theme["text"]
            )
        except Exception as e:
            logger.error(f"Error calculating time: {e}")
    
    # Add player control icons
    icon_y = progress_y + 60
    icon_spacing = 70
    
    # Play button in the center
    play_button_pos = (panel_x + (progress_width // 2), icon_y)
    play_button_size = 40
    
    draw.ellipse(
        (
            play_button_pos[0] - play_button_size // 2,
            play_button_pos[1] - play_button_size // 2,
            play_button_pos[0] + play_button_size // 2,
            play_button_pos[1] + play_button_size // 2
        ),
        fill=theme["accent"]
    )
    
    # Draw play triangle
    play_icon_size = play_button_size // 2
    draw.polygon(
        [
            (play_button_pos[0] - play_icon_size // 3, play_button_pos[1] - play_icon_size // 2),
            (play_button_pos[0] - play_icon_size // 3, play_button_pos[1] + play_icon_size // 2),
            (play_button_pos[0] + play_icon_size // 2, play_button_pos[1])
        ],
        fill=theme["text"]
    )
    
    # Previous and next buttons
    for offset, is_next in [(-icon_spacing * 2, False), (icon_spacing * 2, True)]:
        button_pos = (play_button_pos[0] + offset, icon_y)
        button_size = 30
        
        draw.ellipse(
            (
                button_pos[0] - button_size // 2,
                button_pos[1] - button_size // 2,
                button_pos[0] + button_size // 2,
                button_pos[1] + button_size // 2
            ),
            fill=(*theme["accent"][:3], 180)
        )
        
        # Draw previous/next icons
        arrow_size = button_size // 2
        if is_next:
            # Next button (right-pointing triangle)
            draw.polygon(
                [
                    (button_pos[0] - arrow_size // 3, button_pos[1] - arrow_size // 2),
                    (button_pos[0] - arrow_size // 3, button_pos[1] + arrow_size // 2),
                    (button_pos[0] + arrow_size // 2, button_pos[1])
                ],
                fill=theme["text"]
            )
        else:
            # Previous button (left-pointing triangle)
            draw.polygon(
                [
                    (button_pos[0] + arrow_size // 3, button_pos[1] - arrow_size // 2),
                    (button_pos[0] + arrow_size // 3, button_pos[1] + arrow_size // 2),
                    (button_pos[0] - arrow_size // 2, button_pos[1])
                ],
                fill=theme["text"]
            )
    
    # Simple volume control
    for i in range(3):
        x_pos = play_button_pos[0] + icon_spacing * 3 + i * 15
        y_pos = icon_y
        height = 10 + i * 5
        
        draw.rounded_rectangle(
            [(x_pos, y_pos - height // 2), (x_pos + 5, y_pos + height // 2)],
            2,
            fill=(*theme["accent"][:3], 180)
        )
    
    # Add a subtle watermark
    apply_text_with_shadow(
        thumbnail,
        "Music Bot",
        (20, THUMBNAIL_SIZE[1] - 40),
        info_font,
        (*theme["text"][:3], 150)
    )
    
    # Save the thumbnail
    thumbnail.save(output_path, "PNG")
    return output_path

async def gen_thumb(videoid: str):
    """Generate a thumbnail for a video."""
    try:
        # Check if thumbnail already exists in cache
        cache_path = f"{CACHE_DIR}/{videoid}_v5.png"
        if os.path.isfile(cache_path):
            return cache_path
        
        # Get video information
        video_info = await get_video_info(videoid)
        if not video_info:
            logger.error(f"Could not retrieve video info for {videoid}")
            return None
        
        # Choose a random theme
        theme = random.choice(THEMES)
        
        # Create the thumbnail
        result = await create_modern_thumbnail(video_info, cache_path, theme)
        return result
    
    except Exception as e:
        logger.error(f"Error generating thumbnail: {e}")
        traceback.print_exc()
        return None

# For testing outside of async context
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        video_id = sys.argv[1]
        print(f"Generating thumbnail for video ID: {video_id}")
        result = asyncio.run(gen_thumb(video_id))
        print(f"Thumbnail generated: {result}")
    else:
        print("Please provide a YouTube video ID as an argument")
