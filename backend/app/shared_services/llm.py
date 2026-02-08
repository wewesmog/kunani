from openai import OpenAI
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv
from pydantic import BaseModel
import instructor
from instructor import patch
import json
from .logger_setup import setup_logger

load_dotenv()

logger = setup_logger()

# Get API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Cache for initialized clients
_clients_cache = {}


def _get_openai_client():
    """Get or create OpenAI client"""
    if "openai" not in _clients_cache:
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set")
        _clients_cache["openai"] = OpenAI(api_key=OPENAI_API_KEY)
    return _clients_cache["openai"]


def _get_openrouter_client():
    """Get or create OpenRouter client"""
    if "openrouter" not in _clients_cache:
        if not OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY not set")
        _clients_cache["openrouter"] = instructor.patch(
            OpenAI(
                api_key=OPENROUTER_API_KEY,
                base_url="https://openrouter.ai/api/v1",
                default_headers={
                    "HTTP-Referer": os.getenv("OPENROUTER_REFERRER", "https://kunani.ai"),
                    "X-Title": os.getenv("OPENROUTER_TITLE", "Kunani"),
                }
            ),
            mode=instructor.Mode.JSON
        )
    return _clients_cache["openrouter"]


def _get_gemini_client():
    """Get or create Gemini client"""
    if "gemini" not in _clients_cache:
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not set")
        try:
            import google.generativeai as genai
            genai.configure(api_key=GOOGLE_API_KEY)
            _clients_cache["gemini"] = genai
        except ImportError:
            raise ImportError("google-generativeai library required for Gemini. Install with: pip install google-generativeai")
    return _clients_cache["gemini"]


def call_llm_api(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
    provider: Optional[str] = None,
    response_format: Optional[BaseModel] = None,
    temperature: float = 0.3,
    max_tokens: int = 2000,
    fallback_providers: Optional[List[str]] = None
) -> Any:
    """
    Make a call to LLM API with structured outputs support.
    
    Args:
        messages: List of message dicts [{"role": "system/user/assistant", "content": "..."}]
        model: Model name. Format depends on provider:
            - OpenAI: "gpt-4o-mini", "gpt-4", "gpt-3.5-turbo", etc.
            - OpenRouter: "anthropic/claude-3-opus", "openai/gpt-4", "x-ai/grok-beta", etc.
            - Gemini: "gemini-pro", "gemini-pro-vision", etc. (uses Google API directly)
            - Default: "gpt-4o-mini" (OpenAI)
        provider: Provider to use. Options: "openai", "openrouter", "gemini"
            - Default: "openai" (if not specified, inferred from model or defaults to "openai")
        response_format: Optional Pydantic model for structured output
        temperature: Temperature for response generation
        max_tokens: Maximum tokens in response
    
    Returns:
        If response_format provided: Pydantic model instance
        Otherwise: String content
    """
    # Set defaults
    if provider is None:
        # Infer provider from model name if possible
        if model and model.startswith("gemini"):
            provider = "gemini"
        elif model and "/" in model:  # OpenRouter format: "provider/model"
            provider = "openrouter"
        else:
            provider = "openai"  # Default
    
    if model is None:
        if provider == "gemini":
            model = "gemini-pro"
        else:
            model = "gpt-4o-mini"  # Default OpenAI model
    
    # Fallback providers: try in order if primary fails
    if fallback_providers is None:
        fallback_providers = ["openrouter", "openai", "gemini"]
    
    providers_to_try = [provider] + [p for p in fallback_providers if p != provider]
    
    last_error = None
    for attempt_provider in providers_to_try:
        try:
            logger.info(f"[LLM] Calling {model} with {len(messages)} message(s) via {attempt_provider}")
            
            if attempt_provider == "gemini":
            import google.generativeai as genai
            import json
            
            gemini_client = _get_gemini_client()
            gemini_model = gemini_client.GenerativeModel(model)
            
            prompt_parts = []
            for msg in messages:
                if msg["role"] == "system":
                    prompt_parts.append(f"System: {msg['content']}")
                elif msg["role"] == "user":
                    prompt_parts.append(f"User: {msg['content']}")
                elif msg["role"] == "assistant":
                    prompt_parts.append(f"Assistant: {msg['content']}")
            
            full_prompt = "\n".join(prompt_parts)
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }
            
            if response_format:
                schema_instruction = f"\n\nRespond in valid JSON matching this schema: {response_format.model_json_schema()}"
                full_prompt += schema_instruction
                generation_config["response_mime_type"] = "application/json"
            
            response = gemini_model.generate_content(full_prompt, generation_config=generation_config)
            content = response.text
            
            if response_format:
                try:
                    json_data = json.loads(content)
                    result = response_format.model_validate(json_data)
                    logger.info(f"[LLM] Response received (structured format)")
                    return result
                except (json.JSONDecodeError, Exception) as e:
                    logger.error(f"[LLM] Failed to parse structured response: {e}")
                    raise
            else:
                logger.info(f"[LLM] Response received: {len(content)} characters")
                return content
        
            if attempt_provider == "openrouter":
            client = _get_openrouter_client()
            
            if response_format:
                schema_instruction = f"\n\nRespond in valid JSON matching this schema: {response_format.model_json_schema()}"
                messages_with_schema = messages.copy()
                if messages_with_schema and messages_with_schema[0].get("role") == "system":
                    messages_with_schema[0]["content"] += schema_instruction
                else:
                    messages_with_schema.insert(0, {"role": "system", "content": schema_instruction})
                
                response = client.chat.completions.create(
                    model=model,
                    messages=messages_with_schema,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    response_model=response_format
                )
                logger.info(f"[LLM] Response received (structured format via instructor)")
                return response
            else:
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                content = response.choices[0].message.content
                logger.info(f"[LLM] Response received: {len(content)} characters")
                return content
            else:
                client = _get_openai_client()
                
                if response_format:
                    schema_instruction = f"\n\nRespond in valid JSON matching this schema: {response_format.model_json_schema()}"
                    messages_with_schema = messages.copy()
                    if messages_with_schema and messages_with_schema[0].get("role") == "system":
                        messages_with_schema[0]["content"] += schema_instruction
                    else:
                        messages_with_schema.insert(0, {"role": "system", "content": schema_instruction})
                    
                    response = client.chat.completions.create(
                        model=model,
                        messages=messages_with_schema,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        response_format={"type": "json_object"}
                    )
                    
                    content = response.choices[0].message.content
                    
                    try:
                        json_data = json.loads(content)
                        result = response_format.model_validate(json_data)
                        logger.info(f"[LLM] Response received (structured format)")
                        return result
                    except (json.JSONDecodeError, Exception) as e:
                        logger.error(f"[LLM] Failed to parse structured response: {e}")
                        raise
                else:
                    response = client.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )
                    content = response.choices[0].message.content
                    logger.info(f"[LLM] Response received: {len(content)} characters")
                    return content
            
            # If we get here, the call was successful
            break
            
        except Exception as e:
            last_error = e
            logger.warning(f"[LLM] Provider {attempt_provider} failed: {e}. Trying fallback...")
            if attempt_provider == providers_to_try[-1]:
                # Last provider failed, raise the error
                logger.error(f"[LLM] All providers failed. Last error: {e}", exc_info=True)
                raise
    
    # Should never reach here, but just in case
    if last_error:
        raise last_error
