# AI Model Proxy & Intelligent Router System

This project implements a production-grade AI Model Proxy and Intelligent Router System. It acts as a universal OpenAI-compatible gateway for multiple LLM providers, offering dynamic capability-based routing, a plugin-based provider architecture, robust observability, security features, and self-learning capabilities.

## Features

-   **OpenAI-Compatible API**: Exposes standard `/v1/chat/completions`, `/v1/models`, and `/v1/embeddings` endpoints.
-   **Dynamic Routing**: Intelligently routes requests to the best LLM provider based on real-time model capabilities, cost, latency, and request intent.
-   **Plugin-Based Architecture**: Easily extendable to integrate new LLM providers with minimal changes to the core system.
-   **Config-Driven Design**: All routing policies, provider configurations, and system behaviors are managed via external configuration files and environment variables.
-   **Reliability**: Includes built-in retry mechanisms with exponential backoff, timeout controls, and circuit breaker patterns to ensure system resilience.
-   **Observability**: Integrated with OpenTelemetry for comprehensive tracing, metrics, and logging to monitor system health and performance.
-   **Security**: Features API key encryption at rest, request validation, and rate limiting.
-   **Scalability**: Designed with an asynchronous FastAPI backend to handle high throughput and low latency, suitable for containerized deployments.

## Getting Started

### Prerequisites

-   Python 3.8+
-   `pip` or `uv` package manager
-   Redis (optional, for caching)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/RajaMuhammadAwais/europulse-ai.git
    cd europulse-ai
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure environment variables:**
    Copy `.env.example` to `.env` and fill in your API keys and other settings.
    ```bash
    cp .env.example .env
    # Edit .env with your actual values
    ```

4.  **Configure `config.yaml`:**
    Copy `config.yaml.example` to `config.yaml` and adjust provider settings and routing policies as needed.
    ```bash
    cp config.yaml.example config.yaml
    # Edit config.yaml with your desired configurations
    ```

### Running the Application

```bash
python -m uvicorn ai_model_proxy.main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`.

## API Usage Examples

Refer to `example_api_usage.py` (Python) and `curl_api_usage.sh` (cURL) for examples on how to interact with the proxy.

## Project Structure

```
├── ai_model_proxy/
│   ├── __init__.py
│   ├── main.py                     # FastAPI application entry point
│   ├── config/
│   │   ├── manager.py              # Handles loading and managing configurations
│   │   └── schema.py               # Pydantic models for configuration validation
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   └── endpoints.py        # OpenAI-compatible API endpoints
│   │   └── dependencies.py         # API dependencies (auth, rate limiting)
│   ├── core/
│   │   ├── __init__.py
│   │   ├── router.py               # Router Engine implementation
│   │   ├── analyzer.py             # Request Analyzer implementation
│   │   └── manager.py              # Core logic for managing requests and components
│   ├── providers/
│   │   ├── __init__.py
│   │   ├── base.py                 # Base Provider Plugin interface
│   │   ├── nvidia_nim.py           # NVIDIA NIM Provider Adapter
│   │   ├── openrouter.py           # OpenRouter Provider Adapter
│   │   ├── groq.py                 # Groq Provider Adapter
│   │   ├── gemini.py               # Gemini Provider Adapter
│   │   └── ollama.py               # Ollama Provider Adapter
│   ├── services/
│   │   ├── __init__.py
│   │   ├── cache.py                # Caching service (e.g., Redis client)
│   │   ├── observability.py        # Logging, tracing, metrics setup (OpenTelemetry)
│   │   └── reliability.py          # Retry, circuit breaker patterns
│   ├── models/
│   │   ├── __init__.py
│   │   └── llm_metadata.py         # Pydantic models for LLM metadata and request/response
│   └── security/
│       ├── __init__.py
│       └── auth.py                 # API key encryption, request validation
├── tests/
│   ├── __init__.py
│   ├── unit/
│   ├── integration/
│   └── performance/
├── docs/
│   └── architecture.md             # Detailed architecture documentation
├── scripts/
│   └── setup.sh                    # Setup script for environment
├── .env.example                    # Example environment variables
├── config.yaml.example             # Example configuration file
├── Dockerfile                      # Dockerization for deployment
├── requirements.txt                # Python dependencies
└── README.md                       # Project README
```

## Design Documentation

For a detailed explanation of the system architecture, design decisions, and component contracts, please refer to `ai_model_proxy_design.md`.

## License

This project is licensed under the MIT License.
