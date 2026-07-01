
from odoo import models, api

TZ = 'America/Lima'


class Resuser(models.Model):
    _inherit = 'res.users'

    @api.model
    def create(self, values):
        if not values.get('tz', False):
            values.update(dict(tz=TZ))
        return super(Resuser, self).create(values)
