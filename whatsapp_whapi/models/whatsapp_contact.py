# -*- coding: utf-8 -*-
import json

from odoo import api, fields, models

from ..services.contact_service import ContactService


class WhatsappContact(models.Model):
    _name = 'whatsapp.contact'
    _description = 'WhatsApp Contact'
    _order = 'name, phone'

    channel_id = fields.Many2one('whatsapp.channel', required=True, ondelete='cascade', index=True)
    contact_id = fields.Char(required=True, index=True)
    phone = fields.Char(index=True)
    name = fields.Char()
    exists_on_wa = fields.Boolean()
    lid = fields.Char()
    partner_ref = fields.Char(string='External Reference')
    raw_data = fields.Text()

    _sql_constraints = [
        ('contact_channel_uniq', 'unique(channel_id, contact_id)', 'Contact must be unique per channel.'),
    ]

    @api.model
    def _vals_from_api(self, channel, data):
        contact_id = data.get('id') or data.get('contact_id')
        if not contact_id:
            return None
        phone = data.get('phone') or contact_id.split('@')[0]
        return {
            'channel_id': channel.id,
            'contact_id': contact_id,
            'phone': phone,
            'name': data.get('name') or data.get('pushname') or phone,
            'exists_on_wa': data.get('exists', True),
            'lid': data.get('lid'),
            'raw_data': json.dumps(data, default=str),
        }

    @api.model
    def upsert_from_api(self, channel, data_list):
        for data in data_list:
            vals = self._vals_from_api(channel, data)
            if not vals:
                continue
            existing = self.search([
                ('channel_id', '=', channel.id),
                ('contact_id', '=', vals['contact_id']),
            ], limit=1)
            if existing:
                existing.write(vals)
            else:
                self.create(vals)

    @api.model
    def upsert_from_webhook(self, channel, data_list):
        self.upsert_from_api(channel, data_list)

    @api.model
    def sync_from_api(self, channel, count=500):
        result = ContactService(channel).list_contacts(count=count)
        contacts = result.get('contacts') or result.get('data') or []
        if isinstance(result, list):
            contacts = result
        self.upsert_from_api(channel, contacts)

    def action_check_exists(self):
        for contact in self:
            try:
                ContactService(contact.channel_id).exists(contact.contact_id)
                contact.exists_on_wa = True
            except Exception:
                contact.exists_on_wa = False
