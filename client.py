import requests
from enum import Enum


class RequestError(Exception):
    def __init__(self, status_code, error_code, error_message, error_id):
        self.status_code = status_code
        self.error_code = error_code
        self.error_message = error_message
        self.error_id = error_id
        super(RequestError, self).__init__(error_message)


class Client(object):
    DEFAULT_ENDPOINT = 'https://analytics.adobe.io/api/'

    def __init__(self, api_key, company_id, token, endpoint=DEFAULT_ENDPOINT):
        self._api_key = api_key
        self._company_id = company_id
        self._token = token
        self._endpoint = '{}{}'.format(endpoint, company_id)
        self._auth_headers = self._compose_auth_headers()
        self._methods = {Request.Method.GET: requests.get, Request.Method.POST: requests.post}

    def execute(self, request):
        headers = request.headers.copy()
        headers.update(self._auth_headers)
        url = '{}{}'.format(self._endpoint, request.resource)

        raw_response = self._methods[request.method](url, headers=headers, json=request.payload)
        response = raw_response.json()

        if 'errorCode' in response:
            raise RequestError(raw_response.status_code,
                               response['errorCode'],
                               response['errorDescription'],
                               response['errorId'])

        return response

    def _compose_auth_headers(self):
        return {
            'x-api-key': self._api_key,
            'x-proxy-global-company-id': self._company_id,
            'Authorization': 'Bearer {}'.format(self._token)}

    def __str__(self):
        return """
        \033[1m{:<10s}\033[0m{:>15s}
        \033[1m{:<10s}\033[0m{:>10s}
        \033[1m{:<10s}\033[0m{:>10s}
        \033[1m{:<10s}\033[0m{:>10s}
        """.format('API Key:', self._api_key, 'Token:', self._token, 'Company Id:', self._company_id,
                   'Endpoint:', self._endpoint)


class Request(object):
    Method = Enum('Method', 'GET POST')

    def __init__(self, method, resource, headers=None, payload=None):
        self._method = method
        self._resource = resource

        self._headers = {}
        if headers:
            assert isinstance(headers, dict)
            self._headers = headers

        self._payload = {}
        if payload:
            assert isinstance(payload, dict)
            self._payload = payload

    @property
    def method(self):
        return self._method

    @property
    def resource(self):
        return self._resource

    @property
    def headers(self):
        return self._headers

    @property
    def payload(self):
        return self._payload

    def __str__(self):
        return """
                \033[1m{:<10s}\033[0m{:>15s}
                \033[1m{:<10s}\033[0m{:>10s}
                \033[1m{:<10s}\033[0m{:>10s}
                \033[1m{:<10s}\033[0m{:>10s}
                """.format('Method:', self._method, 'Resource:', self._resource, 'Headers:', self._headers,
                           'Payload:', self._payload)
