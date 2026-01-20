"""
LLM Client Module - Interfaces with LM Studio local inference
Handles API calls and response formatting
"""
from typing import List, Dict, Optional
import requests
import config


class LMStudioClient:
    """
    Client for LM Studio local inference
    Uses OpenAI-compatible API
    """
    
    def __init__(self, 
                 base_url: str = config.LM_STUDIO_BASE_URL,
                 model: str = config.LM_STUDIO_MODEL,
                 temperature: float = config.LLM_TEMPERATURE,
                 max_tokens: int = config.LLM_MAX_TOKENS,
                 top_p: float = config.LLM_TOP_P):
        """
        Initialize LM Studio client
        
        Args:
            base_url: LM Studio API endpoint
            model: Model name/identifier
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            top_p: Nucleus sampling parameter
        """
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
    
    def chat_completion(self, 
                       messages: List[Dict[str, str]],
                       temperature: Optional[float] = None,
                       max_tokens: Optional[int] = None) -> str:
        """
        Generate chat completion
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Override default temperature
            max_tokens: Override default max_tokens
        
        Returns:
            Generated text response
        """
        try:
            # Make direct HTTP request to LM Studio
            url = f"{self.base_url}/chat/completions"
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature or self.temperature,
                "max_tokens": max_tokens or self.max_tokens,
                "top_p": self.top_p
            }
            
            print(f"Sending request to LM Studio: {url}")
            print(f"Model: {self.model}")
            print(f"Messages count: {len(messages)}")
            
            response = requests.post(url, json=payload, timeout=120)
            
            # Log response for debugging
            print(f"Response status: {response.status_code}")
            if response.status_code != 200:
                print(f"Error response: {response.text}")
            
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
        
        except requests.exceptions.RequestException as e:
            error_msg = f"Error calling LM Studio: {str(e)}"
            print(error_msg)
            raise Exception(error_msg)
        except (KeyError, IndexError) as e:
            error_msg = f"Invalid response from LM Studio: {str(e)}"
            print(error_msg)
            raise Exception(error_msg)
    
    def generate_answer(self, 
                       system_prompt: str,
                       user_prompt: str,
                       conversation_history: Optional[List[Dict]] = None) -> str:
        """
        Generate answer given system prompt, user prompt, and optional history
        
        Args:
            system_prompt: System instruction
            user_prompt: User query with context
            conversation_history: Optional conversation history
        
        Returns:
            Generated answer
        """
        messages = []
        
        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)
        
        # Combine system prompt with user prompt since LM Studio Mistral doesn't support system role
        # Put system instructions at the beginning of the user message
        combined_prompt = f"{system_prompt}\n\n{user_prompt}"
        messages.append({"role": "user", "content": combined_prompt})
        
        return self.chat_completion(messages)


# Global client instance
_client = None


def get_llm_client() -> LMStudioClient:
    """
    Get or create global LLM client instance
    
    Returns:
        LMStudioClient instance
    """
    global _client
    if _client is None:
        _client = LMStudioClient()
    return _client


def test_connection() -> bool:
    """
    Test connection to LM Studio
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        client = get_llm_client()
        # Test with actual API call to /v1/models endpoint
        url = f"{client.base_url}/models"
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"Connection test failed: {e}")
        return False


if __name__ == "__main__":
    # Test LLM client
    print("Testing LM Studio connection...")
    
    if test_connection():
        print("✓ Connection successful")
        
        client = get_llm_client()
        
        # Test generation
        response = client.generate_answer(
            system_prompt="You are a helpful assistant.",
            user_prompt="What is 2+2?"
        )
        
        print(f"\nTest response: {response}")
    else:
        print("✗ Connection failed. Make sure LM Studio is running on localhost:1234")
