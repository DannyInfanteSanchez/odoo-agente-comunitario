# -*- coding: utf-8 -*-
from odoo import models, api, fields


class EeSs(models.Model):
    _inherit = 'renipress.eess'

    display_name = fields.Char(string=u"Display Name", compute='_compute_display_name', store=True)

    def unlink(self):
        self.write({'active': False})

    def name_get(self):
        result = []
        for item in self:
            result.append((
                item.id, '%s - %s' % (
                    item.codigo_eess,
                    item.name)))
        return result

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        domain = []
        if self._context.get('from_registro', False):
            diresa_id = self._context.get('diresa_id', False)
            # Obtiene ID de los establecimientos por DIresa
            if diresa_id:
                self.env.cr.execute("""
                    SELECT e.id AS est_id FROM renipress_eess e
                    WHERE e.diresa_id=%s and e.active = true
                    """, (diresa_id,))
            else:
                self.env.cr.execute("""
                    SELECT e.id AS est_id FROM renipress_eess e
                    WHERE e.active = true
                    """)
            establecimiento_ids = self.env.cr.fetchall()
            establecimiento_ids = [i[0] for i in establecimiento_ids]
            domain = [
                ('id', 'in', establecimiento_ids)
            ]
        args = domain + args
        return super(EeSs, self).search(args, offset=offset, limit=limit, order=order, count=count)

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if self._context.get('from_registro', False):
            diresa_id = self._context.get('diresa_id', False)
            # Obtiene ID de los establecimientos por DIresa
            if diresa_id:
                self.env.cr.execute("""
                    SELECT e.id AS est_id FROM renipress_eess e
                    WHERE e.diresa_id=%s and e.active = true
                    """, (diresa_id,))
            else:
                self.env.cr.execute("""
                    SELECT e.id AS est_id FROM renipress_eess e
                    WHERE e.active = true
                    """)
            establecimiento_ids = self.env.cr.fetchall()
            establecimiento_ids = [i[0] for i in establecimiento_ids]
            return self.search([
                ('id', 'in', establecimiento_ids),
                ('display_name', operator, name)]).name_get()
        return super(EeSs, self).name_search(
            name, args=args, operator=operator, limit=limit)

    @api.depends('name', 'codigo_eess')
    def _compute_display_name(self):
        for record in self:
            record.display_name = (
                record.codigo_eess + '-' +
                record.name
            )
