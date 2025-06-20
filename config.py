import os
from typing import Dict, Any, Optional

class Config:
    """Configuration class for K8s Multi-Agent system."""
    
    def __init__(self):
        self.llm_api_key = os.getenv("GEMINI_API_KEY", "")
        self.llm_base_url = os.getenv(
            "GEMINI_BASE_URL",
            "https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        
        # Default temperature for LLM calls
        self.temperature = 0.1
        
        # Human in the loop settings
        self.require_human_approval = True
        
        # Logging settings
        self.debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
        
    def get_llm_settings(self) -> Dict[str, Any]:
        """Get the settings for LLM initialization."""
        return {
            "api_key": self.llm_api_key,
            "base_url": self.llm_base_url,
            "temperature": self.temperature
        }
        
    def update(self, **kwargs):
        """Update configuration with provided values."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
                
# Global config instance
config = Config()
