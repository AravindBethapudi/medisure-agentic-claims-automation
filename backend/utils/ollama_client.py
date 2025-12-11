import requests
import json
import os  # Add this import

def ask_llama(messages, model="llama3.2:1b", temperature=0.0):
    """
    Optimized for 16GB RAM systems
    """
    # Get Ollama URL from environment variable, default to localhost
    OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    
    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/chat",  # Use environment variable
            json={
                "model": model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": 512,
                    "num_ctx": 2048,
                    "num_thread": 4
                }
            },
            timeout=180
        )
        response.raise_for_status()
        return response.json()["message"]["content"]
    except requests.exceptions.Timeout:
        print(f"⏱️ Model timeout - using fallback")
        return "{}"
    except requests.exceptions.RequestException as e:
        print(f"❌ Ollama error connecting to {OLLAMA_HOST}: {e}")
        return "{}"
    except (KeyError, json.JSONDecodeError) as e:
        print(f"❌ Parse error: {e}")
        return "{}"