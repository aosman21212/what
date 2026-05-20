# -*- coding: utf-8 -*-
from odoo import _, fields, models
from odoo.exceptions import UserError

from ..services.user_service import UserService


class WhatsappQrLogin(models.TransientModel):
    _name = 'whatsapp.qr.login'
    _description = 'WhatsApp QR Login'

    channel_id = fields.Many2one('whatsapp.channel', required=True)
    qr_image = fields.Binary(readonly=True)
    qr_base64 = fields.Text(readonly=True)
    state_message = fields.Char(readonly=True)

    def action_fetch_qr(self):
        self.ensure_one()
        if not self.channel_id.api_token:
            raise UserError(_('Please set the API token first.'))
        svc = UserService(self.channel_id)
        try:
            result = svc.login_qr_base64()
            qr_data = result.get('qr') or result.get('base64') or result.get('data')
            if qr_data:
                if ',' in str(qr_data):
                    qr_data = str(qr_data).split(',', 1)[1]
                self.qr_base64 = qr_data
                self.qr_image = qr_data
            self.channel_id.state = 'qr_pending'
            self.state_message = _('Scan the QR code with WhatsApp on your phone.')
        except UserError:
            try:
                img_result = svc.login_qr_image()
                if isinstance(img_result, dict) and img_result.get('qr'):
                    self.qr_image = img_result['qr']
                else:
                    raise
            except Exception as exc:
                raise UserError(_('Could not fetch QR code: %s') % exc) from exc
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_check_connected(self):
        self.ensure_one()
        self.channel_id.action_sync_profile()
        if self.channel_id.state == 'connected':
            self.state_message = _('Connected as %s') % (self.channel_id.phone or '')
        else:
            self.state_message = _('Not connected yet. Scan QR and try again.')
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
