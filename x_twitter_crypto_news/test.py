import base64
from PIL import Image
from io import BytesIO
import json

# Path to the JSON file
json_file_path = r'C:\Users\User\Documents\financialDashboard_AUG\financialDashboard\afdashboard\x_twitter_crypto_news\accounts_binance.json'

# Load the JSON data
with open(json_file_path, 'r') as file:
    data = json.load(file)

# Extract the base64 image string
image_base64 = data.get("image_base64")

# Decode the base64 string
image_data = base64.b64decode(image_base64)

# Convert to an image
image = Image.open(BytesIO(image_data))

# Display the image
image.show()

# Optionally, save the image to a file
image.save('decoded_image.jpg')
