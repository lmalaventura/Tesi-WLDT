import unittest

from api_selector import ApiSelector
from prompt_builder import PromptBuilder


class PromptBuilderTest(unittest.TestCase):

    def setUp(self) -> None:
        self.selector = ApiSelector()
        self.builder = PromptBuilder()

    def test_prompt_contains_selected_endpoint(self) -> None:
        request = "Mostrami tutti i Digital Twin disponibili."
        endpoints = self.selector.select(request)

        prompt, schema = self.builder.build(endpoints, request)

        self.assertIn("GET /hdts", prompt)
        self.assertIn(
            "Restituisce tutti gli Human Digital Twin.",
            prompt,
        )
        self.assertIn(request, prompt)
        self.assertEqual(
            ["/hdts"],
            schema["properties"]["endpoint"]["enum"],
        )
        self.assertEqual(
            ["GET"],
            schema["properties"]["method"]["enum"],
        )

    def test_prompt_does_not_contain_unselected_endpoints(self) -> None:
        request = "Mostrami lo storico della proprietà heartRate."
        endpoints = self.selector.select(request)

        prompt, _ = self.builder.build(endpoints, request)

        self.assertIn(
            "POST /query/event/values/history",
            prompt,
        )
        self.assertNotIn(
            "/query/event/comparison",
            prompt,
        )
        self.assertNotIn(
            "/query/event/stats",
            prompt,
        )

    def test_build_fails_without_candidates(self) -> None:
        with self.assertRaises(ValueError):
            self.builder.build([], "Richiesta non riconosciuta")


if __name__ == "__main__":
    unittest.main()