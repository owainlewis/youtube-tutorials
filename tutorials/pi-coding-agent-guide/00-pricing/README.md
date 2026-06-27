# Pricing and Providers

This is the supporting material for the video: Pricing and Providers.

Pi is free. You pay for the LLM provider you connect to.

## How Each Provider Works

| Provider | How it works in Pi |
|----------|-------------------|
| **Anthropic Claude** | API key or extra usage (both billed per token) |
| **OpenAI ChatGPT** | Subscription works for personal use |
| **GitHub Copilot** | Subscription works via OAuth |
| **Google Gemini CLI** | Subscription works via OAuth |
| **OpenRouter** | API key (access all providers through one key) |
| **Ollama** | Free (runs on your hardware) |

### Claude: API Key or Extra Usage

You can't use your Claude Pro/Max plan's included usage through Pi. If you connect your subscription, it draws from "extra usage" which is billed per token. You'll see this warning:

> Warning: Anthropic subscription auth is active. Third-party usage now draws from extra usage and is billed per token, not your Claude plan limits.

In practice, this is the same as paying per token. **Just use an API key. It's simpler.**

```bash
# Get an API key at console.anthropic.com
export ANTHROPIC_API_KEY=sk-ant-...
```

### OpenAI: Your Subscription Works

If you have ChatGPT Plus or Pro, you can use it with Pi via `/login`. It works for personal use. This is the easiest way to get started with Pi.

```bash
pi
# Then inside Pi:
/login
# Select OpenAI and follow the browser flow
```

## API Key Pricing

| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|-------|----------------------|------------------------|
| Claude Opus 4.6 | $5.00 | $25.00 |
| Claude Sonnet 4.6 | $3.00 | $15.00 |
| Claude Haiku 4.5 | $1.00 | $5.00 |
| Codex | Included with ChatGPT Plus ($20/mo) | - |
| Gemini 2.5 Pro | $1.25 | $10.00 |
| Gemini 2.5 Flash | $0.15 | $0.60 |
| DeepSeek R1 | $0.55 | $2.19 |

## Pi's Cost Advantage

Pi's system prompt is under 1,000 tokens. Claude Code's is 10,000+. That's 9,000 fewer tokens of overhead on every API call.

## The Smart Setup

Pi's real pricing advantage is model switching. Use the cheapest model for each task:

1. **Exploration/planning:** Cheap model (Gemini Flash, Haiku)
2. **Complex work:** Frontier model (Sonnet, Opus, Codex)
3. **Second opinion:** Switch providers entirely

Switch mid-session with `Ctrl+P`. Claude Code can't do this.

## Go Deeper

To go deeper on AI engineering, join my AI engineering community: [aiengineer.co](https://aiengineer.co).
