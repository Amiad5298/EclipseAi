import os
import uuid
import logging
from PIL import Image
import requests

logger = logging.getLogger(__name__)

class ImageSaver:
    """
    Responsible for saving images retrieved from a given URL to the specified output directory.
    """

    def __init__(self, output_dir: str = "output_images") -> None:
        """
        Initialize the ImageSaver with a given output directory.

        Args:
            output_dir (str): The directory where images should be saved. Defaults to "output_images".
        """
        self.output_dir = output_dir
        self._ensure_output_directory_exists()

    def _ensure_output_directory_exists(self) -> None:
        """
        Ensure that the output directory exists. If not, create it.
        """
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            logger.debug(f"Created output directory: {self.output_dir}")
        else:
            logger.debug(f"Output directory already exists: {self.output_dir}")

    def save_image(self, image_url: str, name: str, last_name: str) -> str:
        """
        Download an image from the provided URL, then save it to the output directory with a unique filename.

        Args:
            image_url (str): The URL of the image to download.
            name (str): The first name to include in the saved image file name.
            last_name (str): The last name to include in the saved image file name.

        Returns:
            str: The full path to the saved image.

        Raises:
            ValueError: If there is an error downloading or saving the image.
        """
        unique_id = str(uuid.uuid4())
        image_name = f"{name}_{last_name}_{unique_id}.png"
        image_path = os.path.join(self.output_dir, image_name)

        logger.debug(f"Attempting to save image from URL: {image_url}")
        logger.debug(f"Generated image file name: {image_name}")

        try:
            response = requests.get(image_url, stream=True)
            response.raise_for_status()  # Ensure we catch any non-200 responses

            # Open the image using PIL
            image = Image.open(response.raw)
            image.save(image_path)
            logger.info(f"Saved image to: {image_path}")
            return image_path
        except Exception as e:
            logger.exception(f"Error saving image from {image_url} to {image_path}")
            raise ValueError(f"Error saving image: {e}") from e
