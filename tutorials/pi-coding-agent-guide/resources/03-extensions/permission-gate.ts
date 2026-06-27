/**
 * Permission Gate Extension
 *
 * Blocks dangerous bash commands before they execute.
 * This replicates the safety behavior that Claude Code provides by default.
 *
 * Drop this in ~/.pi/agent/extensions/ and it auto-loads.
 */
import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";

const DANGEROUS_PATTERNS = [
  /rm\s+(-rf|-fr)\s+[\/~]/,  // rm -rf with absolute/home paths
  />\s*\/dev\/sd/,            // writing to block devices
  /mkfs\./,                   // formatting filesystems
  /dd\s+if=/,                 // raw disk writes
  /chmod\s+777/,              // overly permissive permissions
  /curl.*\|\s*(ba)?sh/,       // pipe curl to shell
];

export default function (pi: ExtensionAPI) {
  pi.on("tool_call", async (event, ctx) => {
    if (event.toolName !== "bash") return;

    const command = event.input.command as string;

    for (const pattern of DANGEROUS_PATTERNS) {
      if (pattern.test(command)) {
        if (ctx.hasUI) {
          const allow = await ctx.ui.confirm(
            `Blocked dangerous command:\n${command}\n\nAllow anyway?`
          );
          if (allow) return;
        }
        return { block: true, reason: `Blocked dangerous command: ${command}` };
      }
    }
  });
}
