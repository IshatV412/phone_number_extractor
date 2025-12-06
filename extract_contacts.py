import os
from google import genai
from google.genai import errors as genai_errors
import yaml
from PIL import Image
import json
import time

with open("config.yaml", "r") as f:
    CONFIG = yaml.safe_load(f)


class APIKeyManager:
    """Manages multiple API keys with automatic failover on errors."""
    
    def __init__(self, api_keys, model):
        self.api_keys = api_keys
        self.model = model
        self.current_key_index = 0
        self.client = self._create_client()
    
    def _create_client(self):
        """Create a new client with the current API key."""
        return genai.Client(api_key=self.api_keys[self.current_key_index])
    
    def switch_key(self):
        """Switch to the next available API key."""
        old_index = self.current_key_index
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        self.client = self._create_client()
        print(f"Switched from API key {old_index + 1} to key {self.current_key_index + 1}")
        return self.current_key_index != old_index  # True if we haven't cycled through all keys
    
    def generate_content(self, contents, max_retries=3):
        """Generate content with automatic key rotation on failure."""
        keys_tried = 0
        last_error = None
        
        while keys_tried < len(self.api_keys):
            retries = 0
            while retries < max_retries:
                try:
                    response = self.client.models.generate_content(
                        model=self.model,
                        contents=contents
                    )
                    return response
                except (genai_errors.ClientError, genai_errors.ServerError) as e:
                    last_error = e
                    error_msg = str(e)
                    
                    # Check if it's a rate limit or quota error
                    if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg or "quota" in error_msg.lower():
                        print(f"Rate limit hit on key {self.current_key_index + 1}, switching...")
                        break  # Switch to next key
                    elif "API_KEY_INVALID" in error_msg or "400" in error_msg:
                        print(f"Invalid API key {self.current_key_index + 1}, switching...")
                        break  # Switch to next key
                    else:
                        # Other error, retry with backoff
                        retries += 1
                        if retries < max_retries:
                            wait_time = 2 ** retries
                            print(f"Error: {e}. Retrying in {wait_time}s... ({retries}/{max_retries})")
                            time.sleep(wait_time)
                        else:
                            break  # Max retries reached, try next key
                except Exception as e:
                    last_error = e
                    retries += 1
                    if retries < max_retries:
                        wait_time = 2 ** retries
                        print(f"Unexpected error: {e}. Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        break
            
            # Switch to next key
            keys_tried += 1
            if keys_tried < len(self.api_keys):
                self.switch_key()
        
        # All keys exhausted
        raise Exception(f"All API keys exhausted. Last error: {last_error}")


# Initialize the key manager
key_manager = APIKeyManager(CONFIG["api_keys"], CONFIG["model"])

PROMPT = """This is a screenshot from a WhatsApp contact selection screen. 
Each row represents a contact with:
- A circular profile picture/avatar on the left
- The contact name or phone number displayed next to it
- Some contacts show a saved name (like "Tanmay Jain" or "~ Aayu$hhh_16")
- Unsaved contacts show only their phone number in format "+91 XXXXX XXXXX"

Extract ALL visible contacts from this image. For each contact row, extract:
1. The name (if it's a saved contact with a name)
2. The phone number (if visible, usually in format +91 XXXXX XXXXX)

Note: A single contact may have BOTH a name and phone number visible, or just one of them.
Skip any UI elements like "You", headers, or navigation buttons.

Return the data as a JSON array with this exact format:
```json
[
  {"name": "Contact Name Here", "phone": "+91 XXXXX XXXXX"},
  {"name": null, "phone": "+91 12345 67890"},
  {"name": "Saved Contact Name", "phone": null}
]
```

Use null for missing values. Only return the JSON array, no other text."""

def extract_contacts():
    """Extract contacts from images using Gemini API."""
    records = []
    image_files = os.listdir("./images")
    total = len(image_files)
    
    for i, image_path in enumerate(image_files):
        print(f"Processing {i+1}/{total}: {image_path}")
        image = Image.open("./images/" + image_path)
        response = key_manager.generate_content([image, PROMPT])
        print(response.text)
        records.append(response.text)
    
    with open("contacts.json", "w") as f:
        json.dump(records, f)
    
    print(f"Saved {len(records)} records to contacts.json")
    return len(records)


if __name__ == "__main__":
    extract_contacts()
