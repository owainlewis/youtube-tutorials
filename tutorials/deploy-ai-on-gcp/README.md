# Deploy AI Systems on Google Cloud With OpenAI Codex

This is the supporting material for the video: Deploy AI Systems on Google Cloud With OpenAI Codex.

Learn a small Cloud Run Job architecture, where a coding agent helps, and how to validate the included Terraform without creating cloud resources.

## Start Here

- Read the lesson: [LESSON.md](./LESSON.md)
- Inspect the email classifier sample: [code/email-classifier/](./code/email-classifier/)
- Inspect the Terraform module: [code/terraform/](./code/terraform/)
- Read the supporting architecture: [resources/architecture.md](./resources/architecture.md)
- Review the deployment checklist: [resources/checklist.md](./resources/checklist.md)

The proposal generator material is a [design spec](./resources/spec.md) and [two prompt assets](./code/proposal-generator/backend/app/prompts/). It is not a runnable application.

## Safe Local Check

```bash
terraform -chdir=tutorials/deploy-ai-on-gcp/code/terraform fmt -check -diff
bash tutorials/deploy-ai-on-gcp/code/terraform/validate.sh
python3 -m unittest discover \
  -s tutorials/deploy-ai-on-gcp/code/email-classifier/tests \
  -v
```

These commands format-check and validate a temporary copy, then test the classifier's no-write dry-run path. They do not create Google Cloud resources.

## Go Deeper

To go deeper on AI engineering, join my AI engineering community: [aiengineer.co](https://aiengineer.co).
