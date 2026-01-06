import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    
    # Ollama Configuration (for local LLM)
    USE_LOCAL_LLM = os.getenv("USE_LOCAL_LLM", "false").lower() == "true"
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")
    
    # Browser Configuration
    HEADLESS_BROWSER = os.getenv("HEADLESS_BROWSER", "false").lower() == "true"
    BROWSER_TIMEOUT = int(os.getenv("BROWSER_TIMEOUT", "30"))
    
    # System Configuration
    ENABLE_SYSTEM_CONTROL = os.getenv("ENABLE_SYSTEM_CONTROL", "true").lower() == "true"
    REQUIRE_CONFIRMATION = os.getenv("REQUIRE_CONFIRMATION", "true").lower() == "true"
    
    # Paths
    CHROME_DRIVER_PATH = os.getenv("CHROME_DRIVER_PATH", None)
    LOG_FILE = os.getenv("LOG_FILE", "automation.log")
    
    # Server
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))

config = Config()
