"""Credential-free checks for the six retrieval strategies."""

from importlib import util
from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase, mock
import sys


CODE_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = CODE_DIR / "src"
sys.path.insert(0, str(SRC_DIR))


def load_example(filename: str):
    module_name = "rag_" + filename.removesuffix(".py").replace("-", "_")
    spec = util.spec_from_file_location(module_name, SRC_DIR / filename)
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeCursor:
    def __init__(self, columns: list[str], rows: list[tuple]):
        self.description = [(column,) for column in columns]
        self.rows = rows
        self.executed = []

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def execute(self, query, params=None):
        self.executed.append((query, params))

    def fetchall(self):
        return self.rows


class FakeConnection:
    def __init__(self, cursor: FakeCursor):
        self.fake_cursor = cursor

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def cursor(self):
        return self.fake_cursor


def fake_connect(cursor: FakeCursor):
    return lambda: FakeConnection(cursor)


class RetrievalStrategyTests(TestCase):
    def test_type_1_loads_the_fixture_documents_in_stable_order(self):
        example = load_example("01_document_loading.py")

        documents = example.load_all_documents()

        self.assertIn("--- faq.md ---", documents)
        self.assertIn("--- refund-policy.md ---", documents)
        self.assertLess(documents.index("faq.md"), documents.index("refund-policy.md"))

    def test_type_2_builds_a_parameterized_full_text_query(self):
        example = load_example("02_full_text_search.py")
        cursor = FakeCursor(
            ["name", "brand", "category", "price", "rating", "color", "description", "rank"],
            [("TrailBlazer Pro", "Nike", "running", 89.99, 4.5, "blue", "trail shoe", 0.9)],
        )

        with mock.patch.object(example, "connect", fake_connect(cursor)):
            results = example.full_text_search("blue running shoes", limit=3)

        query, params = cursor.executed[0]
        self.assertIn("websearch_to_tsquery", query)
        self.assertEqual(params, ("blue running shoes", "blue running shoes", 3))
        self.assertEqual(results[0]["name"], "TrailBlazer Pro")

    def test_type_3_embeds_once_then_orders_by_vector_distance(self):
        example = load_example("03_vector_search.py")
        cursor = FakeCursor(
            ["name", "brand", "category", "price", "rating", "color", "description", "similarity"],
            [("UltraGlide 3000", "Nike", "running", 129.99, 4.7, "black", "cushioned", 0.8)],
        )

        with (
            mock.patch.object(example, "embed", return_value=[0.1, 0.2]) as embed,
            mock.patch.object(example, "connect", fake_connect(cursor)),
        ):
            results = example.vector_search("comfortable long run", limit=2)

        embed.assert_called_once_with("comfortable long run")
        query, params = cursor.executed[0]
        self.assertIn("embedding <=> %s::vector", query)
        self.assertEqual(params, ("[0.1, 0.2]", "[0.1, 0.2]", 2))
        self.assertEqual(results[0]["name"], "UltraGlide 3000")

    def test_type_4_fuses_keyword_and_vector_rankings(self):
        example = load_example("04_hybrid_search.py")
        cursor = FakeCursor(
            ["name", "brand", "category", "price", "rating", "color", "description", "rrf_score"],
            [("RainRunner Pro", "Asics", "running", 119.99, 4.3, "black", "wet weather", 0.03)],
        )

        with (
            mock.patch.object(example, "embed", return_value=[0.3]),
            mock.patch.object(example, "connect", fake_connect(cursor)),
        ):
            results = example.hybrid_search("running in rain", limit=4)

        query, params = cursor.executed[0]
        self.assertIn("FULL OUTER JOIN", query)
        self.assertEqual(params["query"], "running in rain")
        self.assertEqual(params["embedding"], "[0.3]")
        self.assertEqual(params["k"], example.K)
        self.assertEqual(params["limit"], 4)
        self.assertEqual(results[0]["name"], "RainRunner Pro")

    def test_type_5_builds_bounded_sql_from_structured_filters(self):
        parameterized = load_example("05a_sql_rag_parameterized.py")

        query, values = parameterized.build_query(
            {
                "brand": "Nike",
                "category": "running",
                "max_price": 100,
                "sort_by": "price_asc",
                "limit": 200,
            }
        )

        self.assertIn("brand ILIKE %s", query)
        self.assertIn("category ILIKE %s", query)
        self.assertIn("price <= %s", query)
        self.assertTrue(query.endswith("ORDER BY price ASC LIMIT 50"))
        self.assertEqual(values, ["Nike", "running", 100])

        query, _ = parameterized.build_query({"limit": -4})
        self.assertTrue(query.endswith("LIMIT 1"))

        dynamic = load_example("05b_sql_rag_dynamic.py")
        response = SimpleNamespace(output_text="SELECT COUNT(*) FROM products")
        responses = SimpleNamespace(create=mock.Mock(return_value=response))
        client = SimpleNamespace(responses=responses)
        cursor = FakeCursor(["count"], [(12,)])

        with (
            mock.patch.object(dynamic, "get_client", return_value=client),
            mock.patch.object(dynamic, "connect", fake_connect(cursor)),
        ):
            generated = dynamic.generate_sql("How many products are there?")
            results = dynamic.execute_query(generated)

        self.assertEqual(generated, "SELECT COUNT(*) FROM products")
        self.assertEqual(results, [{"count": 12}])
        self.assertEqual(responses.create.call_args.kwargs["model"], dynamic.CHAT_MODEL)

    def test_type_6_executes_a_tool_call_then_returns_the_model_answer(self):
        example = load_example("06_agentic_rag.py")
        function_call = SimpleNamespace(
            type="function_call",
            name="load_document",
            arguments='{"filename":"refund-policy.md"}',
            call_id="call-1",
        )
        first = SimpleNamespace(id="response-1", output=[function_call])
        final_text = SimpleNamespace(type="output_text", text="Returns are allowed within 30 days.")
        message = SimpleNamespace(type="message", content=[final_text])
        second = SimpleNamespace(id="response-2", output=[message])
        responses = SimpleNamespace(create=mock.Mock(side_effect=[first, second]))
        client = SimpleNamespace(responses=responses)
        handler = mock.Mock(return_value="Return policy fixture")

        with (
            mock.patch.object(example, "get_client", return_value=client),
            mock.patch.dict(example.TOOL_HANDLERS, {"load_document": handler}),
            mock.patch("builtins.print"),
        ):
            answer = example.ask("Can I return these shoes?")

        handler.assert_called_once_with({"filename": "refund-policy.md"})
        self.assertEqual(answer, "Returns are allowed within 30 days.")
        follow_up = responses.create.call_args_list[1].kwargs
        self.assertEqual(follow_up["previous_response_id"], "response-1")
        self.assertEqual(follow_up["input"][0]["type"], "function_call_output")
        self.assertIn("not allowed", example.load_document("../sql/schema.sql"))

    def test_type_6_accepts_an_answer_after_the_eighth_tool_round(self):
        example = load_example("06_agentic_rag.py")
        tool_responses = []
        for index in range(example.MAX_TOOL_ROUNDS):
            function_call = SimpleNamespace(
                type="function_call",
                name="load_document",
                arguments='{"filename":"faq.md"}',
                call_id=f"call-{index}",
            )
            tool_responses.append(
                SimpleNamespace(id=f"response-{index}", output=[function_call])
            )
        final_text = SimpleNamespace(type="output_text", text="Final answer")
        message = SimpleNamespace(type="message", content=[final_text])
        final_response = SimpleNamespace(id="response-final", output=[message])
        responses = SimpleNamespace(
            create=mock.Mock(side_effect=[*tool_responses, final_response])
        )
        client = SimpleNamespace(responses=responses)

        with (
            mock.patch.object(example, "get_client", return_value=client),
            mock.patch.dict(
                example.TOOL_HANDLERS,
                {"load_document": mock.Mock(return_value="FAQ fixture")},
            ),
            mock.patch("builtins.print"),
        ):
            answer = example.ask("Use every allowed tool round")

        self.assertEqual(answer, "Final answer")
        self.assertEqual(responses.create.call_count, example.MAX_TOOL_ROUNDS + 1)

    def test_model_identifiers_live_only_in_shared_config(self):
        scripts = [path for path in SRC_DIR.glob("*.py") if path.name != "config.py"]
        for script in scripts:
            source = script.read_text()
            self.assertNotIn('model="gpt-', source, script.name)
            self.assertNotIn('model="text-embedding-', source, script.name)


if __name__ == "__main__":
    import unittest

    unittest.main()
