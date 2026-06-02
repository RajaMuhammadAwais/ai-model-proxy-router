#!/bin/bash

PROXY_MASTER_KEY="your-super-secret-proxy-key" # Replace with your actual proxy master key
BASE_URL="http://localhost:8000/v1"

echo "--- Listing Models ---"
curl -X GET \
  "${BASE_URL}/models" \
  -H "X-API-Key: ${PROXY_MASTER_KEY}"

echo "\n--- Chat Completion ---"
curl -X POST \
  "${BASE_URL}/chat/completions" \
  -H "X-API-Key: ${PROXY_MASTER_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Explain the concept of intelligent LLM routing in one sentence."}
    ],
    "temperature": 0.7,
    "max_tokens": 100
  }'

echo "\n--- Embeddings (Placeholder) ---"
curl -X POST \
  "${BASE_URL}/embeddings" \
  -H "X-API-Key: ${PROXY_MASTER_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "input": ["hello world", "how are you"],
    "model": "text-embedding-ada-002"
  }'
