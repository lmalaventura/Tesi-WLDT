import unittest

from api_selector import ApiSelector


class ApiSelectorTest(unittest.TestCase):

    def setUp(self) -> None:
        self.selector = ApiSelector()

    def assert_single_endpoint(
        self,
        request: str,
        expected_method: str,
        expected_endpoint: str,
    ) -> None:
        selected = self.selector.select(request)

        self.assertEqual(1, len(selected))
        self.assertEqual(expected_method, selected[0].method)
        self.assertEqual(expected_endpoint, selected[0].endpoint)

    def test_selects_hdt_list(self) -> None:
        self.assert_single_endpoint(
            "Mostrami tutti i Digital Twin disponibili.",
            "GET",
            "/hdts",
        )

    def test_selects_snapshot(self) -> None:
        self.assert_single_endpoint(
            'Mostrami il valore corrente del Digital Twin "HDT-001".',
            "GET",
            "/hdts/{id}/snapshot",
        )

    def test_selects_history(self) -> None:
        self.assert_single_endpoint(
            "Mostrami lo storico della proprietà heartRate.",
            "POST",
            "/query/event/values/history",
        )

    def test_selects_comparison(self) -> None:
        self.assert_single_endpoint(
            "Trova i pazienti con pressione maggiore di 150.",
            "POST",
            "/query/event/comparison",
        )

    def test_selects_stats(self) -> None:
        self.assert_single_endpoint(
            "Calcola la media della proprietà heartRate.",
            "POST",
            "/query/event/stats",
        )

    def test_returns_empty_list_for_unknown_request(self) -> None:
        selected = self.selector.select(
            "Descrivimi il funzionamento generale del sistema."
        )

        self.assertEqual([], selected)


if __name__ == "__main__":
    unittest.main()