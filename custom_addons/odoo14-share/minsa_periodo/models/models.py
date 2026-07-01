# coding: utf-8

from dateutil.relativedelta import relativedelta

from odoo import models, api, fields
from odoo.exceptions import UserError


class MinsaAnho(models.Model):
    _name = 'minsa.anho'
    _order = 'date_start'

    name = fields.Char(u'Año Fiscal', required=True)
    code = fields.Char(u'Codigo', size=6, required=True)
    date_start = fields.Date(u'Fecha de Inicio', required=True)
    date_stop = fields.Date(u'Fecha de Fin', required=True)
    period_ids = fields.One2many('minsa.periodo', 'fiscalyear_id', u'Periodos')
    state = fields.Selection(
        [('draft', 'Abierto'),
         ('done', 'Cerrado')],
        'Estado',
        readonly=True,
        copy=False)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', u'El código debe ser único!'),
        ('period_uniq', 'unique(date_start, date_stop)', u'El periodo debe ser único'),
    ]

    def create_period(self):
        interval = 1

        for record in self:
            date_start = fields.Date.from_string(record.date_start)
            date_stop = fields.Date.from_string(record.date_stop)
            while date_start < date_stop:
                date_end = date_start + relativedelta(months=interval, days=-1)
                if date_end > date_stop:
                    date_end = date_stop
                self.env['minsa.periodo'].create({
                    'name': date_start.strftime('%m/%Y'),
                    'code': date_start.strftime('%m/%Y'),
                    'date_start': fields.Date.to_string(date_start),
                    'date_stop': fields.Date.to_string(date_end),
                    'fiscalyear_id': record.id,
                })
                date_start = date_start + relativedelta(months=interval)
        return True


class MinsaPeriodo(models.Model):
    _name = 'minsa.periodo'
    _order = 'fiscalyear_id, date_start'

    name = fields.Char(u'Nombre de Periodo', required=True)
    code = fields.Char(u'Code', size=12, required=True)
    special = fields.Boolean(u'Periodo Cerrado / Abierto')
    date_start = fields.Date(u'Inicio de Periodo', required=True)
    date_stop = fields.Date(u'Fin de Periodo', required=True)
    fiscalyear_id = fields.Many2one('minsa.anho', u'Año Fiscal', required=True, index=True)
    year = fields.Integer(u'Año', compute='_compute_year', store=True, readonly=True)
    month = fields.Integer(u'Mes', compute='_compute_month', store=True, readonly=True)
    state = fields.Selection(
        [('draft', 'Abierto'),
         ('done', 'Cerrado')],
        u'Estado',
        readonly=True,
        copy=False,
        default='draft'
    )

    _sql_constraints = [
        ('name_uniq', 'unique (name)', u'El código debe ser único!'),
        ('period_uniq', 'unique(fiscalyear_id, date_start, date_stop)', u'El periodo debe ser único'),
    ]

    @api.onchange('special')
    def _onchange_special(self):
        if self.special:
            self.state = 'done'
        else:
            self.state = 'draft'

    @api.depends('date_start', 'date_stop')
    def _compute_year(self):
        for record in self:
            if not (record.date_start and record.date_stop):
                continue

            date_start = fields.Date.from_string(record.date_start)
            date_stop = fields.Date.from_string(record.date_stop)
            record.year = date_start.year == date_stop.year and date_start.year

    @api.depends('date_start', 'date_stop')
    def _compute_month(self):
        for record in self:
            if not (record.date_start and record.date_stop):
                continue

            date_start = fields.Date.from_string(record.date_start)
            date_stop = fields.Date.from_string(record.date_stop)
            record.month = date_start.month == date_stop.month and date_start.month

    @api.constrains('date_start', 'date_stop')
    def _check_date_start_stop(self):
        for record in self:
            date_start = record.date_start and fields.Datetime.from_string(record.date_start)
            date_stop = record.date_stop and fields.Datetime.from_string(record.date_stop)
            if not date_start:
                message = u'Error en la configuración "Inicio del Periodo" {}'.format(record.name)
                raise UserError(message)

            if not date_stop:
                message = u'Error en la configuración "Fin del Periodo" {}'.format(record.name)
                raise UserError(message)

            if date_start >= date_stop:
                message = u'Error en la configuración "Inicio del Periodo"/"Fin del Periodo" {}'.format(record.name)
                raise UserError(message)
