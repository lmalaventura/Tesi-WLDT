import json
import unittest

from rest_client import RestClient, RestClientError


class RestClientTest(unittest.TestCase):

    def setUp(self) -> None:
        self.client = RestClient(
            base_url="http://localhost:8080"
        )

    def test_prepares_get_request(self) -> None:
        api_call = {
            "method": "GET",
            "endpoint": "/hdts",
            "pathParameters": {},
            "queryParameters": {},
            "body": None,
        }

        prepared = self.client.prepare(api_call)

        self.assertEqual("GET", prepared.method)
        self.assertEqual(
            "http://localhost:8080/hdts",
            prepared.url,
        )
        self.assertIsNone(prepared.body)
        self.assertNotIn(
            "Content-Type",
            prepared.headers,
        )

    def test_resolves_path_parameter(self) -> None:
        api_call = {
            "method": "GET",
            "endpoint": "/hdts/{id}/snapshot",
            "pathParameters": {
                "id": "HDT-001",
            },
            "queryParameters": {},
            "body": None,
        }

        prepared = self.client.prepare(api_call)

        self.assertEqual(
            "http://localhost:8080/hdts/HDT-001/snapshot",
            prepared.url,
        )

    def test_encodes_json_body(self) -> None:
        body = {
            "comparisons": [
                {
                    "propertyName": "systolicPressure",
                    "comparison": "GT",
                    "value": 150,
                }
            ]
        }

        api_call = {
            "method": "POST",
            "endpoint": "/query/event/comparison",
            "pathParameters": {},
            "queryParameters": {},
            "body": body,
        }

        prepared = self.client.prepare(api_call)

        self.assertEqual(
            "application/json",
            prepared.headers["Content-Type"],
        )
        self.assertEqual(
            body,
            json.loads(prepared.body.decode("utf-8")),
        )

    def test_fails_with_unresolved_path_parameter(self) -> None:
        api_call = {
            "method": "GET",
            "endpoint": "/hdts/{id}/snapshot",
            "pathParameters": {},
            "queryParameters": {},
            "body": None,
        }

        with self.assertRaises(RestClientError):
            self.client.prepare(api_call)


if __name__ == "__main__":
    unittest.main()