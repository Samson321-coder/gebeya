"""
watermark.py — Adds a text watermark to house listing photos.
"""
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

WATERMARK_TEXT = "@AkerayTekerayBot"

def apply_watermark(image_bytes: bytes) -> BytesIO:
    """
    Takes raw image bytes, draws a watermark in the bottom-right corner,
    and returns the result as a BytesIO object ready for Telegram upload.
    """
    img = Image.open(BytesIO(image_bytes)).convert("RGBA")
    width, height = img.size

    # Create a transparent overlay layer
    overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)

    # Try to load a font, fall back to default if not available
    font_size = max(20, width // 25)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        try:
            # Try common Linux path
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()

    # Measure text size
    bbox = draw.textbbox((0, 0), WATERMARK_TEXT, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Position: bottom-right with padding
    padding = 15
    x = width - text_width - padding
    y = height - text_height - padding

    # Draw shadow for readability
    draw.text((x + 2, y + 2), WATERMARK_TEXT, font=font, fill=(0, 0, 0, 160))
    # Draw the main text in white
    draw.text((x, y), WATERMARK_TEXT, font=font, fill=(255, 255, 255, 220))

    # Merge overlay with original
    watermarked = Image.alpha_composite(img, overlay).convert("RGB")

    output = BytesIO()
    watermarked.save(output, format="JPEG", quality=92)
    output.seek(0)
    return output
