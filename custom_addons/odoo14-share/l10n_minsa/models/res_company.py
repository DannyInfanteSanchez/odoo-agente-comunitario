
import os

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    logo = fields.Binary(default=lambda self: self._get_logo())
    # currency_id = fields.

    def _get_logo(self):
        logo_filename = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static/img/logo_minsa.png')
        return open(logo_filename, 'rb') .read().encode('base64')

    @api.model
    def create(self, vals):
        if not vals.get('logo'):
            vals.update({'logo': self._get_logo()})
        return super(ResCompany, self).create(vals)
