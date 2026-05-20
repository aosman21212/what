# -*- coding: utf-8 -*-
import json

from odoo import fields, models

from ..services.business_service import BusinessService


class WhatsappOrder(models.Model):
    _name = 'whatsapp.order'
    _description = 'WhatsApp Business Order'
    _order = 'create_date desc'

    channel_id = fields.Many2one('whatsapp.channel', required=True, ondelete='cascade')
    order_id = fields.Char(required=True, index=True)
    chat_id = fields.Char()
    items_json = fields.Text()
    raw_data = fields.Text()

    _sql_constraints = [
        ('order_channel_uniq', 'unique(channel_id, order_id)', 'Order must be unique per channel.'),
    ]

    def action_fetch_items(self):
        for order in self:
            result = BusinessService(order.channel_id).get_order(order.order_id)
            order.items_json = json.dumps(result.get('items') or result, indent=2, default=str)
            order.raw_data = json.dumps(result, indent=2, default=str)
