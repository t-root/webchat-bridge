"""Example API client for calling the local OpenAI-compatible server."""

import json
import requests
from typing import Optional

# Configuration
API_HOST = "http://127.0.0.1"
API_PORT = 5000
BASE_URL = f"{API_HOST}:{API_PORT}"


def call_chat_completions(
    messages: list,
    model: str = "gpt",
    stream: bool = False,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
) -> dict:
    """
    Call the /v1/chat/completions endpoint.
    
    Args:
        messages: List of message dicts with 'role' and 'content' keys
        model: Model ID to use
        stream: Enable streaming
        temperature: Temperature for generation
        max_tokens: Maximum tokens to generate
    
    Returns:
        Response dict from the API
    """
    url = f"{BASE_URL}/v1/chat/completions"
    
    payload = {
        "messages": messages,
        "model": model,
        "stream": stream,
        "temperature": temperature,
    }
    
    if max_tokens:
        payload["max_tokens"] = max_tokens
    
    print(f"📤 Calling {url}")
    print(f"📝 Payload: {json.dumps(payload, indent=2)}")
    
    # timeout=None — wait until the web AI finishes responding (no time limit)
    response = requests.post(url, json=payload, timeout=None)
    response.raise_for_status()
    
    return response.json()


def get_available_models() -> dict:
    """Get available models from bridge server."""
    try:
        bridge_port = 3000
        url = f"{API_HOST}:{bridge_port}/api/ai/config"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get("models", {})
    except Exception as e:
        print(f"⚠️ Failed to load models from server: {e}")
        # Return default models as fallback
        return {
            "claude": {
                "name": "Claude",
                "model": "claude",
            },
            "chatgpt": {
                "name": "ChatGPT",
                "model": "gpt",
            },
            "gemini": {
                "name": "Gemini",
                "model": "gemini",
            },
            "deepseek": {
                "name": "DeepSeek",
                "model": "deepseek",
            }
        }


def select_model_interactive() -> str:
    """Interactively select a model from available options."""
    models = get_available_models()
    
    if not models:
        print("❌ No models available")
        return "gpt"
    
    print("Select model:")
    model_options = []
    choice_to_model = {}
    
    for idx, (platform_key, platform_config) in enumerate(models.items(), 1):
        name = platform_config.get("name", platform_key)
        model_id = platform_config.get("model", platform_key)
        
        print(f"{idx}️⃣  {name} ({model_id})")
        model_options.append(model_id)
        choice_to_model[str(idx)] = model_id
    
    print()
    
    default_choice = "1"
    choice = input(f"Choose (1-{len(model_options)}) [default {default_choice}]: ").strip() or default_choice
    
    selected_model = choice_to_model.get(choice, model_options[0] if model_options else "gpt")
    print(f"\n✓ Using model: {selected_model}\n")
    
    return selected_model


def list_models() -> dict:
    """List available models."""
    url = f"{BASE_URL}/v1/models"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def health_check() -> dict:
    """Check server health."""
    url = f"{BASE_URL}/health"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def display_response(response: dict, show_full: bool = False):
    """Display response in a properly formatted way."""
    try:
        # Extract key info
        model = response.get("model", "unknown")
        request_id = response.get("id", "N/A")
        timestamp = response.get("created", "N/A")
        
        # Extract message content
        choices = response.get("choices", [])
        if not choices:
            print("❌ No choices in response")
            return None
        
        first_choice = choices[0]
        message = first_choice.get("message", {})
        content = message.get("content", "").strip()
        finish_reason = first_choice.get("finish_reason", "unknown")
        
        # Extract usage stats
        usage = response.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", 0)
        
        if show_full:
            # Full detailed response
            print("\n" + "=" * 60)
            print("📦 FULL API RESPONSE")
            print("=" * 60)
            print(f"Model: {model}")
            print(f"Request ID: {request_id}")
            print(f"Finish Reason: {finish_reason}")
            print("-" * 60)
            print("💬 ASSISTANT MESSAGE:")
            print(content)
            print("-" * 60)
            print(f"📊 USAGE STATS:")
            print(f"  • Prompt tokens: {prompt_tokens}")
            print(f"  • Completion tokens: {completion_tokens}")
            print(f"  • Total tokens: {total_tokens}")
            print("-" * 60)
            print(f"Full JSON Response:\n{json.dumps(response, indent=2, ensure_ascii=False)}")
        else:
            # Clean, concise response
            print(f"\n🤖 Assistant ({model}):")
            print(content)
            print(f"\n📊 [{prompt_tokens} → {completion_tokens} tokens]")
        
        return content
    
    except Exception as e:
        print(f"❌ Error displaying response: {e}")
        print(f"Raw response: {json.dumps(response, indent=2, ensure_ascii=False)}")
        return None


if __name__ == "__main__":
    import sys
    
    # Check server is running
    try:
        print("🏥 Checking server health...\n")
        health = health_check()
        print(f"✓ Server is running: {health}\n")
    except Exception as e:
        print(f"❌ Server is not running: {e}")
        print(f"Start the server with: python server.py")
        sys.exit(1)
    
    # Choose display mode
    print("=" * 60)
    print("Chat Completions API Client")
    print("=" * 60)
    print("\nSelect display mode:")
    print("1️⃣  Full API response (JSON + token stats)")
    print("2️⃣  Assistant reply only (concise)\n")
    
    while True:
        mode_choice = input("Choose (1 or 2): ").strip()
        if mode_choice in ["1", "2"]:
            show_full_api = mode_choice == "1"
            break
        print("❌ Please choose 1 or 2\n")
    
    # Interactive Chat with context
    print("\n" + "=" * 60)
    print("Type a message to chat. Enter 'exit' or 'quit' to stop.\n")
    
    # Choose model (load from server)
    selected_model = select_model_interactive()
    
    conversation_history = []
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break
        
        if not user_input:
            continue
        
        # Add user message to history
        conversation_history.append({"role": "user", "content": user_input})
        
        try:
            print("\n⏳ Waiting for response...")
            response = call_chat_completions(
                messages=conversation_history,
                model=selected_model
            )
            
            # Display and extract assistant response
            assistant_message = display_response(response, show_full=show_full_api)
            
            # Add to history if we got a valid response
            if assistant_message:
                conversation_history.append({"role": "assistant", "content": assistant_message})
            print()
        except Exception as e:
            print(f"❌ Error: {e}\n")
