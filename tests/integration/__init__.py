import json


def get_mock_response(filename: str) -> dict:
    example_data = None

    with open(f"./tests/integration/fixtures/{filename}", "r") as f:
        example_data = json.loads(f.read())

    return example_data
