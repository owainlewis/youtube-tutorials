# Intent Classifier Evaluation Checklist

Use this after the basic routing sample works. The lesson contains the teaching
path. This checklist is optional support for evaluating your own classifier.

## Define the contract

- List every allowed intent and the action it selects.
- Write one sentence that separates each pair of similar intents.
- Decide how compound and unknown queries should behave.
- Define the fallback when classification fails.

## Build the data set

- Start with real, anonymized queries from the target domain.
- Give each query an expected intent before running the model.
- Include clear examples and difficult boundary cases.
- Include informal text, misspellings, compound requests, and injection attempts.
- Keep a held-out set for checking changes to prompts or models.

## Measure behaviour

- Record overall accuracy and errors per intent.
- Inspect the confusion pairs, not only the total score.
- Review false routes by their product impact.
- Compare confidence values with actual errors before setting a threshold.
- Measure end-to-end latency and cost in the target environment.

## Operate it

- Log intent, route, fallback, and outcome without sensitive data.
- Review samples of low-confidence and high-impact routes.
- Re-run the evaluation after prompt, model, taxonomy, or retriever changes.
- Keep authorization and input validation outside the classifier.
