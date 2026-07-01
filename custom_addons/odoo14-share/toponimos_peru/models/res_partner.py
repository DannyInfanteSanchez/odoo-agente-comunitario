# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    def _default_country_id(self):
        country_peru = self.env['res.country'].search(
            ['|', ('name', '=', 'Perú'), ('name', '=', 'Peru')], limit=1)
        if country_peru:
            return country_peru
        else:
            return None

    ubigeo = fields.Char('Ubigeo')
    country_id = fields.Many2one(
        'res.country',
        'País',
        default=_default_country_id)
    state_id = fields.Many2one('res.country.state', 'Departamento')
    province_id = fields.Many2one('res.country.state', 'Provincia')
    district_id = fields.Many2one('res.country.state', 'Distrito')

    # Funcion reemplazada para considerar los nuevos campos en el onchange
    @api.model
    def _address_fields(self):
        """ Returns the list of address fields that are synced from the parent
        when the `use_parent_address` flag is set. """
        # ~ return list(ADDRESS_FIELDS)
        address_fields = (
            'street',
            'street2',
            'zip',
            'city',
            'state_id',
            'country_id',
            'province_id',
            'district_id')
        return list(address_fields)

    # # Onchange para actualizar el codigo de distrito
    @api.onchange('district_id')
    def onchange_district(self):
        if self.district_id:
            state = self.district_id.code
            self.zip = state
        else:
            self.zip = None

    @api.onchange('zip')
    def onchange_zip(self):
        # self = self.with_context({'ctx': 'district_id'})
        if self.zip != self.district_id.code:
            district = self.env['res.country.state']
            domain = [('country_id', '=', self.country_id.id),
                      ('code', '=', self.zip)]
            district = district.search(domain, limit=1)
            if district:
                if district.state_id.id and district.province_id.id:
                    self.state_id = district.state_id
                    self.province_id = district.province_id
                    self.district_id = district
                elif district.state_id:
                    self.state_id = district.state_id
                    self.province_id = district
                    self.district_id = None
                else:
                    self.state_id = district
                    self.province_id = None
                    self.district_id = None
            else:
                self.state_id = None
                self.province_id = None
                self.district_id = None

    def _display_address(self, without_company=False):
        '''
        The purpose of this function is to build and return an address formatted accordingly to the
        standards of the country where it belongs.

        :param address: browse record of the res.partner to format
        :returns: the address formatted in a display that fit its country habits (or the default ones
            if not country is specified)
        :rtype: string
        '''
        # get the information that will be injected into the display format
        # get the address format
        address_format = self.country_id.address_format or \
            "%(street)s\n%(street2)s\n%(state_name)s-%(province_name)s-%(district_code)s %(zip)s\n%(country_name)s"
        args = {
            'district_code': self.district_id.code or '',
            'district_name': self.district_id.name or '',
            'province_code': self.province_id.code or '',
            'province_name': self.province_id.name or '',
            'state_code': self.state_id.code or '',
            'state_name': self.state_id.name or '',
            'country_code': self.country_id.code or '',
            'country_name': self.country_id.name or '',
            'company_name': self.parent_name or '',
        }
        for field in self._address_fields():
            args[field] = getattr(self, field) or ''
        if without_company:
            args['company_name'] = ''
        elif self.commercial_company_name:
            address_format = '%(company_name)s\n' + address_format
        return address_format % args
