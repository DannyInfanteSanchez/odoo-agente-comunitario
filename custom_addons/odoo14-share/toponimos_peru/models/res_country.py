# -*- coding: utf-8 -*-

from odoo import api, fields, models


class CountryState(models.Model):
    _description = 'Country state'
    _inherit = 'res.country.state'
    _order = 'name'

    code = fields.Char(
        'Country Code', size=9,
        help='The ISO country code in two chars.\n'
        'You can use this field for quick search.')
    state_id = fields.Many2one('res.country.state', 'Departamento')
    province_id = fields.Many2one('res.country.state', 'Provincia')

    code_reniec = fields.Char('Ubigeo Reniec', size=6)

    @api.model
    def buscar_ubigeo(self, ubigeo):
        domain = [('country_id.code', '=', 'PE'),
                  ('code', '=', ubigeo)]
        return self.search(domain, limit=1)

    @api.model
    def consulta_ubigeoxnombres(self, pais, departamento, provincia, distrito):
        domain = [
            ('country_id.name', '=', pais),
            ('state_id.name', '=', departamento),
            ('province_id.name', '=', provincia),
            ('name', '=', distrito),
        ]
        district = self.env['res.country.state'].search(
            domain, limit=1)
        return district.id and district.code or ''

    @api.model
    def actualizar_xubigeo(self, model_res, res_id, codigo_ubigeo=False):
        """" Metodo para actualizar departamento, provincia, distrito de un recurso.

            :param model_res: modelo del recurso
            :param res_id: id del recurso
            :param codigo_ubigeo: 'ubigeo'

        En una acción de servidor:
        for record in records:
            model_state = env['res.country.state']
            model_state.actualizar_xubigeo(model, record.id)
        """
        res = model_res.browse(res_id)
        if not codigo_ubigeo:
            codigo_ubigeo = res.ubigeo
        if codigo_ubigeo and len(codigo_ubigeo) == 6:
            distrito = self.buscar_ubigeo(codigo_ubigeo)

            if distrito:
                value = dict(departamento_id=distrito.state_id.id,
                             provincia_id=distrito.province_id.id,
                             distrito_id=distrito.id)
                res.write(value)


class Lugar(models.AbstractModel):
    _description = 'Departamento/Provincia/Distrito'
    _name = 'res.country.lugar'
    _codigo_PE = 'PE'

    def _default_country_id(self):
        return self.env['res.country'].search(
            [('code', '=', self._default_country_code)], limit=1).id

    departamento_id = fields.Many2one(
        'res.country.state',
        'Departamento',
        domain=[
            ('country_id.code',
             '=',
             _codigo_PE),
            ('state_id',
             '=',
             False),
            ('province_id',
             '=',
             False)])
    provincia_id = fields.Many2one(
        'res.country.state', 'Provincia',
        domain="[('state_id.state_id', '=', False), ('state_id.province_id', '=', False),"
               " ('state_id', '=', departamento_id), ('province_id', '=', False)]")
    distrito_id = fields.Many2one(
        'res.country.state', 'Distrito',
        domain="[('state_id.province_id', '=', False),"
               " ('state_id', '=', departamento_id), ('province_id', '=', provincia_id)]")

    ubigeo = fields.Char('Ubigeo', size=6)

    @api.constrains('departamento_id', 'provincia_id', 'distrito_id')
    def _check_departamento_provincia_distrito(self):
        # Validacion - Distrito
        if self.distrito_id:
            if not self.departamento_id or not self.provincia_id:
                raise ValueError(
                    'Falta establecer la Provincia y Distrito')
            if self.distrito_id.state_id != self.departamento_id:
                raise ValueError(
                    'Error en el Departamento del Distrito')
            if self.distrito_id.province_id != self.provincia_id:
                raise ValueError('Error en la Provincia del Distrito')

        # Validacion - Provincia
        if self.provincia_id:
            if not self.departamento_id:
                raise ValueError('Falta establecer la Provincia')
            if self.provincia_id.state_id != self.departamento_id:
                raise ValueError(
                    'Error en el departamento de la provincia')

    @api.onchange('distrito_id')
    def _onchange_distrito_id(self):
        if (self.distrito_id and self.distrito_id.code and self.ubigeo and self.distrito_id.code != self.ubigeo) or (self.distrito_id and self.distrito_id.code and not self.ubigeo):
            return {'value': {'ubigeo': self.distrito_id.code}}

    @api.onchange('ubigeo')
    def _onchange_ubigeo(self):
        if self.ubigeo != self.distrito_id.code:
            distrito = self.env['res.country.state']
            domain = [('country_id.code', '=', self._codigo_PE),
                      ('code', '=', self.ubigeo)]
            distrito = distrito.search(domain, limit=1)

            if distrito:
                if distrito.state_id.id and distrito.province_id.id:
                    self.departamento_id = distrito.state_id
                    self.provincia_id = distrito.province_id
                    self.distrito_id = distrito
                elif distrito.state_id:
                    self.departamento_id = distrito.state_id
                    self.provincia_id = distrito
                    self.distrito_id = None
                else:
                    self.departamento_id = distrito
                    self.provincia_id = None
                    self.distrito_id = None
            else:
                self.departamento_id = None
                self.provincia_id = None
                self.distrito_id = None

    @api.model
    def create(self, values):
        # Si se ingresa el ubigeo, se establecerá el
        # departamento/provincia/distrito respectivo
        values = values or {}
        ubigeo = values.get('ubigeo', '')
        if ubigeo and len(ubigeo) == 6:
            domain = [('country_id.code', '=', self._codigo_PE),
                      ('code', '=', ubigeo)]

            distrito = self.env['res.country.state']
            distrito = distrito.search(domain, limit=1)
            if distrito.id:
                values.update(dict(departamento_id=distrito.state_id.id,
                                   provincia_id=distrito.province_id.id,
                                   distrito_id=distrito.id))

        return super(Lugar, self).create(values)
