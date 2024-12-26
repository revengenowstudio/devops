import pytest
from unittest.mock import patch, MagicMock
from http import HTTPStatus

import httpx

from src.http_request import http_request


class TestHttpRequest():

    @patch('httpx.request')
    def test_successful_request(self, mock_request):
        # 模拟成功的 HTTP 请求
        mock_response = MagicMock()
        mock_response.status_code = HTTPStatus.OK  # 200
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        response = http_request(
            headers={'Content-Type': 'application/json'},
            url='https://example.com/api',
            method='GET'
        )

        # 验证请求成功返回
        assert response == mock_response
        mock_request.assert_called_once_with(
            headers={'Content-Type': 'application/json'},
            method='GET',
            url='https://example.com/api',
            params=None,
            json=None,
            follow_redirects=True
        )

    @patch('httpx.request')
    def test_404_not_found(self, mock_request):
        # 模拟 404 Not Found 错误
        error_message = "Not Found"
        mock_response = MagicMock()
        mock_response.status_code = HTTPStatus.NOT_FOUND  # 404
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            error_message, request=MagicMock(), response=mock_response)
        mock_request.return_value = mock_response

        with pytest.raises(httpx.HTTPStatusError) as context:
            http_request(
                headers={'Content-Type': 'application/json'},
                url='https://example.com/api',
                method='GET'
            )

        # 验证日志输出
        context.match(error_message)

    @patch('httpx.request')
    def test_http_status_error(self, mock_request):
        # 模拟其他 HTTP 错误
        error_message = "Bad Request"
        mock_response = MagicMock()
        mock_response.status_code = HTTPStatus.BAD_REQUEST  # 400
        mock_response.json.return_value = {'error': error_message}
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Bad Request", request=MagicMock(), response=mock_response)
        mock_request.return_value = mock_response

        with pytest.raises(httpx.HTTPStatusError,
                           match=error_message) as context:
            http_request(
                headers={'Content-Type': 'application/json'},
                url='https://example.com/api',
                method='GET'
            )

        # 验证日志输出
        context.match(error_message)

    @patch('httpx.request')
    def test_retry_on_exception(self, mock_request):
        # 模拟未知异常并测试重试机制
        mock_request.side_effect = [Exception("Network error"), Exception(
            "Network error"), MagicMock(status_code=HTTPStatus.OK)]

        response = http_request(
            headers={'Content-Type': 'application/json'},
            url='https://example.com/api',
            method='GET',
            retry_times=3
        )

        # 验证请求被重试了 3 次
        assert mock_request.call_count == 3
        assert response.status_code == HTTPStatus.OK

    @patch('httpx.request')
    def test_max_retries_exceeded(self, mock_request):
        # 模拟未知异常并测试重试次数用完后抛出异常
        error_message = "Network error"
        mock_request.side_effect = [Exception(error_message)] * 3

        with pytest.raises(Exception,
                           match=error_message):
            http_request(
                headers={'Content-Type': 'application/json'},
                url='https://example.com/api',
                method='GET',
                retry_times=3
            )

        # 验证抛出的异常是最后一次引发的异常
        assert mock_request.call_count == 3
