# -*- coding: utf-8 -*-
import json

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class WhatsappSendMessage(models.TransientModel):
    _name = 'whatsapp.send.message'
    _description = 'Send WhatsApp Message'

    channel_id = fields.Many2one('whatsapp.channel', required=True)
    to = fields.Char(required=True, string='Chat ID / Phone')
    message_type = fields.Selection([
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('document', 'Document'),
        ('audio', 'Audio'),
        ('voice', 'Voice'),
        ('gif', 'GIF'),
        ('sticker', 'Sticker'),
        ('location', 'Location'),
        ('live_location', 'Live Location'),
        ('poll', 'Poll'),
        ('link_preview', 'Link Preview'),
        ('contact', 'Contact'),
        ('interactive', 'Interactive'),
        ('carousel', 'Carousel'),
    ], default='text', required=True)
    body = fields.Text(string='Message / Caption')
    attachment_id = fields.Many2one('ir.attachment', string='Media File')
    media_url = fields.Char(string='Media URL or ID')
    latitude = fields.Float()
    longitude = fields.Float()
    poll_title = fields.Char()
    poll_options = fields.Text(help='One option per line')
    contact_id = fields.Char(string='Contact ID to send')
    interactive_json = fields.Text(string='Interactive JSON')
    carousel_json = fields.Text(string='Carousel JSON')
    product_id = fields.Many2one('whatsapp.product')

    def _normalize_to(self, phone):
        to = (self.to or '').strip()
        if '@' in to:
            return to
        digits = ''.join(c for c in to if c.isdigit())
        if not digits:
            raise UserError(_('Invalid recipient.'))
        return f'{digits}@s.whatsapp.net'

    def action_send(self):
        self.ensure_one()
        to = self._normalize_to(self.to)
        kwargs = {}
        media = self.media_url
        if self.message_type == 'poll':
            options = [o.strip() for o in (self.poll_options or '').splitlines() if o.strip()]
            if not options:
                raise UserError(_('Poll requires at least one option.'))
            kwargs['title'] = self.poll_title or self.body
            kwargs['options'] = options
        elif self.message_type == 'location':
            kwargs['latitude'] = self.latitude
            kwargs['longitude'] = self.longitude
        elif self.message_type == 'live_location':
            kwargs['latitude'] = self.latitude
            kwargs['longitude'] = self.longitude
        elif self.message_type == 'contact':
            kwargs['contact_id'] = self.contact_id
        elif self.message_type == 'interactive':
            kwargs['interactive_payload'] = json.loads(self.interactive_json or '{}')
        elif self.message_type == 'carousel':
            kwargs['carousel_payload'] = json.loads(self.carousel_json or '{}')

        if self.product_id:
            from ..services.business_service import BusinessService
            BusinessService(self.channel_id).send_product(self.product_id.product_id, to)
            return {'type': 'ir.actions.act_window_close'}

        self.env['whatsapp.message'].send_message(
            self.channel_id,
            to,
            self.message_type,
            body=self.body,
            media=media,
            attachment_id=self.attachment_id.id if self.attachment_id else None,
            **kwargs,
        )
        return {'type': 'ir.actions.act_window_close'}
