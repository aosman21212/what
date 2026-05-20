# -*- coding: utf-8 -*-
from odoo import fields, models


class WhatsappGroupParticipant(models.Model):
    _name = 'whatsapp.group.participant'
    _description = 'WhatsApp Group Participant'

    group_id = fields.Many2one('whatsapp.group', required=True, ondelete='cascade')
    participant_id = fields.Char(required=True)
    is_admin = fields.Boolean()
