# Function to encode a message into an image
def encode_image(input_image_path, output_image_path, message):
    img = Image.open(input_image_path)
    width, height = img.size
    pixel_index = 0
    binary_message = ''.join(format(ord(char), '08b') for char in message)

    if len(binary_message) > width * height:
        print("Message is too large for this image.")
        return

    for x in range(width):
        for y in range(height):
            pixel = list(img.getpixel((x, y)))
            for color_channel in range(3):  # RGB channels
                if pixel_index < len(binary_message):
                    pixel[color_channel] = int(bin(pixel[color_channel])[2:-1] + binary_message[pixel_index], 2)
                    pixel_index += 1
                else:
                    break
            img.putpixel((x, y), tuple(pixel))

    img.save(output_image_path)


# Example usage
message_to_hide = "This example of Stenography."
input_image = "madmax.jpg"
output_image = "output_image.png"

# Encode the message into the image
encode_image(input_image, output_image, message_to_hide)
print("Encoded Message: ",message_to_hide)
