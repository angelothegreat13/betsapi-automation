import requests

from typing import Dict, Any, Optional


class HttpHelper:
    def __init__(self, base_url: Optional[str] = None, headers: Dict[str, str] = {}):
        self._base_url = base_url
        self._headers = headers

    def set_base_url(self, base_url: str):
        self._base_url = base_url

    def get_base_url(self) -> str:
        return self._base_url

    def set_headers(self, headers: Dict[str, str]):
        self._headers.update(headers)

    def get_headers(self) -> Dict[str, str]:
        return self._headers

    def request(self, method: str, url: str, params: Dict[str, Any] = {}) -> requests.Response:
        if not self._base_url:
            raise ValueError("Base URL is not set.")

        full_url = self._base_url + url

        try:
            if method.lower() == "post":
                response = requests.post(full_url, data=params, headers=self._headers)
            elif method.lower() == "get":
                response = requests.get(full_url, params=params, headers=self._headers)
            elif method.lower() == "put":
                response = requests.put(full_url, data=params)
            elif method.lower() == "delete":
                response = requests.delete(full_url)
            else:
                raise ValueError("Invalid HTTP method. Only 'get' and 'post' are supported.")

            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Request failed: {e}")

        return response

    def get(self, url: str, params: Dict[str, Any] = {}) -> requests.Response:
        return self.request('get', url, params)

    def post(self, url: str, params: Dict[str, Any] = {}) -> requests.Response:
        return self.request('post', url, params)
