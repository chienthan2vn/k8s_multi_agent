from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple, List

from langchain.prompts import PromptTemplate
from langchain_core.language_models import BaseLLM

from config import config


class BaseAgent(ABC):
    """Base class for all agents in the system."""

    def __init__(self, llm: BaseLLM, system_prompt: str):
        """Initialize the base agent.
        
        Args:
            llm: The language model to use
            system_prompt: The system prompt that defines the agent's role
        """
        self.llm = llm
        self.system_prompt = system_prompt
        
    @abstractmethod
    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Run the agent on the given inputs.
        
        Args:
            inputs: The inputs to the agent
            
        Returns:
            The outputs from the agent
        """
        pass
    
    def _format_prompt(self, template: str, **kwargs) -> str:
        """Format a prompt template with the given arguments.
        
        Args:
            template: The prompt template
            kwargs: The arguments to format the template with
            
        Returns:
            The formatted prompt
        """
        prompt_template = PromptTemplate.from_template(template)
        return prompt_template.format(**kwargs)
    
    def _get_llm_response(self, prompt: str) -> str:
        """Get a response from the LLM.
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            The LLM's response
        """
        if config.debug_mode:
            print(f"[DEBUG] Agent prompt: {prompt}")
            
        response = self.llm.invoke(prompt)
        
        if config.debug_mode:
            print(f"[DEBUG] Agent response: {response}")
            
        return response
