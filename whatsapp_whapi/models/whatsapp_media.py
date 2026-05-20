# -*- coding: utf-8 -*-
import json

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from ..services.media_service import MediaService


class WhatsappMedia(models.Model):
    _name = 'whatsapp.media'
    _description = 'WhatsApp Media'
    _order = 'create_date desc'

    channel_id = fields.Many2one('whatsapp.channel', required=True, ondelete='cascade')
    media_id = fields.Char(index=True)
    filename = fields.Char()
    mimetype = fields.Char()
    attachment_id = fields.Many2one('ir.attachment', ondelete='set null')
    raw_data = fields.Text()

    def action_upload(self):
        for rec in self:
            if not rec.attachment_id:
                raise UserError(_('Please attach a file first.'))
            result = MediaService(rec.channel_id).upload_from_attachment(rec.attachment_id)
            rec.media_id = result.get('id') or result.get('media', {}).get('id')
            rec.raw_data = json.dumps(result, default=str)

    @api.model
    def sync_from_api(self, channel):
        result = MediaService(channel).list_media()
        items = result.get('media') or result.get('data') or []
        for item in items:
            mid = item.get('id')
            if not mid:
                continue
            existing = self.search([
                ('channel_id', '=', channel.id),
                ('media_id', '=', mid),
            ], limit=1)
            vals = {
                'channel_id': channel.id,
                'media_id': mid,
                'filename': item.get('filename'),
                'mimetype': item.get('mimetype'),
                'raw_data': json.dumps(item, default=str),
            }
            if existing:
                existing.write(vals)
            else:
                self.create(vals)
