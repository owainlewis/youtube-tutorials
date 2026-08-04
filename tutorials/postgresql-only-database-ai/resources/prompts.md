# Retrieval Evaluation Prompt

Use this prompt after you have collected representative questions, expected source documents, and the results from vector, full-text, and hybrid retrieval.

```text
Review these retrieval cases.

For each case:
1. Compare the expected source IDs with the returned source IDs.
2. Identify useful results, missing results, and unrelated results.
3. Do not judge the generated answer. Judge retrieval only.
4. Suggest one testable change to chunking, metadata filters, query text, result count, or fusion settings.
5. State what evidence would show that the change helped.

Return a table with:
- question
- retrieval method
- expected sources
- returned sources
- failure type
- proposed experiment
- success measure

Cases:
<paste cases here>
```

Keep the same evaluation cases while comparing retrieval methods. Do not choose a method from one successful demo query.
