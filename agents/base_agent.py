import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from core.config import get_genai_client, DEFAULT_MODEL

logger = logging.getLogger("CareerCoach.BaseAgent")

class BaseAgent(ABC):
    """
    Abstract base class for all AI agents.
    Provides standard interfaces for system instruction setup and LLM calls.
    """
    
    def __init__(self, name: str, system_instruction: str, model_name: str = DEFAULT_MODEL):
        self.name = name
        self.system_instruction = system_instruction
        self.model_name = model_name
        self.client = None
        
    def _initialize_client(self) -> bool:
        """Initializes the GenAI client. Lazy loading to handle cases where API key is not ready."""
        if self.client is not None:
            return True
        
        self.client = get_genai_client()
        return self.client is not None

    def call_llm(self, prompt: str, temperature: float = 0.7, response_schema: Any = None) -> str:
        """
        Standard helper method to call Gemini API.
        """
        if not self._initialize_client():
            return "Error: Gemini client not initialized. Please verify your GEMINI_API_KEY environment variable."
            
        try:
            from google.genai import types
            
            # Setup generation config
            config = types.GenerateContentConfig(
                system_instruction=self.system_instruction,
                temperature=temperature,
            )
            
            # If structured output is requested, pass the schema
            if response_schema:
                config.response_mime_type = "application/json"
                config.response_schema = response_schema
                
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )
            
            return response.text if response.text else ""
            
        except Exception as e:
            logger.error(f"Error in agent '{self.name}' calling Gemini API: {e}")
            return f"Error: Agent '{self.name}' failed to generate a response. Details: {str(e)}"

    @abstractmethod
    def run(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Abstract run method to be implemented by each specialized agent.
        """
        pass
