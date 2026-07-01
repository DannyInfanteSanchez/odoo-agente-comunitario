# -*- coding: utf-8 -*-
import re
import requests
import json
import base64
from datetime import date
from odoo import models, fields, api, _
from odoo.osv import expression
from .helper import _mapa_obtener_direccion, _mapa_obtener_coordenada, consulta_reniec
from odoo.exceptions import ValidationError


PLANTILLA_TELEFONO_FIJO = '^[+]*[(]{0,1}[0-9]{1,4}[)]{0,1}[-\s\./0-9]*$'
PLANTILLA_CELULAR = '^[9]\d{8}$'

# Constantes Tipo de documento
_DNI = '01'
_CARNE_EXTRANJERIA = '03'
_PASAPORTE = '07'
_PERMISO_TEMPORAL_PERMANENCIA = '23'

# Tipo de documento
SELECTION_TIPO_DOCUMENTO = [
    (_DNI, 'DNI.'),
    (_CARNE_EXTRANJERIA, 'Carné.Ext.'),
    (_PASAPORTE, 'Pasaporte'),
    (_PERMISO_TEMPORAL_PERMANENCIA, 'Carné PTP')
]


class AgenteComunitario(models.Model):
    _name = 'minsa.agente.comunitario'
    _description = 'Agente comunitario de salud'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _compute_es_grupo_nacional(self):
        if self.env['res.users'].has_group('minsa_regcom.group_nacional'):
            self.es_grupo_nacional = True
        else:
            self.es_grupo_nacional = False
        return self.es_grupo_nacional

    def _compute_es_grupo_diresa(self):
        if self.env['res.users'].has_group('minsa_regcom.group_diresa'):
            self.es_grupo_diresa = True
        else:
            self.es_grupo_diresa = False
        return self.es_grupo_diresa

    def _compute_es_grupo_red(self):
        if self.env['res.users'].has_group('minsa_regcom.group_red'):
            self.es_grupo_red = True
        else:
            self.es_grupo_red = False
        return self.es_grupo_red

    def _compute_es_grupo_establecimiento(self):
        if self.env['res.users'].has_group('minsa_regcom.group_establecimiento'):
            self.es_grupo_establecimiento = True
        else:
            self.es_grupo_establecimiento = False
        return self.es_grupo_establecimiento

    def _compute_es_admin(self):
        if self.env['res.users'].has_group('base.group_erp_manager') or self.env['res.users'].has_group('minsa_regcom.group_adminregcom'):
            self.es_grupo_admin = True
        else:
            self.es_grupo_admin = False
        return self.es_grupo_admin

    def _compute_url_open_mapa(self):
        domain = [("key", "=", "map_sigrid_url")]
        record = self.env["ir.config_parameter"].search(domain, limit=1)
        if not record or not record.value:
            raise ValidationError("No esta configurado el parámetro de URL SIGRID")
        url_sigrid = record.value
        url = self._prepare_url(
            url_sigrid, {"{usuario}": self.env.user.nro_documento}
        )
        self.url_open_mapa = url
        return url

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if False and self._context.get('form_registro_agente', False):
            filtro_diresa = 'true'
            filtro_red = 'true'
            filtro_establecimiento = 'true'
            filtro_name = 'true'
            diresa_id = self.env.user.diresa_id.id or False
            red_id = self.env.user.red_id.id or False
            establecimiento_id = self.env.user.red_id.id or False

            if args['name']:
                filtro_name = "p.name ilike '{}'".format(args['name'])
            if diresa_id:
                filtro_diresa = 'p.diresa_id = {}'.format(diresa_id)
            if red_id:
                filtro_red = 'p.red_id = {}'.format(red_id)
            if establecimiento_id:
                filtro_establecimiento = 'p.establecimiento_id = {}'.format(establecimiento_id)
            query = '''
                SELECT
                    p.id AS id,
                    p.name AS name
                FROM minsa_agente_comunitario p
                WHERE p.es_voluntario = true
                        AND p.active = True
                        AND {0}
                        AND {1}
                        AND {2}
                        AND {3}
            '''
            query = query.format(
                filtro_diresa,
                filtro_red,
                filtro_establecimiento,
                filtro_name
            )
            self.env.cr.execute(query)
            partner_ids = self.env.cr.dictfetchall()
            partner_ids = [x['id'] for x in partner_ids]
            ids = super(AgenteComunitario, self.sudo())._search([('id', 'in', partner_ids)])
        else:
            if self.check_access_rights('read', raise_exception=False):
                return super(AgenteComunitario, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
            ids = self.env['minsa.agente.comunitario']._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
            if not count and isinstance(ids, query):
                # the result is expected from this table, so we should link tables
                ids = super(AgenteComunitario, self.sudo())._search([('id', 'in', ids)])
        return ids

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        if self._context.get('form_registro_agente', False):
            diresa_id = self.env.user.diresa_id.id or False
            red_id = self.env.user.red_id.id or False
            establecimiento_id = self.env.user.establecimiento_id.id or False
            domain = [('es_voluntario', '=', True)]
            if diresa_id:
                domain.append(('diresa_id', '=', diresa_id))
            if red_id:
                domain.append(('red_id', '=', red_id))
            if establecimiento_id:
                domain.append(('establecimiento_id', '=', establecimiento_id))
            if name:
                domain.append(('name', operator, name))
            return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)
        return super(AgenteComunitario, self)._name_search(name, args, operator, limit, name_get_uid=name_get_uid)

    @api.onchange("tipo_documento")
    def _onchange_tipo_documento(self):
        if not self.tipo_documento:
            return

        if self.tipo_documento:
            self.numero_documento = False
            self.name = False
            self.telefono = False
            return

    @api.onchange("numero_documento", "tipo_documento")
    def _onchange_numero_documento(self):
        # Validamos Nro. documento
        errors = ''
        if not self.numero_documento:
            return {
                'value': {
                    'name': '',
                    'ape_paterno': '',
                    'ape_materno': '',
                    'nombres': '',
                    'telefono': '',
                    'fecha_nacimiento': False,
                    'genero_id': False
                }
            }
        try:
            data, errors = consulta_reniec(self, self.tipo_documento, self.numero_documento)
        except Exception:
            return {
                'value': {
                    'name': '',
                    'ape_paterno': '',
                    'ape_materno': '',
                    'nombres': '',
                    'telefono': '',
                    'fecha_nacimiento': False,
                    'genero_id': False
                }
            }

        # nombres y apellidos
        if errors and len(errors) > 0:
            return {
                'value': {
                    'name': '',
                    'ape_paterno': '',
                    'ape_materno': '',
                    'nombres': '',
                    'telefono': '',
                    'fecha_nacimiento': False,
                    'genero_id': False
                },
                'warning': {
                    'title': u'Error en la búsqueda',
                    'message': u'{}'.format(data.get('error')),
                }
            }

        self.captura_nombre()
        if self.tipo_documento in [_DNI]:
            return {
                'value': {
                    'name': self.name,
                    'ape_paterno': self.ape_paterno,
                    'ape_materno': self.ape_materno,
                    'nombres': self.nombres,
                    'genero_id': self.genero_id,
                    'fecha_nacimiento': self.fecha_nacimiento
                }
            }

    def captura_nombre(self):
        if self.tipo_documento in [_DNI]:
            data, errors = consulta_reniec(self, self.tipo_documento, self.numero_documento)
            data = data[1]
            self.ape_paterno = data.get('apellidoPaterno', False)
            self.ape_materno = data.get('apellidoMaterno', False)
            self.nombres = data.get('nombres', False)
            self.name = u"{} {} {}".format(self.ape_paterno, self.ape_materno, self.nombres)
            self.genero_id = self.env['minsa.genero'].search([('codigo', '=', data.get('genero', False))], limit=1)
            fecha = data.get('fechaNacimiento', False)
            fecnac = fecha[:4] + '-' + fecha[4:6] + '-' + fecha[6:8]
            self.fecha_nacimiento = fecnac
        else:
            materno = ""
            if self.ape_materno:
                materno = self.ape_materno
            self.name = u"{} {} {}".format(self.ape_paterno, materno, self.nombres)

    def normalize(self, s):
        replacements = (
            ("á", "a"),
            ("é", "e"),
            ("í", "i"),
            ("ó", "o"),
            ("ú", "u"),
        )
        for a, b in replacements:
            s = s.replace(a, b).replace(a.upper(), b.upper())
        return s

    def _prepare_url(self, url, replace):
        for key, value in replace.items():
            if not isinstance(value, str):
                # for latitude and longitude which are floats
                if isinstance(value, float):
                    value = "%.5f" % value
                else:
                    value = ""
            url = url.replace(key, value)
        return url

    def open_map(self):
        self.ensure_one()

        domain = [("key", "=", "map_openstreetmap_url_buscar_coordenada")]
        record = self.env["ir.config_parameter"].search(domain, limit=1)
        if not record or not record.value:
            raise ValidationError("No esta configurado el parámetro de URL OPENSTREETMAP buscar Coordenada")
        url_coordenada = record.value
        if url_coordenada and self.latitud and self.longitud:
            url = self._prepare_url(
                url_coordenada,
                {
                    "{LATITUDE}": self.latitud,
                    "{LONGITUDE}": self.longitud,
                },
            )
        else:
            domain = [("key", "=", "map_openstreetmap_url_buscar_direccion")]
            record = self.env["ir.config_parameter"].search(domain, limit=1)
            if not record or not record.value:
                raise ValidationError("No esta configurado el parámetro de URL OPENSTREETMAP buscar Direccion")
            url_direccion = record.value
            url = self._prepare_url(
                url_direccion, {"{ADDRESS}": self.direccion}
            )
        return {
            "type": "ir.actions.act_url",
            "url": url,
            "target": "new",
        }

    def open_location_modal(self):
        self.ensure_one()
        self.url_open_mapa = self._compute_url_open_mapa()
        self.dummy_field = "<iframe id= 'form_modal_iframe_id' src='{0}' frameborder='0' style='border: none; width: 100%; height: 100%;'></iframe>".format(self.url_open_mapa)
        return {
            "name": u"Mapa Geolocalización",
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "minsa.agente.comunitario",
            "view_id": self.env.ref("minsa_regcom.agente_comunitario_view_mapa_form").id,  # NOQA
            "target": "new",
            "context": {"url_open_mapa": self.url_open_mapa},
            "res_id": self.id,
        }

    def cancel(self):
        # close the modal form without saving any changes
        return {'type': 'ir.actions.act_window_close'}

    def recupera_map_sigrid(self):
        self.ensure_one()
        domain = [("key", "=", "map_sigrid_url_recupera_direccion")]
        record = self.env["ir.config_parameter"].search(domain, limit=1)
        # departamento_id, provincia_id, distrito_id, ubigeo = False
        if not record or not record.value:
            raise ValidationError("No esta configurado el parámetro de URL RECUPERA SIGRID ")
        url_sigrid = record.value
        url = self._prepare_url(
            url_sigrid, {"{usuario}": self.env.user.nro_documento}
        )
        response = requests.get(url)
        if response.status_code != 200:
            raise ValidationError("No existe respuesta de la url de SIGRID")
        record_pais = self.env["res.country"].sudo().search([('code', '=', 'PE')], limit=1)
        data = response.json()
        departamento = data.get('departamento') or False
        provincia = data.get('provincia') or False
        distrito = data.get('distrito') or False
        departamento_id = False
        provincia_id = False
        distrito_id = False
        str_departamento = ''
        str_provincia = ''
        str_distrito = ''
        if departamento:
            str_departamento = "{}".format(self.normalize(departamento).lower())
        if str_departamento:
            str_departamento = "'{0}'".format(str_departamento)
            query = """
                    SELECT id, name
                    FROM res_country_state WHERE
                    country_id = {0} and
                    state_id isnull and
                    province_id isnull and
                    TRIM(BOTH FROM LOWER(replace(name,'áéíóúÁÉÍÓÚäëïöüÄËÏÖÜ','aeiouAEIOUaeiouAEIOU')))
                    = {1}
                    order by id asc limit 1;
                """.format(record_pais.id, str_departamento)
            print('******* query departamento=', query)
            self._cr.execute(query)
            res = self.env.cr.fetchall()
            if res:
                departamento_id = res[0][0]
        if not departamento_id:
            raise ValidationError("No existe departamento %s " % (str_departamento))

        if provincia:
            str_provincia = "{}".format(self.normalize(provincia).lower())
        if str_provincia:
            str_provincia = "'{0}'".format(str_provincia)
            query = """
                    SELECT id, name
                    FROM res_country_state WHERE
                    country_id = {0} and
                    state_id = {1} and
                    province_id isnull and
                    TRIM(BOTH FROM LOWER(replace(name,'áéíóúÁÉÍÓÚäëïöüÄËÏÖÜ','aeiouAEIOUaeiouAEIOU')))
                    = ({2})
                    order by id asc limit 1;
                """.format(record_pais.id, departamento_id, str_provincia)
            self._cr.execute(query)
            res = self.env.cr.fetchall()
            if res:
                provincia_id = res[0][0]
        if not provincia_id:
            raise ValidationError("No existe provincia %s " % (str_provincia))

        if distrito:
            ubigeo = ''
            str_distrito = "{}".format(self.normalize(distrito).lower())
        if str_distrito:
            str_distrito = "'%{0}%'".format(str_distrito)
            query = """
                SELECT id, name, code_reniec
                FROM res_country_state WHERE
                country_id = {0} and
                state_id = {1} and
                province_id = {2} and
                TRIM(BOTH FROM LOWER(replace(name,'áéíóúÁÉÍÓÚäëïöüÄËÏÖÜ','aeiouAEIOUaeiouAEIOU')))
                like ({3})
                order by id asc limit 1;
            """.format(record_pais.id, departamento_id, provincia_id, str_distrito)
            self._cr.execute(query)
            res = self.env.cr.fetchall()
            if res:
                distrito_id = res[0][0]
                ubigeo = res[0][2]
        if not distrito_id:
            raise ValidationError("No existe departamento %s, Provincias %s distrito %s" % (departamento_id, provincia_id, str_distrito))

        self.longitud = data.get('x')
        self.latitud = data.get('y')
        self.direccion = data.get('match_addr')
        self.ubigeo = ubigeo
        self.state_id = departamento_id
        self.province_id = provincia_id
        self.district_id = distrito_id

    def buscar_direccion(self):
        self.ensure_one()
        data = None
        status = None
        mensaje = None
        if not self.direccion:
            raise ValidationError("Tiene que ingresar una dirección, verifique")
        data, status, mensaje = _mapa_obtener_direccion(self, self.direccion)
        if not data:
            raise ValidationError(_("Direccion Estado:%s Error %s" % (status, mensaje)))
        else:
            self.longitud = data.get('longitud')
            self.latitud = data.get('latitud')
            self.direccion = data.get('direccion')
            self.state_id = data.get('departamento_id')
            self.province_id = data.get('provincia_id')
            self.district_id = data.get('distrito_id')
            self.ubigeo = data.get('ubigeo')

    def buscar_coordenada(self):
        self.ensure_one()
        data = None
        status = None
        mensaje = None
        data, status, mensaje = _mapa_obtener_coordenada(self, self.latitud, self.longitud)
        if not data:
            msj = "Coordenada Estado:{} Error:{}".format(status, mensaje)
            raise ValidationError(msj)
        else:
            self.direccion = data.get('direccion')
            self.state_id = data.get('departamento_id')
            self.province_id = data.get('provincia_id')
            self.district_id = data.get('distrito_id')
            self.ubigeo = data.get('ubigeo')

    @api.onchange('nombres', 'ape_paterno', 'ape_materno')
    def _onchange_nombres(self):
        if self.ape_paterno and self.nombres:
            materno = ""
            if self.ape_materno:
                materno = self.ape_materno
            self.name = u"{} {}, {}".format(self.ape_paterno, materno, self.nombres)
            return {
                'value': {
                    'name': self.name
                }
            }

    @api.onchange('line_ids', 'invoice_payment_term_id', 'invoice_date_due', 'invoice_cash_rounding_id', 'invoice_vendor_bill_id')
    def _onchange_recompute_dynamic_lines(self):
        self._recompute_dynamic_lines()

    def unlink(self):
        self.write({'active': False})

    @api.constrains('telefono')
    def _check_telefono(self):
        if self.telefono and not re.search(PLANTILLA_TELEFONO_FIJO, self.telefono):
            raise ValidationError(u'Teléfono fijo inv álido')

    @api.constrains('celular')
    def _check_celular(self):
        if self.celular and not re.search(PLANTILLA_CELULAR, self.celular):
            raise ValidationError(u'Número de celular inválido')

    @api.constrains('direccion')
    def _check_direccion(self):
        if not self.direccion:
            raise ValidationError('Falta que ingrese una dirección, verifique')

    @api.constrains('email')
    def _check_email(self):
        param_obj = self.env["ir.config_parameter"].sudo()
        validador_email = param_obj.get_param("validador_email") or False
        if not validador_email:
            raise ValidationError(u'Falta configurar el parametro validador_email, coordine con el administrador del sistema')
        if self.email and not re.search(validador_email, self.email):
            raise ValidationError(u'Correo invalido, verifique')

    @api.depends('dialecto_ids')
    def _compute_name_dialectos(self):
        for record in self:
            names = record.dialecto_ids.mapped('display_name')
            record.name_dialectos = ', '.join(names)

    @api.depends('fecha_nacimiento')
    def _compute_edad(self):
        today = date.today()
        for record in self:
            if record.fecha_nacimiento:
                birth_date = fields.Date.from_string(record.fecha_nacimiento)
                delta = today - birth_date
                record.edad = delta.days // 365

    name = fields.Char(string="Apellido y Nombres", help=u"Apellidos y nombres", tracking=True)
    ape_paterno = fields.Char(string="Apellido Paterno", help=u"Ingresar el apellido paterno", tracking=True)
    ape_materno = fields.Char(string="Apellido Materno", help=u"Ingresar el apellido materno", tracking=True)
    nombres = fields.Char(string="Nombres", help=u"Ingresar el nombre", tracking=True)
    diresa_id = fields.Many2one(
        'renipress.diresa',
        string=u'Diresa',
        default=lambda self: self.env.user.diresa_id.id or False, tracking=True
    )
    red_id = fields.Many2one(
        'renipress.red',
        'Red',
        domain="[('diresa_id', '=', diresa_id)]",
        default=lambda self: self.env.user.red_id.id or False, tracking=True
    )
    establecimiento_id = fields.Many2one(
        'renipress.eess',
        string='Renipress',
        domain="[('red_id', '=', red_id)]",
        default=lambda self: self.env.user.establecimiento_id.id or False, tracking=True
    )
    tipo_documento = fields.Selection(selection=SELECTION_TIPO_DOCUMENTO, string='Tipo Documento', default=_DNI, tracking=True)
    numero_documento = fields.Char(string="Num.Documento", help=u"Ingresar el número del documento de identidad")
    telefono = fields.Char(string=u"Teléfono", help=u"Ingrese nmero de telefono fijo")
    celular = fields.Char(string="Celular", help=u"Ingresar nmero de celular")
    email = fields.Char(string=u"Correo electrónico", help=u"Ingresar el correo electrnico")
    operador_id = fields.Many2one('minsa.operador.mobil', string='Operador', tracking=True)
    fecha_nacimiento = fields.Date(
        "Fecha Nacimiento",
        tracking=True
    )
    edad = fields.Integer(string="Edad", compute='_compute_edad', store=True)
    genero_id = fields.Many2one('minsa.genero', string='Genero', tracking=True)
    etnia_id = fields.Many2one('minsa.etnia', string='Etnia', tracking=True)
    seguro_id = fields.Many2one('minsa.seguro', string='Tipo de seguro', tracking=True)
    dialecto_id = fields.Many2one('minsa.dialecto', string='Idioma Dialecto', tracking=True)
    dialecto_ids = fields.Many2many(
        "minsa.dialecto", "ins_postulante_estab_ref",
        string="Idioma Dialectos",
        help="Seleccione los idiomas que habla")
    name_dialectos = fields.Char(string="Dialectos", compute='_compute_name_dialectos', store=True)
    grado_instruccion_id = fields.Many2one('minsa.grado.instruccion', string=u'Grado de Instrucción', tracking=True)
    tipo_voluntariado_id = fields.Many2one('minsa.tipo.voluntariado', string=u'Tipo de voluntariado', tracking=True)
    tipo_voluntariado_ids = fields.Many2many(
        "minsa.tipo.voluntariado", "agente_voluntariado_ref",
        string="Tipo de voluntariado",
        help="Seleccione los tipos de voluntariado")
    direccion = fields.Char(string=u"Direccion", help=u"Ingresar la dirección")
    country_id = fields.Many2one(
        'res.country',
        string='Country',
        ondelete='restrict',
        default=lambda self: self.env["ir.model.data"].xmlid_to_res_id("base.pe") or False,
    )
    state_id = fields.Many2one("res.country.state", string='Departamento', ondelete='restrict', domain="[('country_id', '=?', country_id)]")
    province_id = fields.Many2one("res.country.state", string='Provincia', ondelete='restrict', domain="[('country_id', '=?', country_id),('state_id', '=?', state_id)]")
    district_id = fields.Many2one("res.country.state", string='Distrito', ondelete='restrict', domain="[('country_id', '=?', country_id),('state_id', '=?', state_id),('province_id', '=?', province_id)]")
    ubigeo = fields.Char(string=u"Ubigeo", help=u"Ubigeo")
    latitud = fields.Float(string='Geo Latitud', digits=(16, 5))
    longitud = fields.Float(string='Geo Longitud', digits=(16, 5))
    active = fields.Boolean(string='Activo', default=True)

    es_voluntario = fields.Boolean(string="Es voluntario", tracking=True, default=False)
    es_grupo_nacional = fields.Boolean('Grupo Nacional', compute='_compute_es_grupo_nacional', default=False)
    es_grupo_diresa = fields.Boolean('Grupo Diresa', compute='_compute_es_grupo_diresa', default=False)
    es_grupo_red = fields.Boolean('Grupo Red', compute='_compute_es_grupo_red', default=False)
    es_grupo_establecimiento = fields.Boolean('Grupo Establecimiento', compute='_compute_es_grupo_establecimiento', default=False)
    es_grupo_admin = fields.Boolean('Grupo Admin', compute='_compute_es_admin', default=False)
    url_open_mapa = fields.Char('URL Mapa', compute='_compute_url_open_mapa', default=False)
    dummy_field = fields.Char('Dummpy')
    cuenta_field = fields.Integer('Cuenta', default="1")
    foto = fields.Binary(string="Foto", required="1")
    nivel_agente_id = fields.Many2one('minsa.nivel.agente', string=u'Nivel Agente', tracking=True)
    estandar_laboral_id = fields.Many2one('minsa.estandar.laboral', string=u'Estándar de Competencia Laboral', tracking=True)

    _sql_constraints = [
        ('uniq_tipo_documento_numero_documento', 'UNIQUE(tipo_documento,numero_documento)', u"Tipo y número de documento ya existe, verifique")
    ]

    @api.model_create_multi
    def create(self, values):
        res = super().create(values)
        record_id = res.id
        if res.tipo_documento in [_DNI]:
            data, errors = consulta_reniec(self, res.tipo_documento, res.numero_documento)
            data = data[1]
            ape_paterno = data.get('apellidoPaterno', False)
            ape_materno = data.get('apellidoMaterno', False)
            nombres = data.get('nombres', False)
            genero = self.env['minsa.genero'].search([('codigo', '=', data.get('genero', False))], limit=1)
            fecha = data.get('fechaNacimiento', False)
            fecnac = fecha[:4] + '-' + fecha[4:6] + '-' + fecha[6:8]
            fecha_nacimiento = fecnac
            if fecha_nacimiento:
                birth_date = fields.Date.from_string(fecha_nacimiento)
                delta = date.today() - birth_date
                edad_year = delta.days // 365
            else:
                self.fecha_nacimiento._compute_edad(self)
                edad_year = self.fecha_nacimiento
            name = u"{} {} {}".format(ape_paterno, ape_materno, nombres)
            self.env.cr.execute("""
                UPDATE minsa_agente_comunitario
                    SET ape_paterno = %s,
                        ape_materno = %s,
                        nombres = %s,
                        name = %s,
                        genero_id = %s,
                        fecha_nacimiento = %s,
                        edad = %s
                WHERE id = %s
                """, (ape_paterno, ape_materno, nombres, name, genero.id, fecha_nacimiento, edad_year, record_id,))
        else:
            materno = ""
            if self.ape_materno:
                materno = self.ape_materno
            name = u"{} {} {}".format(res.ape_paterno, materno, res.nombres)
            self.env.cr.execute("""
                UPDATE minsa_agente_comunitario
                    SET name = %s
                WHERE id = %s
                """, (name, record_id,))
        return res

def write(self, values):
    res = super(AgenteComunitario, self).write(values)
    for rec in self:
        # lógica para actualizar datos desde RENIEC si aplica
        if rec.tipo_documento in [_DNI, _CARNE_EXTRANJERIA]:
            data, errors = consulta_reniec(rec, rec.tipo_documento, rec.numero_documento)
            data = data[1]
            ape_paterno = data.get('apellidoPaterno', False)
            ape_materno = data.get('apellidoMaterno', False)
            nombres = data.get('nombres', False)
            genero = rec.env['minsa.genero'].search([('codigo', '=', data.get('genero', False))], limit=1)
            fecha = data.get('fechaNacimiento', False)
            fecnac = fecha[:4] + '-' + fecha[4:6] + '-' + fecha[6:8]
            fecha_nacimiento = fecnac
            edad_year = None
            if fecha_nacimiento:
                birth_date = fields.Date.from_string(fecha_nacimiento)
                delta = date.today() - birth_date
                edad_year = delta.days // 365
            else:
                self.fecha_nacimiento._compute_edad(self)
                edad_year = self.fecha_nacimiento

            name = u"{} {} {}".format(ape_paterno, ape_materno, nombres)

            # aquí sí puedes hacer SQL para estos campos que sí existen:
            rec.env.cr.execute("""
                UPDATE minsa_agente_comunitario
                   SET ape_paterno = %s,
                       ape_materno = %s,
                       nombres = %s,
                       name = %s,
                       genero_id = %s,
                       fecha_nacimiento = %s,
                       edad = %s
                 WHERE id = %s
            """, (ape_paterno, ape_materno, nombres, name, genero.id, fecha_nacimiento, edad_year, rec.id))
        else:
            materno = rec.ape_materno or ""
            name = u"{} {} {}".format(rec.ape_paterno, materno, rec.nombres)
            rec.env.cr.execute("""
                UPDATE minsa_agente_comunitario
                   SET name = %s
                 WHERE id = %s
            """, (name, rec.id))

        # si el usuario cargó la foto y viene en values, no uses SQL para esto
        if 'foto' in values and values['foto']:
            rec.foto = values['foto']

    return res