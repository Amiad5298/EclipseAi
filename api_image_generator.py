import logging
import json
from typing import Dict
import requests

logger = logging.getLogger(__name__)

class ApiImageGenerator:
    """
    A class responsible for generating background images using the OpenAI Image Generation API.
    """

    def __init__(self, api_key: str) -> None:
        """
        Initialize the ApiImageGenerator with a given OpenAI API key.

        Args:
            api_key (str): The OpenAI API key.
        """
        self.api_key = api_key
        self.api_url = "https://api.openai.com/v1/images/generations"

    def generate_prompt(self, name: str, job_title: str, hobby: str, favorite_food: str) -> str:
        """
        Generate a prompt string based on the provided user attributes.

        Args:
            name (str): The person's name.
            job_title (str): The person's job title or profession.
            hobby (str): The person's hobby.
            favorite_food (str): The person's favorite food.

        Returns:
            str: A descriptive prompt for image generation.
        """
        prompt = (
            f"Create a vivid background image inspired by {name}'s profession as a {job_title}, "
            f"who loves {hobby} and their favorite food is {favorite_food}."
        )
        logger.debug(f"Generated prompt: {prompt}")
        return prompt

    def create_background_image(self, prompt: str) -> str:
        """
        Use the OpenAI Image Generation API to create a background image from a given prompt.

        Args:
            prompt (str): The prompt describing the desired image.

        Returns:
            str: The URL of the generated image.

        Raises:
            ValueError: If there is an error during the API request or response parsing.
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        # Update the data payload to remove the "model" parameter if it's not supported by the API.
        data: Dict[str, Any] = {
            "prompt": prompt,
            "n": 1,
            "size": "1024x1024",
        }

        logger.debug(f"Making request to OpenAI API at {self.api_url} with prompt: {prompt}")
        try:
            response = requests.post(self.api_url, headers=headers, data=json.dumps(data))
            response.raise_for_status()
            result = response.json()

            if "data" not in result or not result["data"]:
                logger.error(f"Unexpected API response structure: {result}")
                raise ValueError("Unexpected API response structure: no 'data' field or empty 'data' array.")

            image_url = result['data'][0].get('url')
            if not image_url:
                logger.error(f"No URL found in API response: {result}")
                raise ValueError("No 'url' found in the API response.")

            logger.info(f"Successfully generated image URL: {image_url}")
            return image_url
        except requests.exceptions.RequestException as e:
            logger.exception("Error occurred while calling the OpenAI image generation API.")
            raise ValueError(f"Error creating image with OpenAI API: {e}") from e