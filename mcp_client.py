from openai import OpenAI
from typing import Dict, Any, Optional

from config import config


class MCPClient:
    """Client for interacting with LLM APIs using the OpenAI client."""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """Initialize the MCP client.
        
        Args:
            api_key: The API key to use for authentication
            base_url: The base URL for the API
        """
        settings = config.get_llm_settings()
        
        self.client = OpenAI(
            api_key=api_key or settings["api_key"],
            base_url=base_url or settings["base_url"]
        )
        
        self.temperature = settings["temperature"]
    
    def generate(self, 
                 system_prompt: str, 
                 user_prompt: str, 
                 temperature: Optional[float] = None) -> str:
        """Generate a response from the LLM.
        
        Args:
            system_prompt: The system prompt to guide the LLM's role and behavior
            user_prompt: The user prompt containing the query or task
            temperature: Optional temperature override for this specific call
            
        Returns:
            The LLM's response as a string
        """
        try:
            response = self.client.chat.completions.create(
                model="gemini-pro",  # This will be ignored by Gemini API but required by OpenAI client
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature or self.temperature
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error generating LLM response: {str(e)}")
            return f"[LLM ERROR: {str(e)}]"
