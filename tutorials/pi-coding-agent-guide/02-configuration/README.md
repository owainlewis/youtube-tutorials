# Configuration

This is the supporting material for the video: Configuration.

Pi stores configuration at `~/.pi/agent/`. Here's how to set it up properly.

## Directory Structure

```
~/.pi/agent/
├── extensions/           Global extensions (auto-loaded)
├── skills/               Global skills
├── prompts/              Prompt templates
├── themes/               Custom themes
├── sessions/             Session history (JSONL)
├── models.json           Custom provider config
├── settings.json         Settings
├── auth.json             OAuth tokens (auto-managed)
├── SYSTEM.md             Replace default system prompt
└── APPEND_SYSTEM.md      Append to default system prompt
```

## Custom Providers (models.json)

Add custom model providers in `~/.pi/agent/models.json`. Changes are picked up live. No restart needed.

See [models.json](./models.json) for an example with OpenRouter and Ollama.

### OpenRouter (One Key, Every Model)

OpenRouter gives you access to hundreds of models through a single API key, including some free models. Great for trying different providers without managing separate accounts.

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

```json
{
  "providers": {
    "ollama": {
      "baseUrl": "http://localhost:11434/v1",
      "apiKey": "ollama",
      "api": "openai-chat-completions",
      "models": [
        { "id": "qwen2.5-coder:32b", "contextWindow": 32768 }
      ]
    }
  }
}
```

## System Prompt Customization

Pi's default system prompt is 24 words:

> "You are an expert coding assistant operating inside pi, a coding agent harness. You help users by reading files, executing commands, editing code, and writing new files."

Everything else (tools, guidelines, documentation) is dynamically added. You can customize the prompt in two ways:

### APPEND_SYSTEM.md (recommended)

Adds your instructions to the default prompt. The default behavior stays intact, your rules are added on top.

```
~/.pi/agent/APPEND_SYSTEM.md     Global (all projects)
.pi/APPEND_SYSTEM.md              Project-local
```

See [APPEND_SYSTEM.md](./APPEND_SYSTEM.md) for an example that adds rules about explaining reasoning, running tests, and asking before deleting files.

### SYSTEM.md (full replacement)

Replaces the default prompt entirely. Use this to fundamentally change what Pi does.

See [SYSTEM-reviewer.md](./SYSTEM-reviewer.md) for an example that turns Pi into a read-only code reviewer that cannot modify files.

To use it: copy or rename it to `~/.pi/agent/SYSTEM.md` or `.pi/SYSTEM.md`.

### CLI Options

For one-off sessions:

```bash
# Append to system prompt
pi --append-system-prompt "Always write tests first"

# Replace system prompt entirely
pi --system-prompt "You are a security auditor. Only look for vulnerabilities."
```

## Settings (settings.json)

Key settings:

```json
{
  "defaultProvider": "openai",
  "defaultModel": "gpt-5.3-codex",
  "skills": ["~/path/to/your/skills"],
  "extensionPaths": ["~/path/to/extra/extensions"],
  "compaction": {
    "threshold": 0.8
  }
}
```

## Prompt Templates

Reusable prompts stored at `~/.pi/agent/prompts/`:

```markdown
<!-- ~/.pi/agent/prompts/review.md -->
Review the recent changes in this project.
Focus on: {{focus}}
Check for bugs, security issues, and unnecessary complexity.
```

Invoke with `/review`. Pi interpolates `{{focus}}` from context.

## Go Deeper

To go deeper on AI engineering, join my AI engineering community: [aiengineer.co](https://aiengineer.co).
