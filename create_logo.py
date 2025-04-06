from PIL import Image, ImageDraw, ImageFont

# Constants
canvas_width, canvas_height = 600, 200
pixel_size = 10
pink = (255, 0, 144)
spacing_between_logo_and_text = 20

# Step 1: Create base canvas
base_img = Image.new("RGB", (canvas_width, canvas_height), (0, 0, 0))
draw = ImageDraw.Draw(base_img)

# Step 2: Draw pixel logo (8-bit drop/heart-like shape)
heart_pixels = [
    (2, 0), (3, 0), (6, 0), (7, 0),
    (1, 1), (4, 1), (5, 1), (8, 1),
    (0, 2), (3, 2), (6, 2), (9, 2),
    (1, 3), (4, 3), (5, 3), (8, 3),
    (2, 4), (3, 4), (6, 4), (7, 4),
    (3, 5), (6, 5),
    (4, 6), (5, 6)
]

# Get logo bounding box
logo_width = (max(x for x, y in heart_pixels) + 1) * pixel_size
logo_height = (max(y for x, y in heart_pixels) + 1) * pixel_size
logo_x = 50
logo_y = (canvas_height - logo_height) // 2

# Draw the logo
for x, y in heart_pixels:
    draw.rectangle(
        [
            logo_x + x * pixel_size,
            logo_y + y * pixel_size,
            logo_x + (x + 1) * pixel_size - 1,
            logo_y + (y + 1) * pixel_size - 1
        ],
        fill=pink
    )

# Step 3: Draw pixelated text using default font, then upscale
text = "OffCaramel"
font = ImageFont.load_default()

# Render small text
small_text_img = Image.new("RGB", (200, 50), (0, 0, 0))
small_draw = ImageDraw.Draw(small_text_img)
small_draw.text((0, 0), text, font=font, fill=pink)

# Pixelate by upscaling
scale_factor = 4
text_img = small_text_img.resize(
    (small_text_img.width * scale_factor, small_text_img.height * scale_factor),
    resample=Image.NEAREST
)

# Center text vertically to match logo
text_x = logo_x + logo_width + spacing_between_logo_and_text
text_y = (canvas_height - text_img.height) // 2

# Paste the text image onto the base image
base_img.paste(text_img, (text_x, text_y))

# Save result
base_img.save("aligned_pixel_logo.png")
print("Saved as aligned_pixel_logo.png")