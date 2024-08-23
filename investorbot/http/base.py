from dataclasses import dataclass
import uuid
import hashlib
import hmac
import json
import logging
from typing import Dict
import requests
from os import path
from pathlib import Path
from urllib.parse import urlparse
from investorbot.timeseries import time_now
from investorbot.constants import DEFAULT_LOGS_NAME, INVESTOR_APP_ENVIRONMENT

logger = logging.getLogger(DEFAULT_LOGS_NAME)


@dataclass
class HttpClient:
    api_url: str
    id_incr: int

    def write_request_to_file(
        self, uri_string: str, response_text: str, response_code: str
    ):

        if INVESTOR_APP_ENVIRONMENT != "Development":
            return

        # from urlparse import urlparse  # Python 2
        parsed_uri = urlparse(uri_string)

        result = "./api{uri.path}".format(uri=parsed_uri)
        directory_path_components = result.split("/")

        directory_path = path.join(*directory_path_components)
        logger.debug(directory_path)

        Path(directory_path).mkdir(parents=True, exist_ok=True)
        file_path = path.join(
            directory_path, f"status{response_code}{uuid.uuid4()}.json"
        )

        response_dict = json.loads(response_text)
        response_formatted = json.dumps(response_dict, indent=4)

        with open(file_path, "w") as f:
            f.write(response_formatted)

    def get(self, method: str):
        response = requests.get(f"{self.api_url}{method}")

        if response.status_code != 200:
            response.raise_for_status()

        self.write_request_to_file(
            f"{self.api_url}{method}", response.text, response.status_code
        )

        return json.loads(response.text)

    def get_data(self, method: str):
        return self.get(method)["result"]["data"]


@dataclass
class AuthenticatedHttpClient(HttpClient):
    api_key: str
    api_secret_key: str

    def __params_to_str(self, obj, level):
        if level >= 3:  # ! level 3 seems to be arbitrarily chosen in crypto.com docs
            return str(obj)

        return_str = ""
        for key in sorted(obj):
            return_str += key
            if obj[key] is None:
                return_str += "null"
            elif isinstance(obj[key], list):
                for subObj in obj[key]:
                    return_str += self.__params_to_str(subObj, level + 1)
            else:
                return_str += str(obj[key])
        return return_str

    def __get_signature(self, req: dict) -> str:
        """
        See https://exchange-docs.crypto.com/exchange/v1/rest-ws/index.html#digital-signature
        """

        # First ensure the params are alphabetically sorted by key
        param_str = ""

        if "params" in req:
            param_str = self.__params_to_str(req["params"], 0)

        payload_str = (
            req["method"]
            + str(req["id"])
            + req["api_key"]
            + param_str
            + str(req["nonce"])
        )

        return hmac.new(
            bytes(str(self.api_secret_key), "utf-8"),
            msg=bytes(payload_str, "utf-8"),
            digestmod=hashlib.sha256,
        ).hexdigest()

    def post_request(self, method: str, params={}) -> Dict:
        req = {
            "id": self.id_incr,
            "method": "private/" + method,
            "api_key": self.api_key,
            "params": params,
            "nonce": time_now(),
        }

        logger.debug(json.dumps(req, indent=4))

        req["sig"] = self.__get_signature(req)

        headers = {"Content-Type": "application/json"}

        result = requests.post(f"{self.api_url}{method}", json=req, headers=headers)

        if result.status_code != 200:
            result.raise_for_status()

        self.write_request_to_file(
            f"{self.api_url}{method}", result.text, result.status_code
        )

        self.id_incr += 1

        logger.debug(result.text)

        data_dict = json.loads(result.text)["result"]

        # * data doesn't always exist even though it exists in about 90% of API calls.
        return data_dict["data"] if "data" in data_dict else data_dict
