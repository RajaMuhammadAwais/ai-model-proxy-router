import httpx
import asyncio

async def main():
    api_key = "your-proxy-master-key" # Replace with your actual proxy master key
    base_url = "http://localhost:8000/v1"

    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }

    # Example 1: List Models
    print("\n--- Listing Models ---")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/models", headers=headers)
            response.raise_for_status()
            models = response.json()
            print(models)
    except httpx.HTTPStatusError as e:
        print(f"Error listing models: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        print(f"Request error listing models: {e}")

    # Example 2: Chat Completion
    print("\n--- Chat Completion ---")
    chat_payload = {
        "messages": [
            {"role": "user", "content": "Explain the concept of intelligent LLM routing in one sentence."}
        ],
        "temperature": 0.7,
        "max_tokens": 100
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{base_url}/chat/completions", headers=headers, json=chat_payload)
            response.raise_for_status()
            chat_response = response.json()
            print(chat_response)
    except httpx.HTTPStatusError as e:
        print(f"Error during chat completion: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        print(f"Request error during chat completion: {e}")

    # Example 3: Embeddings (placeholder, as not fully implemented yet)
    print("\n--- Embeddings (Placeholder) ---")
    embeddings_payload = {
        "input": ["hello world", "how are you"],
        "model": "text-embedding-ada-002" # This model will be routed by the system
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{base_url}/embeddings", headers=headers, json=embeddings_payload)
            response.raise_for_status()
            embeddings_response = response.json()
            print(embeddings_response)
    except httpx.HTTPStatusError as e:
        print(f"Error during embeddings: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        print(f"Request error during embeddings: {e}")

if __name__ == "__main__":
    asyncio.run(main())
