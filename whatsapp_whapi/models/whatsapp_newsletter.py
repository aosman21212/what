# -*- coding: utf-8 -*-
import json

from odoo import api, fields, models

from ..services.newsletter_service import NewsletterService


class WhatsappNewsletter(models.Model):
    _name = 'whatsapp.newsletter'
    _description = 'WhatsApp Newsletter / Channel'
    _order = 'name'

    channel_id = fields.Many2one('whatsapp.channel', required=True, ondelete='cascade', index=True)
    newsletter_id = fields.Char(required=True, index=True)
    name = fields.Char()
    description = fields.Text()
    subscribers_count = fields.Integer()
    raw_data = fields.Text()

    _sql_constraints = [
        ('newsletter_channel_uniq', 'unique(channel_id, newsletter_id)', 'Newsletter must be unique per channel.'),
    ]

    @api.model
    def sync_from_api(self, channel):
        result = NewsletterService(channel).list_newsletters()
        items = result.get('newsletters') or result.get('data') or []
        if isinstance(result, list):
            items = result
        for item in items:
            nid = item.get('id')
            if not nid:
                continue
            vals = {
                'channel_id': channel.id,
                'newsletter_id': nid,
                'name': item.get('name') or item.get('title'),
                'description': item.get('description'),
                'subscribers_count': item.get('subscribers_count') or item.get('followers'),
                'raw_data': json.dumps(item, default=str),
            }
            existing = self.search([
                ('channel_id', '=', channel.id),
                ('newsletter_id', '=', nid),
            ], limit=1)
            if existing:
                existing.write(vals)
            else:
                self.create(vals)

    def action_subscribe(self):
        for rec in self:
            NewsletterService(rec.channel_id).subscribe(rec.newsletter_id)

    def action_unsubscribe(self):
        for rec in self:
            NewsletterService(rec.channel_id).unsubscribe(rec.newsletter_id)
