import os
import requests
import json

class ApiImageGenerator:
    def __init__(self, api_key):
        self.api_key = api_key
        self.api_url = "https://api.openai.com/v1/images/generations"

    def generate_prompt(self, name, job_title, hobby, favorite_food):
        return f"Create a vivid background image inspired by {name}'s profession as a {job_title}, who loves {hobby} and their favorite food is {favorite_food}."

    def create_background_image(self, prompt):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        data = {
            "model": "dall-e-3",
            "prompt": prompt,
            "n": 1,
            "size": "1024x1024",
        }

        try:
            response = requests.post(self.api_url, headers=headers, data=json.dumps(data))
            response.raise_for_status()  # Raise an exception for HTTP errors

            result = response.json()
            return result['data'][0]['url']
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error creating image with OpenAI API: {e}")
