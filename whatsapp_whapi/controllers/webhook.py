# -*- coding: utf-8 -*-
import json
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class WhatsappWebhookController(http.Controller):

    @http.route(
        '/whatsapp/whapi/webhook/<string:webhook_secret>',
        type='http',
        auth='public',
        methods=['POST'],
        csrf=False,
    )
    def whapi_webhook(self, webhook_secret, **kwargs):
        channel = request.env['whatsapp.channel'].sudo().search([
            ('webhook_secret', '=', webhook_secret),
            ('active', '=', True),
        ], limit=1)
        if not channel:
            _logger.warning('Whapi webhook: unknown secret %s', webhook_secret)
            return request.make_response('Not found', status=404)

        try:
            body = request.httprequest.get_data(as_text=True)
            payload = json.loads(body) if body else {}
        except json.JSONDecodeError:
            _logger.exception('Whapi webhook: invalid JSON')
            return request.make_response('Bad request', status=400)

        try:
            channel._process_webhook_payload(payload)
        except Exception:
            _logger.exception('Whapi webhook processing failed for channel %s', channel.id)

        return request.make_response(json.dumps({'status': 'ok'}), headers=[
            ('Content-Type', 'application/json'),
        ])
