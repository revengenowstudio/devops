import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.archive_document_collector import ArchiveDocumentCollector


class TestArchiveDocumentCollector:
    @patch("httpx.request")
    def test_collect_document(self, mock_http_request: MagicMock, tmpdir: Path):
        test_content_key = "test_content_key"
        test_doc_content = "test_data\n"
        test_doc_json_content = {test_content_key: "test_json_data\n"}
        test_url = "https://test_url"
        test_token = "test_token"
        test_http_headers = {"test_header": "test_value"}

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = test_doc_json_content
        mock_response.text = test_doc_content
        mock_http_request.return_value = mock_response

        collector = ArchiveDocumentCollector(test_token)
        result = collector.collect_document(
            url=test_url,
            content_key=test_content_key,
            http_headers=test_http_headers,
            json_api=False,
            base64_decode=False,
            use_token=False,
        )
        assert result == test_doc_content

        result = collector.collect_document(
            url=test_url,
            content_key=test_content_key,
            http_headers=test_http_headers,
            json_api=False,
            base64_decode=False,
            use_token=True,
        )
        expected_header = test_http_headers.copy()
        expected_header.update({"Authorization": f"Bearer {test_token}"})
        assert mock_http_request.call_args.kwargs["headers"] == expected_header
        assert result == test_doc_content

        result = collector.collect_document(
            url=test_url,
            content_key=test_content_key,
            http_headers=test_http_headers,
            json_api=False,
            base64_decode=False,
            use_token=True,
        )
        expected_header = test_http_headers.copy()
        expected_header.update({"Authorization": f"Bearer {test_token}"})
        assert mock_http_request.call_args.kwargs["headers"] == expected_header
        assert result == test_doc_content

        result = collector.collect_document(
            url=test_url,
            content_key=test_content_key,
            http_headers=test_http_headers,
            json_api=True,
            base64_decode=False,
            use_token=False,
        )
        assert result == test_doc_json_content[test_content_key]

        from base64 import b64encode

        mock_response.text = b64encode(test_doc_content.encode())
        result = collector.collect_document(
            url=test_url,
            content_key=test_content_key,
            http_headers=test_http_headers,
            json_api=False,
            base64_decode=True,
            use_token=False,
        )
        assert result == test_doc_content

        test_doc_content = "test\ntest\n\n"
        tmp_file = tmpdir / "test_file.txt"
        tmp_file.write_text(test_doc_content, encoding="utf-8")
        test_url = f"file://{str(tmp_file)}"
        result = collector.collect_document(
            url=test_url,
            content_key=test_content_key,
            http_headers=test_http_headers,
            json_api=False,
            base64_decode=False,
            use_token=False,
        )
        assert result == test_doc_content
