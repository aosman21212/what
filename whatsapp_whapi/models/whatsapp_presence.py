# -*- coding: utf-8 -*-
import json

from odoo import api, fields, models


class WhatsappPresence(models.Model):
    _name = 'whatsapp.presence'
    _description = 'WhatsApp Presence'
    _order = 'write_date desc'

    channel_id = fields.Many2one('whatsapp.channel', required=True, ondelete='cascade', index=True)
    entry_id = fields.Char(required=True, index=True)
    online = fields.Boolean()
    typing = fields.Boolean()
    recording = fields.Boolean()
    last_seen = fields.Datetime()
    raw_data = fields.Text()

    _sql_constraints = [
        ('presence_channel_uniq', 'unique(channel_id, entry_id)', 'Presence must be unique per channel.'),
    ]

    @api.model
    def upsert_from_webhook(self, channel, data_list):
        for data in data_list:
            entry_id = data.get('id') or data.get('entry_id') or data.get('from')
            if not entry_id:
                continue
            vals = {
                'channel_id': channel.id,
                'entry_id': entry_id,
                'online': data.get('online'),
                'typing': data.get('typing'),
                'recording': data.get('recording'),
                'raw_data': json.dumps(data, default=str),
            }
            existing = self.search([
                ('channel_id', '=', channel.id),
                ('entry_id', '=', entry_id),
            ], limit=1)
            if existing:
                existing.write(vals)
            else:
                self.create(vals)
