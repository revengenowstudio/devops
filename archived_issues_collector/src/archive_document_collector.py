from pathlib import Path

from base64_decode import base64_decode_str

from http_request import http_request


class ArchiveDocumentCollector:
    def __init__(self, token: str | None = None):
        self.__token_header = self.__make_token_header(token)

    def __make_token_header(self, token: str | None) -> dict[str, str]:
        if token is None:
            return {}
        return {"Authorization": f"Bearer {token}"}

    def collect_document(
        self,
        url: str,
        content_key: str,
        http_headers: dict[str, str],
        json_api: bool,
        base64_decode: bool,
        use_token: bool,
    ) -> str:
        result = ""

        if url.startswith("file://"):
            return Path(url[7:]).read_text(encoding="utf-8")

        new_headers = http_headers.copy()
        if use_token:
            new_headers.update(self.__token_header)

        response = http_request(url=url, method="GET", headers=new_headers)

        if json_api:
            result = response.json()[content_key]
        else:
            result = response.text

        if base64_decode:
            result = base64_decode_str(result)

        return result
