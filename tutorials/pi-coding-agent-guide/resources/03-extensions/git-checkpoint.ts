/**
 * Git Checkpoint Extension
 *
 * Auto-stashes your changes before each agent turn.
 * If the agent makes a mess, you can restore with:
 *   git stash list
 *   git stash pop
 *
 * Drop this in ~/.pi/agent/extensions/ and it auto-loads.
 */
import { execSync } from "node:child_process";
import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";

function isGitRepo(cwd: string): boolean {
  try {
    execSync("git rev-parse --is-inside-work-tree", {
      cwd,
      stdio: "pipe",
    });
    return true;
  } catch {
    return false;
  }
}

function hasChanges(cwd: string): boolean {
  try {
    const status = execSync("git status --porcelain", {
      cwd,
      encoding: "utf-8",
    });
    return status.trim().length > 0;
  } catch {
    return false;
  }
}

function stash(cwd: string, message: string): boolean {
  try {
    execSync(`git stash push -m "${message}" --include-untracked`, {
      cwd,
      stdio: "pipe",
    });
    return true;
  } catch {
    return false;
  }
}

export default function (pi: ExtensionAPI) {
  pi.on("turn_start", async (_event, ctx) => {
    const cwd = ctx.cwd;
    if (!isGitRepo(cwd) || !hasChanges(cwd)) return;

    const timestamp = new Date().toISOString().slice(0, 19);
    const message = `pi-checkpoint-${timestamp}`;

    if (stash(cwd, message)) {
      // Pop immediately to keep working tree intact but save the stash
      try {
        execSync("git stash pop", { cwd, stdio: "pipe" });
      } catch {
        // Conflict on pop. Leave it stashed so the user can resolve.
      }
    }
  });
}
