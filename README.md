# Langflow Flows and Custom Components

This repo contains custom Langflow components and ready-to-import Langflow flow JSONs. Use it as a components/flows library you can pull into your own Langflow instance.

**Table Of Contents**
- What’s Inside
- How To Use
- Prerequisites
- API Keys

## What’s Inside
- `custom_nodes/` — Custom component implementations (lfx-based components).
- `multi-agent/` — Example Langflow flows as JSON you can import.

## How To Use
1. Add custom components
   - If you are using Langflow Desktop, you must manually load custom components.
   - Point Langflow to the `custom_nodes/` directory as a custom components path in your Langflow setup.
   - After Langflow reloads, the components should appear in the UI.

2. Import flows
   - In the Langflow UI, import any JSON from `multi-agent/`.
   - The flow should load with nodes wired up; update provider credentials as needed.

The `custom_nodes/multi_query_retriever.py` component depends on the custom Qdrant retriever implemented in `custom_nodes/qdrant_vector_store_output.py`.

## Prerequisites
These flows use common services, but the blocks are interchangeable. For example, you can swap OpenAI with providers like [OpenRouter](https://openrouter.ai/docs/quickstart#authentication), [Anthropic](https://docs.anthropic.com/en/docs/getting-started), or [Google AI Studio](https://ai.google.dev/gemini-api/docs/api-key), and you can replace Cohere embeddings with Azure/OpenAI embeddings or other embedding providers.

- Langflow installed (Desktop app, Python package, or Docker container).
- AI provider (LLM).
- Embedding model provider.
- Vector store (Qdrant, Pinecone, etc.).
- Search API tool (Tavily or another web search provider).

**API Keys**
Tavily
- Sign in to the Tavily dashboard at [app.tavily.com](https://app.tavily.com/).
- Open the API keys section and copy or create a key.

OpenAI
- Sign in to the OpenAI platform at [platform.openai.com](https://platform.openai.com/).
- Go to the [API keys page](https://platform.openai.com/api-keys) and create a new secret key.

Groq
- Sign in to GroqCloud at [console.groq.com](https://console.groq.com/).
- Go to the [API keys page](https://console.groq.com/keys) and create a key.
- Groq limits: OpenAI `gpt-oss-*` models are listed at 8K TPM on the Free plan; full limits are documented in the [rate limits](https://console.groq.com/docs/rate-limits) docs.

Cohere
- Sign in to the Cohere dashboard at [dashboard.cohere.com](https://dashboard.cohere.com/).
- Go to the [API keys page](https://dashboard.cohere.com/api-keys) and create a trial or production key.

Qdrant
- Create a free Qdrant Cloud cluster at [cloud.qdrant.io](https://cloud.qdrant.io/).
- Use the cluster URL and API key when configuring the Qdrant components.
