# -*- coding: utf-8 -*-
import json

from odoo import api, fields, models

from ..services.chat_service import ChatService


class WhatsappChat(models.Model):
    _name = 'whatsapp.chat'
    _description = 'WhatsApp Chat'
    _order = 'last_message_date desc, name'

    channel_id = fields.Many2one('whatsapp.channel', required=True, ondelete='cascade', index=True)
    chat_id = fields.Char(required=True, index=True)
    name = fields.Char()
    is_group = fields.Boolean(default=False)
    archived = fields.Boolean()
    pinned = fields.Boolean()
    muted = fields.Boolean()
    unread_count = fields.Integer()
    last_message_id = fields.Char()
    last_message_date = fields.Datetime()
    raw_data = fields.Text()
    message_ids = fields.One2many('whatsapp.message', 'chat_ref_id')
    message_count = fields.Integer(compute='_compute_message_count')

    _sql_constraints = [
        ('chat_channel_uniq', 'unique(channel_id, chat_id)', 'Chat must be unique per channel.'),
    ]

    @api.depends('message_ids')
    def _compute_message_count(self):
        for rec in self:
            rec.message_count = len(rec.message_ids)

    @api.model
    def _vals_from_api(self, channel, data):
        chat_id = data.get('id') or data.get('chat_id')
        if not chat_id:
            return None
        return {
            'channel_id': channel.id,
            'chat_id': chat_id,
            'name': data.get('name') or data.get('title') or chat_id.split('@')[0],
            'is_group': '@g.us' in chat_id or data.get('type') == 'group',
            'archived': data.get('archive') or data.get('archived'),
            'pinned': data.get('pin') or data.get('pinned'),
            'muted': data.get('mute') or data.get('muted'),
            'unread_count': data.get('unread') or data.get('unread_count') or 0,
            'last_message_id': data.get('last_message', {}).get('id') if isinstance(data.get('last_message'), dict) else data.get('last_message_id'),
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
                ('chat_id', '=', vals['chat_id']),
            ], limit=1)
            if existing:
                existing.write(vals)
            else:
                self.create(vals)

    @api.model
    def upsert_from_webhook(self, channel, data_list):
        self.upsert_from_api(channel, data_list)

    @api.model
    def sync_from_api(self, channel, count=100):
        result = ChatService(channel).list_chats(count=count)
        chats = result.get('chats') or result.get('data') or result if isinstance(result, list) else []
        if isinstance(result, dict) and not chats:
            chats = result.get('chats', [])
        self.upsert_from_api(channel, chats)
        return True

    def action_archive(self):
        for chat in self:
            ChatService(chat.channel_id).archive_chat(chat.chat_id, True)
            chat.archived = True

    def action_unarchive(self):
        for chat in self:
            ChatService(chat.channel_id).archive_chat(chat.chat_id, False)
            chat.archived = False

    def action_mark_read(self):
        for chat in self:
            ChatService(chat.channel_id).update_settings(chat.chat_id, {'mark_read': True})
            chat.unread_count = 0

    def action_open_inbox(self):
        self.ensure_one()
        return self.channel_id.action_open_inbox()
