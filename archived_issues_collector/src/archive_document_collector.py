

import httpx

from base64_decode import base64_decode_str


class ArchiveDocumentCollector():
    def __init__(self, token: str | None = None):
        self.__http_client = httpx.Client()
        self.__token_header = self.__make_token_header(token)

    def __make_token_header(self, token: str | None) -> dict[str, str]:
        if token is None:
            return {}
        return {
            "Authorization": f"Bearer  {token}"
        }

    def collect_document(
        self,
        url: str,
        json_api: bool,
        content_key: str,
        base64_decode: bool,
        use_token: bool,
        http_headers: dict[str, str],

    ) -> str:
        result = ""

        if use_token:
            http_headers.update(self.__token_header)

        response = self.__http_client.get(
            url, headers=http_headers
        )

        if json_api:
            if content_key.strip():
                result = response.json()[content_key]
            else:
                result = response.json()
        else:
            result = response.text

        if base64_decode:
            result = base64_decode_str(result)

        return result
