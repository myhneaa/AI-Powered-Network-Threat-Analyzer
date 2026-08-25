import os
from dotenv import load_dotenv
from google import genai
import groq

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
            self.groq_api_key = os.getenv("GROQ_API_KEY", "")
            
            self.gemini_client = None
            self.groq_client = None
            
            if self.gemini_api_key:
                self.gemini_client = genai.Client(api_key=self.gemini_api_key)
                
            if self.groq_api_key:
                self.groq_client = groq.Groq(api_key=self.groq_api_key)
                
            self._is_initialized = True

    def get_gemini_api_key(self):
        return self.gemini_api_key

    def get_groq_api_key(self):
        return self.groq_api_key

    def get_gemini_client(self):
        """Returns an instance of the GenerativeAI Client."""
        return self.gemini_client

    def get_groq_client(self):
        """Returns an instance of the Groq Client."""
        return self.groq_client


