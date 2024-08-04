from dataclasses import dataclass
import hashlib
import hmac
import json
import logging
import time
from typing import Dict
import requests

logger = logging.getLogger("client")


@dataclass
class HttpClient:
    api_url: str
    id_incr: int

    def get(self, method: str):
        response = requests.get(f"{self.api_url}{method}")

        if response.status_code != 200:
            message = f"The following query did not succeed: ({self.api_url}{method})"

            logger.fatal(message, response.text)

            raise ValueError(message)

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
            "nonce": int(time.time() * 1000),
        }

        logger.debug(json.dumps(req, indent=4))

        req["sig"] = self.__get_signature(req)

        headers = {"Content-Type": "application/json"}

        result = requests.post(f"{self.api_url}{method}", json=req, headers=headers)

        if result.status_code != 200:
            raise ValueError(result.text)

        self.id_incr += 1

        logger.info(result.text)

        data_dict = json.loads(result.text)["result"]

        # * data doesn't always exist even though it exists in about 90% of API calls.
        return data_dict["data"] if "data" in data_dict else data_dict
