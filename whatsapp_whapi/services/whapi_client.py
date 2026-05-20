# -*- coding: utf-8 -*-
import json
import logging

import requests

from odoo import _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = 'https://gate.whapi.cloud'


class WhapiClient:
    """HTTP gateway for Whapi.Cloud REST API."""

    def __init__(self, channel):
        self.channel = channel
        self.base_url = (channel.api_base_url or DEFAULT_BASE_URL).rstrip('/')
        self.token = channel.api_token
        self.env = channel.env
        self.timeout = 60

    def _headers(self, extra=None):
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.token}',
        }
        if extra:
            headers.update(extra)
        return headers

    def _log_request(self, method, path, status_code, request_body=None, response_body=None):
        if not self.channel:
            return
        try:
            self.env['whatsapp.api.log'].sudo().create({
                'channel_id': self.channel.id,
                'method': method,
                'path': path,
                'status_code': status_code,
                'request_body': request_body[:5000] if request_body else False,
                'response_body': response_body[:5000] if response_body else False,
            })
        except Exception:
            _logger.exception('Failed to log Whapi request')

    def _parse_error(self, response):
        try:
            data = response.json()
            if isinstance(data, dict):
                return data.get('error') or data.get('message') or json.dumps(data)
        except Exception:
            pass
        return response.text or _('Whapi API error (%s)') % response.status_code

    def request(self, method, path, params=None, json_data=None, data=None, files=None, content_type='application/json'):
        url = f'{self.base_url}{path}'
        headers = self._headers()
        if files:
            headers.pop('Content-Type', None)
        elif content_type and json_data is not None:
            headers['Content-Type'] = content_type

        req_body = None
        if json_data is not None:
            req_body = json.dumps(json_data, default=str)
        elif data is not None:
            req_body = str(data)

        try:
            response = requests.request(
                method=method.upper(),
                url=url,
                headers=headers,
                params=params,
                json=json_data if json_data is not None and not files else None,
                data=data if not files else None,
                files=files,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            self._log_request(method, path, 0, req_body, str(exc))
            raise UserError(_('Whapi connection failed: %s') % exc) from exc

        resp_text = response.text
        self._log_request(method, path, response.status_code, req_body, resp_text)

        if response.status_code >= 400:
            raise UserError(self._parse_error(response))

        if not resp_text or response.status_code == 204:
            return {}
        try:
            return response.json()
        except json.JSONDecodeError:
            return {'raw': resp_text}

    def get(self, path, params=None):
        return self.request('GET', path, params=params)

    def post(self, path, json_data=None, data=None, files=None):
        return self.request('POST', path, json_data=json_data, data=data, files=files)

    def put(self, path, json_data=None):
        return self.request('PUT', path, json_data=json_data)

    def patch(self, path, json_data=None):
        return self.request('PATCH', path, json_data=json_data)

    def delete(self, path, json_data=None):
        return self.request('DELETE', path, json_data=json_data)

    def head(self, path):
        return self.request('HEAD', path)
