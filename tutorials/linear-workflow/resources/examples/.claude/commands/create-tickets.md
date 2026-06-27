Read the spec file at $ARGUMENTS.

Then:

1. Create a **parent issue** in Linear with the spec title as the issue title and a summary of the spec as the description. Use the team and project specified below, or ask if not clear.

2. For each task in the spec, create a **sub-issue** linked to the parent via `parentId`. Each sub-issue should include:
   - A clear title matching the task name
   - Description with: what to build, which files to touch, how to verify
   - A reference to the spec file: `Spec: <path-to-spec>`
   - Appropriate label: `feature`, `bug`, `cleanup`, `tech-debt`, or `docs`
   - Priority: 1=Urgent, 2=High, 3=Normal, 4=Low (default to 3 unless the spec says otherwise)

3. Check for **file overlaps** between tasks. If two tasks touch the same files, either:
   - Set a `blockedBy` relationship so they run sequentially, or
   - Flag the overlap and ask how to resolve it

4. Print a summary table of all created tickets with their IDs, titles, and any blocking relationships.
