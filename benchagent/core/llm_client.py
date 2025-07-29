import openai
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from .config import LLMConfig


class LLMClient:
    """LLM client - wrapper for large language model calls"""
    
    def __init__(self, config: LLMConfig, task_manager=None):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.task_manager = task_manager
        
        # Initialize OpenAI client
        self.client = openai.OpenAI(
            api_key=config.api_key,
            base_url=config.base_url
        )
    
    def chat_completion(self, messages: list, **kwargs) -> str:
        """Send chat completion request"""
        try:
            # Record request start time
            request_start = datetime.now()
            
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                temperature=kwargs.get('temperature', self.config.temperature),
                max_tokens=kwargs.get('max_tokens', self.config.max_tokens),
                timeout=kwargs.get('timeout', self.config.timeout)
            )
            
            # Record response time
            request_end = datetime.now()
            response_time = (request_end - request_start).total_seconds()
            
            content = response.choices[0].message.content
            self.logger.debug(f"LLM response: {content[:200]}...")
            
            # Save interaction history
            self._save_interaction_history(
                messages=messages,
                response_content=content,
                response_time=response_time,
                model_config={
                    'model': self.config.model,
                    'temperature': kwargs.get('temperature', self.config.temperature),
                    'max_tokens': kwargs.get('max_tokens', self.config.max_tokens)
                },
                usage_info={
                    "completion_tokens": response.usage.completion_tokens,
                    "prompt_tokens": response.usage.prompt_tokens, 
                    "total_tokens": response.usage.total_tokens
                } if response.usage else None,
                context=kwargs.get('context', {})
            )
            
            return content
            
        except Exception as e:
            self.logger.error(f"LLM request failed: {e}")
            # Save failed interaction record
            self._save_interaction_history(
                messages=messages,
                error=str(e),
                context=kwargs.get('context', {})
            )
            raise
    
    def extract_code_blocks(self, text: str, language: str = None) -> list:
        """Extract code blocks from text"""
        import re
        
        if language:
            pattern = f'```{language}\\n(.*?)\\n```'
        else:
            pattern = r'```(\w+)?\n(.*?)\n```'
        
        matches = re.findall(pattern, text, re.DOTALL)
        
        if language:
            return [match.strip() for match in matches]
        else:
            return [(lang or 'unknown', code.strip()) for lang, code in matches]
    
    def extract_json_blocks(self, text: str) -> list:
        """Extract JSON blocks from text"""
        import re
        import json
        
        # Try to extract blocks surrounded by ```json
        json_pattern = r'```json\n(.*?)\n```'
        matches = re.findall(json_pattern, text, re.DOTALL)
        
        results = []
        for match in matches:
            try:
                results.append(json.loads(match.strip()))
            except json.JSONDecodeError:
                continue
        
        # If not found, try to directly parse JSON in the entire text
        if not results:
            try:
                # Find the first JSON starting with { or [
                start_idx = -1
                for i, char in enumerate(text):
                    if char in ['{', '[']:
                        start_idx = i
                        break
                
                if start_idx >= 0:
                    # Simple bracket matching to find JSON end position
                    stack = []
                    end_idx = -1
                    for i in range(start_idx, len(text)):
                        char = text[i]
                        if char in ['{', '[']:
                            stack.append(char)
                        elif char in ['}', ']']:
                            if stack:
                                opening = stack.pop()
                                if len(stack) == 0:
                                    end_idx = i + 1
                                    break
                    
                    if end_idx > start_idx:
                        json_text = text[start_idx:end_idx]
                        results.append(json.loads(json_text))
                        
            except (json.JSONDecodeError, IndexError):
                pass
        
        return results
    
    def _save_interaction_history(self, messages: List[Dict[str, str]], 
                                 response_content: str = None, 
                                 response_time: float = None,
                                 model_config: Dict[str, Any] = None,
                                 usage_info: Dict[str, Any] = None,
                                 context: Dict[str, Any] = None,
                                 error: str = None):
        """Save LLM interaction history"""
        if not self.task_manager:
            return
            
        try:
            # Build interaction record
            interaction_record = {
                "timestamp": datetime.now().isoformat(),
                "request": {
                    "messages": messages,
                    "model_config": model_config or {},
                    "context": context or {}
                },
                "response": {
                    "content": response_content,
                    "response_time_seconds": response_time,
                    "usage": usage_info,
                    "error": error
                },
                "success": error is None
            }
            
            # Save to file
            self.task_manager.save_llm_interaction(interaction_record)
            
        except Exception as e:
            # Log but don't affect main flow
            self.logger.warning(f"Failed to save LLM interaction history: {e}")