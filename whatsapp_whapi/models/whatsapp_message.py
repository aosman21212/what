# -*- coding: utf-8 -*-
import json
from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from ..services.message_service import MessageService
from ..services.media_service import MediaService


MESSAGE_TYPES = [
    ('text', 'Text'),
    ('image', 'Image'),
    ('video', 'Video'),
    ('short', 'Short Video'),
    ('gif', 'GIF'),
    ('audio', 'Audio'),
    ('voice', 'Voice'),
    ('document', 'Document'),
    ('link_preview', 'Link Preview'),
    ('location', 'Location'),
    ('live_location', 'Live Location'),
    ('contact', 'Contact'),
    ('contact_list', 'Contact List'),
    ('poll', 'Poll'),
    ('interactive', 'Interactive'),
    ('carousel', 'Carousel'),
    ('sticker', 'Sticker'),
    ('story', 'Story'),
    ('unknown', 'Unknown'),
]


class WhatsappMessage(models.Model):
    _name = 'whatsapp.message'
    _description = 'WhatsApp Message'
    _order = 'timestamp desc, id desc'

    channel_id = fields.Many2one('whatsapp.channel', required=True, ondelete='cascade', index=True)
    chat_ref_id = fields.Many2one('whatsapp.chat', ondelete='set null', string='Chat')
    chat_id = fields.Char(required=True, index=True)
    message_id = fields.Char(index=True)
    from_me = fields.Boolean()
    message_type = fields.Selection(MESSAGE_TYPES, default='text')
    body = fields.Text()
    timestamp = fields.Datetime()
    state = fields.Selection([
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
        ('failed', 'Failed'),
    ], default='pending')
    media_id = fields.Char()
    attachment_id = fields.Many2one('ir.attachment', ondelete='set null')
    from_name = fields.Char()
    raw_payload = fields.Text()
    latitude = fields.Float()
    longitude = fields.Float()
    poll_json = fields.Text()
    interactive_json = fields.Text()

    _sql_constraints = [
        ('message_channel_uniq', 'unique(channel_id, message_id)', 'Message ID must be unique per channel when set.'),
    ]

    @api.model
    def _extract_body(self, data):
        msg_type = data.get('type', 'text')
        if msg_type == 'text' and data.get('text'):
            return data['text'].get('body', '')
        if data.get('body'):
            return data['body']
        for key in ('image', 'video', 'document', 'audio', 'voice', 'sticker'):
            if data.get(key):
                part = data[key]
                if isinstance(part, dict):
                    return part.get('caption') or part.get('id') or ''
        return ''

    @api.model
    def _get_or_create_chat(self, channel, chat_id, data=None):
        chat = self.env['whatsapp.chat'].search([
            ('channel_id', '=', channel.id),
            ('chat_id', '=', chat_id),
        ], limit=1)
        if not chat:
            chat = self.env['whatsapp.chat'].create({
                'channel_id': channel.id,
                'chat_id': chat_id,
                'name': (data or {}).get('from_name') or chat_id.split('@')[0],
                'is_group': '@g.us' in chat_id,
            })
        return chat

    @api.model
    def _vals_from_api(self, channel, data):
        chat_id = data.get('chat_id') or data.get('chat', {}).get('id')
        if not chat_id:
            return None
        ts = data.get('timestamp')
        timestamp = False
        if ts:
            timestamp = datetime.utcfromtimestamp(int(ts))
        chat = self._get_or_create_chat(channel, chat_id, data)
        return {
            'channel_id': channel.id,
            'chat_ref_id': chat.id,
            'chat_id': chat_id,
            'message_id': data.get('id'),
            'from_me': data.get('from_me', False),
            'message_type': data.get('type', 'text') if data.get('type') in {t[0] for t in MESSAGE_TYPES} else 'unknown',
            'body': self._extract_body(data),
            'timestamp': timestamp,
            'from_name': data.get('from_name'),
            'media_id': self._extract_media_id(data),
            'raw_payload': json.dumps(data, default=str),
            'poll_json': json.dumps(data.get('poll')) if data.get('poll') else False,
            'interactive_json': json.dumps(data.get('interactive')) if data.get('interactive') else False,
        }

    @api.model
    def _extract_media_id(self, data):
        for key in ('image', 'video', 'document', 'audio', 'voice', 'sticker', 'gif'):
            part = data.get(key)
            if isinstance(part, dict):
                return part.get('id') or part.get('media_id')
            if isinstance(part, str):
                return part
        return data.get('media_id')

    @api.model
    def upsert_from_webhook(self, channel, data_list):
        for data in data_list:
            vals = self._vals_from_api(channel, data)
            if not vals or not vals.get('message_id'):
                continue
            existing = self.search([
                ('channel_id', '=', channel.id),
                ('message_id', '=', vals['message_id']),
            ], limit=1)
            if existing:
                existing.write(vals)
            else:
                self.create(vals)
            if vals.get('chat_ref_id'):
                self.env['whatsapp.chat'].browse(vals['chat_ref_id']).write({
                    'last_message_id': vals['message_id'],
                    'last_message_date': vals.get('timestamp'),
                })

    @api.model
    def update_statuses_from_webhook(self, channel, statuses):
        state_map = {
            'sent': 'sent',
            'delivered': 'delivered',
            'read': 'read',
            'played': 'read',
            'failed': 'failed',
        }
        for status in statuses:
            msg_id = status.get('id') or status.get('message_id')
            if not msg_id:
                continue
            msg = self.search([
                ('channel_id', '=', channel.id),
                ('message_id', '=', msg_id),
            ], limit=1)
            if msg:
                st = status.get('status') or status.get('state')
                msg.state = state_map.get(st, msg.state)

    def action_mark_read(self):
        for msg in self:
            if msg.message_id:
                MessageService(msg.channel_id).mark_read(msg.message_id)
                msg.state = 'read'

    def action_delete(self):
        for msg in self:
            if msg.message_id:
                MessageService(msg.channel_id).delete(msg.message_id)
            msg.unlink()

    def action_fetch_statuses(self):
        from ..services.status_service import StatusService
        for msg in self:
            if not msg.message_id:
                continue
            result = StatusService(msg.channel_id).get_message_statuses(msg.message_id)
            msg.raw_payload = json.dumps(result, indent=2, default=str)

    def action_send_reply(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Send Message'),
            'res_model': 'whatsapp.send.message',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_channel_id': self.channel_id.id,
                'default_to': self.chat_id,
                'default_message_type': 'text',
            },
        }

    @api.model
    def send_message(self, channel, to, message_type, body=None, media=None, attachment_id=None, **kwargs):
        svc = MessageService(channel)
        media_ref = media
        if attachment_id and not media_ref:
            attachment = self.env['ir.attachment'].browse(attachment_id)
            upload = MediaService(channel).upload_from_attachment(attachment)
            media_ref = upload.get('id') or upload.get('media', {}).get('id')
        dispatch = {
            'text': lambda: svc.send_text(to, body or '', **kwargs),
            'image': lambda: svc.send_image(to, media_ref, caption=body, **kwargs),
            'video': lambda: svc.send_video(to, media_ref, **kwargs),
            'document': lambda: svc.send_document(to, media_ref, **kwargs),
            'audio': lambda: svc.send_audio(to, media_ref, **kwargs),
            'voice': lambda: svc.send_voice(to, media_ref, **kwargs),
            'gif': lambda: svc.send_gif(to, media_ref, **kwargs),
            'sticker': lambda: svc.send_sticker(to, media_ref, **kwargs),
            'location': lambda: svc.send_location(to, kwargs.get('latitude'), kwargs.get('longitude'), **kwargs),
            'live_location': lambda: svc.send_live_location(to, kwargs.get('latitude'), kwargs.get('longitude'), **kwargs),
            'poll': lambda: svc.send_poll(to, kwargs.get('title', body), kwargs.get('options', []), **kwargs),
            'link_preview': lambda: svc.send_link_preview(to, body or '', **kwargs),
            'contact': lambda: svc.send_contact(to, kwargs.get('contact_id'), **kwargs),
            'interactive': lambda: svc.send_interactive(to, kwargs.get('interactive_payload', {})),
            'carousel': lambda: svc.send_carousel(to, kwargs.get('carousel_payload', {})),
        }
        if message_type not in dispatch:
            raise UserError(_('Unsupported message type: %s') % message_type)
        result = dispatch[message_type]()
        sent = result.get('message') or result
        if isinstance(sent, dict):
            self.upsert_from_webhook(channel, [sent])
        elif result.get('messages'):
            self.upsert_from_webhook(channel, result['messages'])
        return result

    @api.model
    def get_inbox_data(self, channel_id, chat_id=None, limit=50):
        channel = self.env['whatsapp.channel'].browse(channel_id)
        domain = [('channel_id', '=', channel_id)]
        if chat_id:
            domain.append(('chat_id', '=', chat_id))
        messages = self.search(domain, limit=limit, order='timestamp asc, id asc')
        chats = self.env['whatsapp.chat'].search([
            ('channel_id', '=', channel_id),
        ], order='last_message_date desc, name')
        return {
            'channel': {'id': channel.id, 'name': channel.name, 'state': channel.state},
            'chats': [{
                'id': c.id,
                'chat_id': c.chat_id,
                'name': c.name,
                'unread_count': c.unread_count,
                'last_message_date': c.last_message_date.isoformat() if c.last_message_date else False,
            } for c in chats],
            'messages': [{
                'id': m.id,
                'chat_id': m.chat_id,
                'body': m.body,
                'from_me': m.from_me,
                'message_type': m.message_type,
                'timestamp': m.timestamp.isoformat() if m.timestamp else False,
                'from_name': m.from_name,
                'state': m.state,
            } for m in messages],
        }
