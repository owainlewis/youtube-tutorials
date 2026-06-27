/**
 * Custom Slash Command Extension
 *
 * Shows how to register your own slash commands.
 * This example adds /review and /explain commands.
 *
 * Drop this in ~/.pi/agent/extensions/ and it auto-loads.
 */
import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";

export default function (pi: ExtensionAPI) {
  // /review - sends a code review prompt to the agent
  pi.registerCommand("review", {
    description: "Review recent changes for issues",
    handler: async (args, ctx) => {
      const focus = args || "security, performance, and correctness";
      await pi.sendUserMessage(
        `Review the recent changes in this project. Focus on: ${focus}. ` +
          `Run git diff to see what changed, then give specific feedback.`
      );
    },
  });

  // /explain - ask the agent to explain a file or concept
  pi.registerCommand("explain", {
    description: "Explain a file or concept",
    getArgumentCompletions: (prefix) => {
      // Could return file paths for tab completion here
      return [];
    },
    handler: async (args, ctx) => {
      if (!args) {
        if (ctx.hasUI) {
          ctx.ui.notify("Usage: /explain <file or concept>", "warning");
        }
        return;
      }
      await pi.sendUserMessage(
        `Explain ${args} clearly. Start with the high-level purpose, ` +
          `then walk through the key details. Use examples where helpful.`
      );
    },
  });
}
