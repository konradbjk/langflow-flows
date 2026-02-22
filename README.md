# Langflow Flows and Custom Components

This repo contains custom Langflow components and ready-to-import Langflow flow JSONs. Use it as a components/flows library you can pull into your own Langflow instance.

**What’s Inside**
- `custom_nodes/` — Custom component implementations (lfx-based components).
- `multi-agent/` — Example Langflow flows as JSON you can import.

**How To Use**
1. Add custom components
   - Point Langflow to the `custom_nodes/` directory as a custom components path in your Langflow setup.
   - After Langflow reloads, the components should appear in the UI.

2. Import flows
   - In the Langflow UI, import any JSON from `multi-agent/`.
   - The flow should load with nodes wired up; update provider credentials as needed.

**API Keys**
Below are the current official steps to get API keys for providers used in these flows. Keep keys in your environment or a secure secrets manager.

Tavily
- Sign in to the Tavily Platform and open your dashboard.
- Your API keys are listed in the dashboard; you can add additional keys there.

OpenAI
- Sign in to the OpenAI platform.
- Find or create a Secret API key on the API keys page.

Groq
- Follow the Groq Quickstart to create an API key in GroqCloud.
- The quickstart recommends setting `GROQ_API_KEY` as an environment variable.

Cohere
- Cohere provides evaluation and production keys.
- Create a trial or production key from the API keys page.

**Key Pages (for reference)**
```
https://app.tavily.com/
https://help.tavily.com/articles/9170796666-how-can-i-create-an-api-key
https://platform.openai.com/api-keys
https://help.openai.com/en/articles/4936850-where-do-i-find-my-openai-api-key
https://console.groq.com/keys
https://console.groq.com/docs/quickstart
https://dashboard.cohere.com/api-keys
https://docs.cohere.com/docs/rate-limits
```
