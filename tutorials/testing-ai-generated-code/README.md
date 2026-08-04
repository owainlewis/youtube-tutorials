# How I Test AI-Generated Code

This is the supporting material for the video: How I Test AI-Generated Code.

Learn how to turn requirements and risks into tests that give an AI coding agent useful feedback.

## Start Here

- Read the lesson: [LESSON.md](./LESSON.md)
- Run the offline example: [code/](./code/)
- Reuse the prompts: [resources/prompts.md](./resources/prompts.md)
- Review the copyable examples: [resources/examples/](./resources/examples/)
- Browse the slides: [resources/slides/](./resources/slides/)

## Quick Check

From the repository root:

```bash
python3 -m unittest discover \
  -s tutorials/testing-ai-generated-code/code/tests \
  -v
```

The check uses only the Python standard library. It needs no credentials or network access.

## Go Deeper

To go deeper on AI engineering, join my AI engineering community: [aiengineer.co](https://aiengineer.co).
