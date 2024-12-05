import os
import uuid
from PIL import Image
import requests

class ImageSaver:
    def __init__(self, output_dir="output_images"):
        self.output_dir = output_dir
        self.ensure_output_directory_exists()

    def ensure_output_directory_exists(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def save_image(self, image_url, name, last_name):
        try:
            image = Image.open(requests.get(image_url, stream=True).raw)
            unique_id = str(uuid.uuid4())
            image_name = f"{name}_{last_name}_{unique_id}.png"
            image_path = os.path.join(self.output_dir, image_name)
            image.save(image_path)
            return image_path
        except Exception as e:
            raise ValueError(f"Error saving image: {e}")
