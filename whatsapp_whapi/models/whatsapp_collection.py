# -*- coding: utf-8 -*-
import json

from odoo import api, fields, models

from ..services.business_service import BusinessService


class WhatsappCollection(models.Model):
    _name = 'whatsapp.collection'
    _description = 'WhatsApp Business Collection'
    _order = 'name'

    channel_id = fields.Many2one('whatsapp.channel', required=True, ondelete='cascade', index=True)
    collection_id = fields.Char(required=True, index=True)
    name = fields.Char()
    product_ids = fields.One2many('whatsapp.product', 'collection_id')
    raw_data = fields.Text()

    _sql_constraints = [
        ('collection_channel_uniq', 'unique(channel_id, collection_id)', 'Collection must be unique per channel.'),
    ]

    @api.model
    def sync_from_api(self, channel):
        result = BusinessService(channel).list_collections()
        items = result.get('collections') or result.get('data') or []
        if isinstance(result, list):
            items = result
        for item in items:
            cid = item.get('id')
            if not cid:
                continue
            vals = {
                'channel_id': channel.id,
                'collection_id': cid,
                'name': item.get('name'),
                'raw_data': json.dumps(item, default=str),
            }
            existing = self.search([
                ('channel_id', '=', channel.id),
                ('collection_id', '=', cid),
            ], limit=1)
            if existing:
                existing.write(vals)
            else:
                self.create(vals)
