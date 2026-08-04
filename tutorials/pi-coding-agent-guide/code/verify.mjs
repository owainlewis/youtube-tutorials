import assert from "node:assert/strict";
import { readFile, readdir } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const tutorialDir = join(dirname(fileURLToPath(import.meta.url)), "..");
const resourcesDir = join(tutorialDir, "resources");

const jsonPaths = [
  "02-configuration/models.json",
  "02-configuration/settings.json",
];

for (const relativePath of jsonPaths) {
  const contents = await readFile(join(resourcesDir, relativePath), "utf8");
  JSON.parse(contents);
}

const extensionDir = join(resourcesDir, "03-extensions");
const extensionNames = (await readdir(extensionDir)).filter((name) => name.endsWith(".ts"));
assert.ok(extensionNames.length > 0, "expected at least one extension example");

for (const name of extensionNames) {
  const contents = await readFile(join(extensionDir, name), "utf8");
  assert.match(contents, /@earendil-works\/pi-coding-agent/);
  assert.doesNotMatch(contents, /@mariozechner\/pi-coding-agent/);
}

const tutorialText = await Promise.all([
  readFile(join(tutorialDir, "README.md"), "utf8"),
  readFile(join(tutorialDir, "LESSON.md"), "utf8"),
  readFile(join(resourcesDir, "00-pricing", "README.md"), "utf8"),
]);

const joinedText = tutorialText.join("\n");
assert.doesNotMatch(joinedText, /per 1M tokens/i);
assert.doesNotMatch(joinedText, /\$\d+(?:\.\d+)?\s*\/\s*(?:month|mo)/i);

console.log("Pi tutorial resource checks passed.");
