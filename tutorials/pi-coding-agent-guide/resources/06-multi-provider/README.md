# Multi-Provider Setup

This is the supporting material for the video: Multi-Provider Setup.

One of Pi's strongest features: switch between LLM providers mid-session. Use Claude for complex reasoning, GPT for speed, Gemini for large context, or a local model for privacy.

## Built-in Providers

These work out of the box with an API key or subscription:

**API Key:**
- Anthropic (Claude)
- OpenAI (GPT)
- Google Gemini
- Mistral
- Groq
- Cerebras
- xAI (Grok)
- OpenRouter (access everything through one key)
- Amazon Bedrock
- Azure OpenAI
- And 10+ more

**Subscription (OAuth):**
- Claude Pro/Max
- ChatGPT Plus/Pro
- GitHub Copilot
- Gemini CLI

## Switching Models

During a session:
- **Ctrl+P** / **Shift+Ctrl+P** to cycle through available models
- **Shift+Tab** to change thinking level (off/low/medium/high/xhigh)

Both changes take effect on the next message. No restart needed.

## Custom Providers (models.json)

Add any OpenAI-compatible API in `~/.pi/agent/models.json`:

See [models.json](./models.json) for a complete example.

### OpenRouter (Access Everything)

One API key, dozens of models:

```json
{
  "providers": {
    "openrouter": {
      "baseUrl": "https://openrouter.ai/api/v1",
      "apiKey": "${OPENROUTER_API_KEY}",
      "api": "openai-chat-completions",
      "models": [
        { "id": "anthropic/claude-sonnet-4", "contextWindow": 200000 },
        { "id": "google/gemini-2.5-pro", "reasoning": true, "contextWindow": 1000000 },
        { "id": "deepseek/deepseek-r1", "reasoning": true, "contextWindow": 128000 }
      ]
    }
  }
}
```

### Local Models (Ollama)

Run models on your own hardware:

```json
{
  "providers": {
    "ollama": {
      "baseUrl": "http://localhost:11434/v1",
      "apiKey": "ollama",
      "api": "openai-chat-completions",
      "models": [
        { "id": "qwen2.5-coder:32b", "contextWindow": 32768, "maxTokens": 8192 }
      ]
    }
  }
}
```

### LM Studio

```json
{
  "providers": {
    "lm-studio": {
      "baseUrl": "http://localhost:1234/v1",
      "apiKey": "lm-studio",
      "api": "openai-chat-completions",
      "models": [
        { "id": "your-model-name", "contextWindow": 32768 }
      ]
    }
  }
}
```

## Workflow: Pick the Right Model for the Task

A practical approach to multi-provider usage:

1. **Exploration/planning:** Use a cheap, fast model (Gemini Flash, Haiku)
2. **Complex edits:** Switch to a frontier model (Claude Opus, Codex, Gemini Pro)
3. **Second opinion:** Switch providers entirely. If Claude suggests an approach, ask GPT or Gemini to review it.
4. **Large context:** Switch to Gemini Pro (1M context) for reading huge codebases
5. **Privacy:** Switch to a local model (Ollama) for sensitive code

The key insight: you don't need the most expensive model for every message. Switch based on the task.

## Changes Are Live

`models.json` is hot-reloaded. Edit it, save, and new models appear in the Ctrl+P cycle immediately. No restart needed.

## Go Deeper

To go deeper on AI engineering, join my AI engineering community: [aiengineer.co](https://aiengineer.co).
