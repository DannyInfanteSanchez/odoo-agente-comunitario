# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models
from odoo.exceptions import ValidationError


class IrConfigParameter(models.Model):
    _inherit = 'ir.config_parameter'

    def select_parameter(self, filtro_key):
        domain = [('key', '=', filtro_key)]
        record = self.search(domain, limit=1)
        if not record or not record.value:
            mensaje = 'Falta configurar el parametro {} , verifique'.format(filtro_key)
            raise ValidationError(mensaje)
        return record.value
