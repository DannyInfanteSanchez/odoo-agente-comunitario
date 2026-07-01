# -*- coding: utf-8 -*-

from odoo import fields, models


class ResCountryState(models.Model):
    _inherit = 'res.country.state'

    diresa_ids = fields.Many2many(
        'renipress.diresa',
        'renipress_diresa_departamento_rel',
        'departamento_id', 'diresa_id',
        'Diresas', readonly=True)
