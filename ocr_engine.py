import requests
import base64
import io
from PIL import Image

class OCREngine:
    def __init__(self, config_manager):
        self.config_manager = config_manager

    def perform_ocr(self, image, mode="Pure Text"):
        """
        Perform OCR on the given PIL Image object.
        Returns the text result or an error message.
        """
        api_url = self.config_manager.get("api_url")
        api_key = self.config_manager.get("api_key")
        model = self.config_manager.get("model")

        if not api_key or "YOUR_API_KEY" in api_key:
             return "Error: API Key not configured."

        # Convert image to RGB if it's RGBA (transparency not supported in JPEG)
        if image.mode in ('RGBA', 'P'):
            image = image.convert('RGB')
            
        # Convert image to base64
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        base64_image = f"data:image/jpeg;base64,{img_str}"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # Select prompt based on mode
        # "Pure Text": "Free OCR."
        # "Markdown": "Convert the document to markdown."
        # "Figure": "Parse the figure."
        prompt_text = "Free OCR." # Default
        if mode == "Markdown":
            prompt_text = "Convert the document to markdown."
        elif mode == "Figure":
            prompt_text = "Parse the figure."

        # Construct payload for Multimodal model
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": base64_image}},
                        {"type": "text", "text": prompt_text}
                    ]
                }
            ],
            "stream": False,
            "max_tokens": 4096,
            "temperature": 0.0,
            "top_p": 0.95,
        }

        try:
            response = requests.post(api_url, json=payload, headers=headers)
            response.raise_for_status() # Raise error for bad status codes
            
            data = response.json()
            # Extract content from response
            if "choices" in data and len(data["choices"]) > 0:
                content = data["choices"][0]["message"]["content"]
                return content
            else:
                return f"Error: Unexpected response format: {data}"

        except requests.exceptions.RequestException as e:
            return f"Network Error: {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"
