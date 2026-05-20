# -*- coding: utf-8 -*-
from odoo import fields, models


class WhatsappApiLog(models.Model):
    _name = 'whatsapp.api.log'
    _description = 'WhatsApp API Log'
    _order = 'create_date desc'

    channel_id = fields.Many2one('whatsapp.channel', required=True, ondelete='cascade')
    method = fields.Char(required=True)
    path = fields.Char(required=True)
    status_code = fields.Integer()
    request_body = fields.Text()
    response_body = fields.Text()
