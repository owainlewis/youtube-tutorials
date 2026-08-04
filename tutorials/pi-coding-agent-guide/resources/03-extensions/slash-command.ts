/** Register two small prompt commands. */
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

export default function (pi: ExtensionAPI) {
  pi.registerCommand("review", {
    description: "Review recent changes for important issues",
    handler: async (args, ctx) => {
      const focus = args || "correctness, security, and unnecessary complexity";
      await ctx.sendUserMessage(
        `Review the recent changes. Focus on ${focus}. Read the diff and report ` +
          "specific findings with file paths and line numbers. Do not edit files.",
      );
    },
  });

  pi.registerCommand("explain", {
    description: "Explain a file or technical concept",
    handler: async (args, ctx) => {
      if (!args) {
        if (ctx.hasUI) ctx.ui.notify("Usage: /explain <file or concept>", "warning");
        return;
      }

      await ctx.sendUserMessage(
        `Explain ${args}. Start with its purpose, then show the important details ` +
          "and one concrete example. Do not edit files.",
      );
    },
  });
}
