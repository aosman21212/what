# -*- coding: utf-8 -*-
import json

from odoo import api, fields, models

from ..services.group_service import GroupService


class WhatsappGroup(models.Model):
    _name = 'whatsapp.group'
    _description = 'WhatsApp Group'
    _order = 'name'

    channel_id = fields.Many2one('whatsapp.channel', required=True, ondelete='cascade', index=True)
    group_id = fields.Char(required=True, index=True)
    name = fields.Char()
    description = fields.Text()
    invite_code = fields.Char()
    participant_count = fields.Integer()
    raw_data = fields.Text()
    participant_ids = fields.One2many('whatsapp.group.participant', 'group_id')

    _sql_constraints = [
        ('group_channel_uniq', 'unique(channel_id, group_id)', 'Group must be unique per channel.'),
    ]

    @api.model
    def _vals_from_api(self, channel, data):
        group_id = data.get('id') or data.get('group_id')
        if not group_id:
            return None
        participants = data.get('participants') or []
        return {
            'channel_id': channel.id,
            'group_id': group_id,
            'name': data.get('name') or data.get('subject'),
            'description': data.get('description'),
            'invite_code': data.get('invite_code'),
            'participant_count': len(participants) if participants else data.get('size', 0),
            'raw_data': json.dumps(data, default=str),
        }

    @api.model
    def upsert_from_api(self, channel, data_list):
        for data in data_list:
            vals = self._vals_from_api(channel, data)
            if not vals:
                continue
            participants_data = data.get('participants') or []
            existing = self.search([
                ('channel_id', '=', channel.id),
                ('group_id', '=', vals['group_id']),
            ], limit=1)
            if existing:
                existing.write(vals)
                group = existing
            else:
                group = self.create(vals)
            if participants_data:
                group.participant_ids.unlink()
                for p in participants_data:
                    pid = p if isinstance(p, str) else p.get('id') or p.get('participant')
                    self.env['whatsapp.group.participant'].create({
                        'group_id': group.id,
                        'participant_id': pid,
                        'is_admin': p.get('admin') if isinstance(p, dict) else False,
                    })

    @api.model
    def upsert_from_webhook(self, channel, data_list):
        self.upsert_from_api(channel, data_list)

    @api.model
    def sync_from_api(self, channel):
        result = GroupService(channel).list_groups()
        groups = result.get('groups') or result.get('data') or []
        if isinstance(result, list):
            groups = result
        self.upsert_from_api(channel, groups)

    def action_leave(self):
        for group in self:
            GroupService(group.channel_id).leave(group.group_id)
            group.unlink()

    def action_refresh(self):
        for group in self:
            data = GroupService(group.channel_id).get(group.group_id)
            self.upsert_from_api(group.channel_id, [data.get('group') or data])
