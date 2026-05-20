# -*- coding: utf-8 -*-
import json

from odoo import _, fields, models
from odoo.exceptions import UserError

from ..services.contact_service import ContactService


class WhatsappCheckPhones(models.TransientModel):
    _name = 'whatsapp.check.phones'
    _description = 'Check WhatsApp Phone Numbers'

    channel_id = fields.Many2one('whatsapp.channel', required=True)
    phones_text = fields.Text(required=True, help='One phone number per line')
    result_json = fields.Text(readonly=True)

    def action_check(self):
        self.ensure_one()
        phones = [p.strip() for p in (self.phones_text or '').splitlines() if p.strip()]
        if not phones:
            raise UserError(_('Enter at least one phone number.'))
        result = ContactService(self.channel_id).check_phones(phones)
        self.result_json = json.dumps(result, indent=2, default=str)
        contacts = result.get('contacts') or result.get('data') or []
        if contacts:
            self.env['whatsapp.contact'].upsert_from_api(self.channel_id, contacts)
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
