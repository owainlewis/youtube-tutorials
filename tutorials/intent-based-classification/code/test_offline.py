"""Credential-free checks for the routing policy and mock retrievers."""

import unittest

from intents import Intent
from routing import route_to_retrieval


class RoutingTests(unittest.TestCase):
    def test_each_intent_uses_its_expected_strategy(self) -> None:
        cases = [
            (Intent.CONCEPTUAL, "What is a JWT?", "semantic_search"),
            (Intent.PROCEDURAL, "How do I reset my API key?", "hybrid_search"),
            (Intent.FACTUAL, "What was our Q3 revenue?", "structured_query"),
            (
                Intent.COMPARATIVE,
                "Should I use Postgres or MongoDB?",
                "multi_source_retrieval",
            ),
            (Intent.OUT_OF_SCOPE, "What's the weather?", "early_exit"),
        ]

        for intent, query, expected_strategy in cases:
            with self.subTest(intent=intent):
                result = route_to_retrieval(intent, query)
                self.assertEqual(result.strategy_used, expected_strategy)
                self.assertTrue(result.chunks)

    def test_out_of_scope_query_does_not_search(self) -> None:
        result = route_to_retrieval(Intent.OUT_OF_SCOPE, "Tell me a joke")

        self.assertFalse(result.metadata["search_performed"])


if __name__ == "__main__":
    unittest.main()
