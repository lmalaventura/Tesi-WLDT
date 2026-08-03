import unittest

from api_selector import ApiSelector
from validator import ApiCallValidator


class ApiCallValidatorTest(unittest.TestCase):

    def setUp(self) -> None:
        self.selector = ApiSelector()
        self.validator = ApiCallValidator()

    def test_valid_hdt_list_call(self) -> None:
        candidates = self.selector.select(
            "Mostrami tutti i Digital Twin disponibili."
        )

        api_call = {
            "method": "GET",
            "endpoint": "/hdts",
            "pathParameters": {},
            "queryParameters": {},
            "body": {},
            "missingInformation": [],
        }

        result = self.validator.validate(api_call, candidates)

        self.assertTrue(result.valid)
        self.assertTrue(result.executable)
        self.assertIsNone(api_call["body"])

    def test_valid_snapshot_call(self) -> None:
        candidates = self.selector.select(
            'Mostrami il valore corrente del Digital Twin "HDT-001".'
        )

        api_call = {
            "method": "GET",
            "endpoint": "/hdts/{id}/snapshot",
            "pathParameters": {
                "id": "HDT-001",
            },
            "queryParameters": {},
            "body": None,
            "missingInformation": [],
        }

        result = self.validator.validate(api_call, candidates)

        self.assertTrue(result.valid)
        self.assertTrue(result.executable)

    def test_rejects_replaced_endpoint_template(self) -> None:
        candidates = self.selector.select(
            'Mostrami il valore corrente del Digital Twin "HDT-001".'
        )

        api_call = {
            "method": "GET",
            "endpoint": "/hdts/HDT-001/snapshot",
            "pathParameters": {
                "id": "HDT-001",
            },
            "queryParameters": {},
            "body": None,
            "missingInformation": [],
        }

        result = self.validator.validate(api_call, candidates)

        self.assertFalse(result.valid)
        self.assertFalse(result.executable)

    def test_stats_call_is_valid_but_not_executable(self) -> None:
        candidates = self.selector.select(
            'Calcola la media della proprietà "heartRate".'
        )

        api_call = {
            "method": "POST",
            "endpoint": "/query/event/stats",
            "pathParameters": {},
            "queryParameters": {},
            "body": {
                "propertyName": "heartRate",
            },
            "missingInformation": [
                "hdtIds",
                "modelIds",
                "modelNames",
            ],
        }

        result = self.validator.validate(api_call, candidates)

        self.assertTrue(result.valid)
        self.assertFalse(result.executable)
        self.assertEqual(
            ["hdtIds", "modelIds", "modelNames"],
            result.missing_required_information,
        )

    def test_rejects_optional_dates_as_required(self) -> None:
        candidates = self.selector.select(
            'Calcola la media della proprietà "heartRate".'
        )

        api_call = {
            "method": "POST",
            "endpoint": "/query/event/stats",
            "pathParameters": {},
            "queryParameters": {},
            "body": {
                "propertyName": "heartRate",
            },
            "missingInformation": [
                "hdtIds",
                "modelIds",
                "modelNames",
                "from",
                "to",
            ],
        }

        result = self.validator.validate(api_call, candidates)

        self.assertFalse(result.valid)
        self.assertFalse(result.executable)
        self.assertTrue(
            any(
                "non obbligatorie" in error
                for error in result.errors
            )
        )


if __name__ == "__main__":
    unittest.main()