import os
from dotenv import load_dotenv
import google.generativeai as genai

class Config(object):
    """
    Singleton class to manage configuration and API keys.
    Ensures only one instance of the configuration exists.
    """
    _instance = None
    _is_initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._is_initialized:
            load_dotenv()
            self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
            
            if self.gemini_api_key:
                genai.configure(api_key=self.gemini_api_key)
                
            self._is_initialized = True

    def get_api_key(self):
        return self.gemini_api_key

    def setup_gemini_model(self, model_name="gemini-1.5-pro"):
        """Returns an instance of the GenerativeModel."""
        return genai.GenerativeModel(model_name)
