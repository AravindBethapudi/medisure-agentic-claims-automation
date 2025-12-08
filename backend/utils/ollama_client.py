# backend/utils/ollama_client.py
import requests
import json

def ask_llama(messages, model="llama3.2:3b", temperature=0.0):
    """
    Optimized for 16GB RAM systems
    """
    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": 512,      # Limit response length
                    "num_ctx": 2048,         # Smaller context window
                    "num_thread": 4          # Optimize CPU usage
                }
            },
            timeout=180  # 3 minutes
        )
        response.raise_for_status()
        return response.json()["message"]["content"]
    except requests.exceptions.Timeout:
        print(f"⏱️ Model timeout - using fallback")
        return "{}"
    except requests.exceptions.RequestException as e:
        print(f"❌ Ollama error: {e}")
        return "{}"
    except (KeyError, json.JSONDecodeError) as e:
        print(f"❌ Parse error: {e}")
        return "{}"