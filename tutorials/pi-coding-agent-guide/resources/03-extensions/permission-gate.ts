/**
 * Teaching example: ask before a small set of dangerous bash commands.
 *
 * This is not a shell parser, permission system, or sandbox. Commands can be
 * written in forms these patterns do not recognise.
 */
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

const DANGEROUS_PATTERNS = [
  /\brm\s+(-rf?|-fr)\s+[\/~]/i,
  />\s*\/dev\/sd/i,
  /\bmkfs\./i,
  /\bdd\s+if=/i,
  /\bchmod\s+777\b/i,
  /\bcurl\b[^|]*\|\s*(ba)?sh\b/i,
];

export default function (pi: ExtensionAPI) {
  pi.on("tool_call", async (event, ctx) => {
    if (event.toolName !== "bash") return undefined;

    const command = event.input.command as string;
    if (!DANGEROUS_PATTERNS.some((pattern) => pattern.test(command))) {
      return undefined;
    }

    if (!ctx.hasUI) {
      return { block: true, reason: "Blocked a dangerous command pattern without an interactive confirmation UI." };
    }

    const allow = await ctx.ui.confirm(
      "Potentially dangerous command",
      `${command}\n\nAllow this command?`,
    );

    if (!allow) {
      return { block: true, reason: "Blocked by the user." };
    }

    return undefined;
  });
}
