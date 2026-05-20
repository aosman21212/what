# -*- coding: utf-8 -*-
import json
import uuid

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from ..services.channel_service import ChannelService
from ..services.user_service import UserService


class WhatsappChannel(models.Model):
    _name = 'whatsapp.channel'
    _description = 'WhatsApp Channel (Whapi)'
    _order = 'name'

    name = fields.Char(required=True, default='WhatsApp')
    active = fields.Boolean(default=True)
    api_token = fields.Char(required=True, groups='whatsapp_whapi.group_whatsapp_manager')
    api_base_url = fields.Char(
        default='https://gate.whapi.cloud',
        required=True,
    )
    webhook_secret = fields.Char(
        default=lambda self: str(uuid.uuid4()),
        copy=False,
        groups='whatsapp_whapi.group_whatsapp_manager',
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('qr_pending', 'Awaiting QR'),
        ('connected', 'Connected'),
        ('error', 'Error'),
    ], default='draft', required=True)
    phone = fields.Char(readonly=True)
    profile_json = fields.Text(readonly=True)
    settings_json = fields.Text(readonly=True)
    limits_json = fields.Text(readonly=True)
    last_health_at = fields.Datetime(readonly=True)
    webhook_registered = fields.Boolean(readonly=True)
    user_ids = fields.Many2many(
        'res.users',
        'whatsapp_channel_user_rel',
        'channel_id',
        'user_id',
        string='Allowed Users',
    )
    chat_ids = fields.One2many('whatsapp.chat', 'channel_id')
    message_ids = fields.One2many('whatsapp.message', 'channel_id')
    contact_ids = fields.One2many('whatsapp.contact', 'channel_id')
    group_ids = fields.One2many('whatsapp.group', 'channel_id')
    media_ids = fields.One2many('whatsapp.media', 'channel_id')
    newsletter_ids = fields.One2many('whatsapp.newsletter', 'channel_id')
    product_ids = fields.One2many('whatsapp.product', 'channel_id')
    log_ids = fields.One2many('whatsapp.api.log', 'channel_id')
    chat_count = fields.Integer(compute='_compute_counts')
    message_count = fields.Integer(compute='_compute_counts')

    @api.depends('chat_ids', 'message_ids')
    def _compute_counts(self):
        for rec in self:
            rec.chat_count = len(rec.chat_ids)
            rec.message_count = len(rec.message_ids)

    def _get_webhook_url(self):
        self.ensure_one()
        base = self.env['ir.config_parameter'].sudo().get_param('web.base.url', '')
        return f'{base.rstrip("/")}/whatsapp/whapi/webhook/{self.webhook_secret}'

    def action_check_health(self):
        for channel in self:
            try:
                svc = ChannelService(channel)
                result = svc.health()
                channel.last_health_at = fields.Datetime.now()
                if result.get('status') in ('connected', 'online', 'ready', True) or result:
                    channel.state = 'connected' if channel.phone else channel.state
            except UserError as exc:
                channel.state = 'error'
                raise exc
        return True

    def action_sync_profile(self):
        for channel in self:
            svc = UserService(channel)
            profile = svc.profile()
            channel.profile_json = json.dumps(profile, indent=2)
            if isinstance(profile, dict):
                channel.phone = profile.get('phone') or profile.get('id') or channel.phone
                channel.state = 'connected'
        return True

    def action_sync_settings(self):
        for channel in self:
            svc = ChannelService(channel)
            settings = svc.get_settings()
            channel.settings_json = json.dumps(settings, indent=2)
        return True

    def action_register_webhooks(self):
        for channel in self:
            svc = ChannelService(channel)
            svc.register_webhook(channel._get_webhook_url())
            channel.webhook_registered = True
        return True

    def action_test_webhook(self):
        for channel in self:
            ChannelService(channel).test_webhook()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Webhook'),
                'message': _('Test webhook sent.'),
                'type': 'success',
                'sticky': False,
            },
        }

    def action_get_limits(self):
        for channel in self:
            limits = ChannelService(channel).get_limits()
            channel.limits_json = json.dumps(limits, indent=2)
        return True

    def action_logout(self):
        for channel in self:
            UserService(channel).logout()
            channel.state = 'draft'
            channel.phone = False
            channel.webhook_registered = False
        return True

    def action_open_qr_login(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('QR Login'),
            'res_model': 'whatsapp.qr.login',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_channel_id': self.id},
        }

    def action_open_inbox(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'tag': 'whatsapp_whapi.inbox',
            'name': _('WhatsApp Inbox'),
            'params': {'channel_id': self.id},
        }

    def action_sync_chats(self):
        for channel in self:
            self.env['whatsapp.chat'].sync_from_api(channel)
        return True

    def action_sync_contacts(self):
        for channel in self:
            self.env['whatsapp.contact'].sync_from_api(channel)
        return True

    def action_sync_groups(self):
        for channel in self:
            self.env['whatsapp.group'].sync_from_api(channel)
        return True

    def action_sync_products(self):
        for channel in self:
            self.env['whatsapp.product'].sync_from_api(channel)
        return True

    def action_sync_newsletters(self):
        for channel in self:
            self.env['whatsapp.newsletter'].sync_from_api(channel)
        return True

    def action_sync_collections(self):
        for channel in self:
            self.env['whatsapp.collection'].sync_from_api(channel)
        return True

    def _process_webhook_payload(self, payload):
        self.ensure_one()
        if payload.get('messages'):
            self.env['whatsapp.message'].upsert_from_webhook(self, payload['messages'])
        if payload.get('statuses'):
            self.env['whatsapp.message'].update_statuses_from_webhook(self, payload['statuses'])
        if payload.get('chats'):
            self.env['whatsapp.chat'].upsert_from_webhook(self, payload['chats'])
        if payload.get('contacts'):
            self.env['whatsapp.contact'].upsert_from_webhook(self, payload['contacts'])
        if payload.get('groups'):
            self.env['whatsapp.group'].upsert_from_webhook(self, payload['groups'])
        if payload.get('presences'):
            self.env['whatsapp.presence'].upsert_from_webhook(self, payload['presences'])
