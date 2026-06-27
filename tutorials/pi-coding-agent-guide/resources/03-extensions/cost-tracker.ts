/**
 * Cost Tracker Extension
 *
 * Tracks token usage across the session and shows a running cost estimate.
 * Adds a /cost command and a persistent status widget.
 *
 * Drop this in ~/.pi/agent/extensions/ and it auto-loads.
 */
import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";

// Approximate costs per million tokens (input/output)
const PRICING: Record<string, { input: number; output: number }> = {
  "claude-opus-4": { input: 15, output: 75 },
  "claude-sonnet-4": { input: 3, output: 15 },
  "claude-haiku-4": { input: 0.8, output: 4 },
  "codex": { input: 2.5, output: 10 },
  "gpt-4o": { input: 2.5, output: 10 },
  "gpt-4o-mini": { input: 0.15, output: 0.6 },
  "gemini-2.5-pro": { input: 1.25, output: 10 },
  "gemini-2.5-flash": { input: 0.15, output: 0.6 },
};

function findPricing(modelId: string): { input: number; output: number } {
  for (const [key, price] of Object.entries(PRICING)) {
    if (modelId.includes(key)) return price;
  }
  // Default to Sonnet pricing if unknown
  return { input: 3, output: 15 };
}

let totalInputTokens = 0;
let totalOutputTokens = 0;
let totalCost = 0;

function formatCost(cost: number): string {
  if (cost < 0.01) return `$${cost.toFixed(4)}`;
  return `$${cost.toFixed(2)}`;
}

function updateStatus(ctx: any) {
  if (!ctx.hasUI) return;
  const display = `${formatCost(totalCost)} | ${totalInputTokens + totalOutputTokens} tokens`;
  ctx.ui.setStatus("cost-tracker", display);
}

export default function (pi: ExtensionAPI) {
  pi.on("session_start", async (_event, ctx) => {
    totalInputTokens = 0;
    totalOutputTokens = 0;
    totalCost = 0;
    updateStatus(ctx);
  });

  pi.on("turn_end", async (event, ctx) => {
    const usage = event.usage;
    if (!usage) return;

    const modelId = ctx.model?.id || "claude-sonnet-4";
    const pricing = findPricing(modelId);

    const inputTokens = usage.inputTokens || 0;
    const outputTokens = usage.outputTokens || 0;

    totalInputTokens += inputTokens;
    totalOutputTokens += outputTokens;
    totalCost +=
      (inputTokens * pricing.input) / 1_000_000 +
      (outputTokens * pricing.output) / 1_000_000;

    updateStatus(ctx);
  });

  pi.registerCommand("cost", {
    description: "Show session cost breakdown",
    handler: async (_args, ctx) => {
      const modelId = ctx.model?.id || "unknown";
      const summary = [
        `Model: ${modelId}`,
        `Input tokens: ${totalInputTokens.toLocaleString()}`,
        `Output tokens: ${totalOutputTokens.toLocaleString()}`,
        `Estimated cost: ${formatCost(totalCost)}`,
      ].join("\n");

      if (ctx.hasUI) {
        ctx.ui.notify(summary, "info");
      }
    },
  });
}
