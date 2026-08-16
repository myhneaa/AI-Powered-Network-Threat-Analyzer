import os
from dotenv import load_dotenv
from google import genai

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
            self.client = None
            
            if self.gemini_api_key:
                self.client = genai.Client(api_key=self.gemini_api_key)
                
            self._is_initialized = True

    def get_api_key(self):
        return self.gemini_api_key

    def get_client(self):
        """Returns an instance of the GenerativeAI Client."""
        return self.client

