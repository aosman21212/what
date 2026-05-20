# -*- coding: utf-8 -*-
import json

from odoo import api, fields, models

from ..services.business_service import BusinessService


class WhatsappProduct(models.Model):
    _name = 'whatsapp.product'
    _description = 'WhatsApp Business Product'
    _order = 'name'

    channel_id = fields.Many2one('whatsapp.channel', required=True, ondelete='cascade', index=True)
    product_id = fields.Char(required=True, index=True)
    name = fields.Char()
    description = fields.Text()
    price = fields.Float()
    currency = fields.Char()
    image_url = fields.Char()
    raw_data = fields.Text()
    collection_id = fields.Many2one('whatsapp.collection', ondelete='set null')

    _sql_constraints = [
        ('product_channel_uniq', 'unique(channel_id, product_id)', 'Product must be unique per channel.'),
    ]

    @api.model
    def sync_from_api(self, channel):
        result = BusinessService(channel).list_products()
        items = result.get('products') or result.get('data') or []
        if isinstance(result, list):
            items = result
        for item in items:
            pid = item.get('id')
            if not pid:
                continue
            vals = {
                'channel_id': channel.id,
                'product_id': pid,
                'name': item.get('name'),
                'description': item.get('description'),
                'price': item.get('price'),
                'currency': item.get('currency'),
                'image_url': item.get('image_url') or (item.get('image') or {}).get('url') if isinstance(item.get('image'), dict) else item.get('image'),
                'raw_data': json.dumps(item, default=str),
            }
            existing = self.search([
                ('channel_id', '=', channel.id),
                ('product_id', '=', pid),
            ], limit=1)
            if existing:
                existing.write(vals)
            else:
                self.create(vals)

    def action_send_product(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Send Product',
            'res_model': 'whatsapp.send.message',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_channel_id': self.channel_id.id,
                'default_message_type': 'text',
            },
        }
