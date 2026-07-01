# -*- coding: utf-8 -*-

import uuid
from dateutil.relativedelta import relativedelta

from odoo import fields, models


class ResUser(models.Model):
    _inherit = 'res.users'

    token_ids = fields.One2many('res.users.token', 'user_id', 'Tokens')


class ResUsersToken(models.Model):
    _name = 'res.users.token'

    def _default_valid_until(self):
        t = fields.Datetime.from_string(fields.Datetime.now()) + relativedelta(days=365)
        return t

    user_id = fields.Many2one('res.users', 'Usuario')
    token = fields.Char('Token', size=50, index=True, default=lambda self: '%s' % uuid.uuid4(), required=True)
    valid_until = fields.Datetime('Fecha de Expiración', default=_default_valid_until, required=True)
    is_active = fields.Boolean('Is Active', default=True)
