from config import Config


def test_config_is_singleton():
    """
    Test that the Config class correctly implements the Singleton design pattern.
    """
    config1 = Config()
    config2 = Config()
    
    # Both variables should point to the exact same object in memory
    assert config1 is config2
    
def test_config_env_vars_missing(monkeypatch):
    """
    Test that config handles missing environment variables gracefully 
    (returns empty string, doesn't crash).
    """
    # 1. Prevent python-dotenv from reading the local .env file on disk
    monkeypatch.setattr("config.load_dotenv", lambda: None)
    
    # 2. Clear them out of the current environment
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    
    # 3. Reset the Singleton state completely
    Config._instance = None
    Config._is_initialized = False
    
    config = Config()
    
    # 4. Our config.py defaults to "" if not found, not None
    assert config.get_gemini_api_key() == ""
    assert config.get_groq_api_key() == ""
    
    # 5. Clean up Singleton state for any tests running after this
    Config._instance = None
    Config._is_initialized = False
