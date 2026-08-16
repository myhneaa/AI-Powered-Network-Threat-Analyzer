from log_parser import Observer
from config import Config

class BaseAgent(Observer):
    """
    Base class for all AI Agents in the system.
    Inherits from Observer to receive network logs.
    """
    def __init__(self, name: str):
        self.name = name
        self.config = Config()
        self.client = self.config.get_client()

    def update(self, data: dict):
        """
        To be implemented by child classes.
        """
        pass
