# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class BaseModel(models.AbstractModel):
    """
    Modelo Base para los Servicios Odoo
    """
    _description = u'Modelo Base Api'
    _name = 'baseapi.basemodel'

    """
    Especifique en _fields_json los pares `(dato, etiqueta)` que se devolvera en el metodo get_json

    _fields_json = [
        ('create_uid.login', ),  # Devolverá como dato object.create_uid.login y como etiqueta object_create_uid_login
        ('create_uid.login', 'create_login'), # Devolverá como dato object.create_uid.login y como etiqueta create_login
        ('write_date', ),  # Devolverá como dato write_date y como etiqueta write_date
    ]


    Ejemplo:
    """

    _fields_json = [
        ('create_uid.login', 'create_login'),
        ('write_uid.login', 'write_login'),
        ('create_date', 'create_date'),
        ('write_date', 'write_date'),
    ]

    @property
    def _alias_fields(self):
        return {key: value for value, key in self._fields_json}

    active = fields.Boolean(
        'Activo/Inactivo', default=True, track_visibility='onchange')

    @api.model
    def get_json(self, domain=None, order=None, limit=None, offset=None, only_fields=None):
        """
        Retorna data del catalogo, usando los "atributos" definidos en `_fields_json`

        :param domain: Dominio para filtrar el catálogo
        :rtype: dict
        """

        domain = domain or []
        _fields_json = []
        for field in self._fields_json:
            if len(field) == 1:
                field_name = field[0]
                field_label = field[0]
            elif len(field) == 2:
                field_name, field_label = field
            else:
                raise ValidationError('Error en la definicion de _fields_json')
            if '.' in field_label:
                field_label = field_label.replace('.', '_')
            _fields_json.append((field_name, field_label))

        self._fields_json = _fields_json

        result = []
        only_fields = only_fields and only_fields.split(',') or []
        for record in self.search(domain, order=order, limit=limit, offset=offset):
            item = {}
            for field_name, field_label in self._fields_json:
                if only_fields and field_label not in only_fields:
                    continue
                value = False
                for field in field_name.split('.'):
                    if value is False:
                        value = getattr(record, field)
                    else:
                        value = getattr(value, field)

                item.update({field_label: value})
            result.append(item)

        return result
