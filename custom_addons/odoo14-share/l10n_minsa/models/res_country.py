
from odoo import api, models


class ResCountry(models.Model):
    _inherit = 'res.country'

    def write(self, vals):
        if 'code' in vals:
            domain = [('id', 'in', self.ids), ('code', '!=', vals['code'])]
            if not self.search(domain, limit=1):
                del vals['code']

        if not vals:
            return
        super(ResCountry, self).write(vals)
