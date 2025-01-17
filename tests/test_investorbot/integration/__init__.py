import json


def get_mock_response(filename: str) -> dict:
    example_data = None

    with open(
        f"./tests/test_investorbot/integration/fixtures/{filename}.json", "r"
    ) as f:
        example_data = json.loads(f.read())

    return example_data
