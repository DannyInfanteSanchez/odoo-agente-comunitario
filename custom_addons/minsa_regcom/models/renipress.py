# -*- coding: utf-8 -*-

from odoo import fields, models


class UnidadEjecutora(models.Model):
    _name = 'minsa.unidad.ejecutora'
    _description = 'Unidad Ejecutora'
    _order = 'codigo'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    codigo = fields.Char(string=u'Código', size=10, required=True, tracking=True)
    name = fields.Char(string='Nombre', required=True, tracking=True)
    active = fields.Boolean(default=True, tracking=True)

    def unlink(self):
        self.write({'active': False})

    _sql_constraints = [
        ('uniq_codigo', 'UNIQUE(codigo)', u"Código ya existe, verifique"),
        ('uniq_name', 'UNIQUE(name)', u"Nombre ya existe, verifique")
    ]


class EeSs(models.Model):
    _inherit = 'renipress.eess'

    unidadejecutora_id = fields.Many2one(
        'minsa.unidad.ejecutora',
        string=u'Unidad Ejecutora',
        tracking=True)
