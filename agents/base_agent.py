from config import Config


class BaseAgent:
    """
    Base class for all AI Agents in the system.
    Provides shared access to the configuration and LLM clients.
    """
    def __init__(self, name: str):
        self.name = name
        self.config = Config()
        self.gemini_client = self.config.get_gemini_client()
        self.groq_client = self.config.get_groq_client()
