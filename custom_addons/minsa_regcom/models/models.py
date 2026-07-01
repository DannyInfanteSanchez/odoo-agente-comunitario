# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, tools
from datetime import datetime
from .helper import _diferencia_fecha_dias
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


TIPO_REGISTRO_AGENTE = 'agente'
TIPO_REGISTRO_COMITE = 'comite'
TIPO_REGISTRO = [
    (TIPO_REGISTRO_AGENTE, 'Agente Comunitario de salud'),
    (TIPO_REGISTRO_COMITE, 'Comite Comunitario'),
]

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

ESTADO_BORRADOR = 'borrador'
ESTADO_VALIDADO = 'validado'
ESTADO_VALIDADO_2 = 'validado2'

ESTADO_REGISTRO = [
    (ESTADO_BORRADOR, 'Borrador'),
    (ESTADO_VALIDADO, 'Validado RED'),
    (ESTADO_VALIDADO_2, 'Validado DIRESA')
]

ESTADO_ACTIVO = 'activo'
ESTADO_NOACTIVO = 'noactivo'

ESTADO_PERSONA = [
    (ESTADO_ACTIVO, 'Activo'),
    (ESTADO_NOACTIVO, 'No Activo'),
]

ARCHIVO_ADJUNTO = 'adjunto'
ARCHIVO_URL = 'url'

SELECTION_TIPO_ARCHIVO = [
    (ARCHIVO_ADJUNTO, 'Archivo adjunto'),
    (ARCHIVO_URL, 'URL del archivo'),
]


class Documento(models.Model):
    _name = 'minsa.documento'
    _description = 'Tipo de Archivo adjuntar'
    _order = 'codigo'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    codigo = fields.Char(string=u'Código', size=4, required=True, tracking=True)
    name = fields.Char(string='Tipo de Archivo', required=True, tracking=True)
    active = fields.Boolean(default=True, tracking=True)

    def unlink(self):
        self.write({'active': False})

    _sql_constraints = [
        ('uniq_codigo', 'UNIQUE(codigo)', u"Código ya existe, verifique"),
        ('uniq_name', 'UNIQUE(name)', u"Nombre ya existe, verifique")
    ]


class Genero(models.Model):
    _name = 'minsa.genero'
    _description = 'Genero de la persona'
    _order = 'codigo'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    codigo = fields.Char(string=u'Código', size=4, required=True, tracking=True)
    name = fields.Char(string='Nombre', required=True, tracking=True)
    active = fields.Boolean(default=True, tracking=True)

    def unlink(self):
        self.write({'active': False})

    _sql_constraints = [
        ('uniq_codigo', 'UNIQUE(codigo)', u"Código ya existe, verifique"),
        ('uniq_name', 'UNIQUE(name)', u"Nombre ya existe, verifique")
    ]


class Etnia(models.Model):
    _name = 'minsa.etnia'
    _description = 'Etnia de la persona'
    _order = 'codigo'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    codigo = fields.Char(string=u'Código', size=4, required=True, tracking=True)
    name = fields.Char(string='Nombre', required=True, tracking=True)
    active = fields.Boolean(default=True, tracking=True)

    def unlink(self):
        self.write({'active': False})

    _sql_constraints = [
        ('uniq_codigo', 'UNIQUE(codigo)', u"Código ya existe, verifique"),
        ('uniq_name', 'UNIQUE(name)', u"Nombre ya existe, verifique")
    ]


class Seguro(models.Model):
    _name = 'minsa.seguro'
    _description = 'Tipo de seguro'
    _order = 'codigo'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    codigo = fields.Char(string=u'Código', size=4, required=True, tracking=True)
    name = fields.Char(string='Nombre', required=True, tracking=True)
    active = fields.Boolean(default=True, tracking=True)

    def unlink(self):
        self.write({'active': False})

    _sql_constraints = [
        ('uniq_codigo', 'UNIQUE(codigo)', u"Código ya existe, verifique"),
        ('uniq_name', 'UNIQUE(name)', u"Nombre ya existe, verifique")
    ]


class Dialecto(models.Model):
    _name = 'minsa.dialecto'
    _description = 'Idioma dialecto'
    _order = 'codigo'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    codigo = fields.Char(string=u'Código', size=4, required=True, tracking=True)
    name = fields.Char(string='Nombre', required=True, tracking=True)
    active = fields.Boolean(default=True, tracking=True)

    def unlink(self):
        self.write({'active': False})

    _sql_constraints = [
        ('uniq_codigo', 'UNIQUE(codigo)', u"Código ya existe, verifique"),
        ('uniq_name', 'UNIQUE(name)', u"Nombre ya existe, verifique")
    ]


class GradoInstruccion(models.Model):
    _name = 'minsa.grado.instruccion'
    _description = u'Grado de instrucción de la persona'
    _order = 'codigo'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    codigo = fields.Char(string=u'Código', size=4, required=True, tracking=True)
    name = fields.Char(string='Nombre', required=True, tracking=True)
    active = fields.Boolean(default=True, tracking=True)

    def unlink(self):
        self.write({'active': False})

    _sql_constraints = [
        ('uniq_codigo', 'UNIQUE(codigo)', u"Código ya existe, verifique"),
        ('uniq_name', 'UNIQUE(name)', u"Nombre ya existe, verifique")
    ]


class TipoVoluntariado(models.Model):
    _name = 'minsa.tipo.voluntariado'
    _description = 'Tipo de voluntariado'
    _order = 'codigo'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    codigo = fields.Char(string=u'Código', size=4, required=True, tracking=True)
    name = fields.Char(string='Nombre', required=True, tracking=True)
    active = fields.Boolean(default=True, tracking=True)

    def unlink(self):
        self.write({'active': False})

    _sql_constraints = [
        ('uniq_codigo', 'UNIQUE(codigo)', u"Código ya existe, verifique"),
        ('uniq_name', 'UNIQUE(name)', u"Nombre ya existe, verifique")
    ]


class OperadorMobil(models.Model):
    _name = 'minsa.operador.mobil'
    _description = 'Operador Mobil'
    _order = 'codigo'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    codigo = fields.Char(string=u'Código', size=4, required=True, tracking=True)
    name = fields.Char(string='Nombre', required=True, tracking=True)
    active = fields.Boolean(default=True, tracking=True)

    def unlink(self):
        self.write({'active': False})

    _sql_constraints = [
        ('uniq_codigo', 'UNIQUE(codigo)', u"Código ya existe, verifique"),
        ('uniq_name', 'UNIQUE(name)', u"Nombre ya existe, verifique")
    ]


class NivelAgente(models.Model):
    _name = 'minsa.nivel.agente'
    _description = 'Nivel Agente comunitario'
    _order = 'id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Nombre', required=True, tracking=True)
    active = fields.Boolean(default=True, tracking=True)

    def unlink(self):
        self.write({'active': False})

    _sql_constraints = [
        ('uniq_name', 'UNIQUE(name)', u"Nombre ya existe, verifique")
    ]


class EstandarLaboral(models.Model):
    _name = 'minsa.estandar.laboral'
    _description = 'Estándar de Competencia Laboral'
    _order = 'id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Nombre', required=True, tracking=True)
    active = fields.Boolean(default=True, tracking=True)

    def unlink(self):
        self.write({'active': False})

    _sql_constraints = [
        ('uniq_name', 'UNIQUE(name)', u"Nombre ya existe, verifique")
    ]


class Registro(models.Model):
    _name = 'minsa.registro'
    _description = u'Registro Agente comunitario de salud'
    _order = 'create_date desc, diresa_id'
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

    @api.onchange('diresa_id')
    def _onchange_diresa_id(self):
        lnacional = self._compute_es_grupo_nacional()
        ldiresa = self._compute_es_grupo_diresa()
        lred = self._compute_es_grupo_red()
        lestablecimiento = self._compute_es_grupo_establecimiento()
        ladmin = self._compute_es_admin()
        return {
            "value": {
                'es_grupo_nacional': lnacional,
                'es_grupo_diresa': ldiresa,
                'es_grupo_red': lred,
                'es_grupo_establecimiento': lestablecimiento,
                'es_grupo_admin': ladmin
            }
        }

    @api.constrains('detalle_ids')
    def _validate_registro_detalle(self):
        for record in self:
            if len(record.detalle_ids) == 0:
                raise ValidationError(
                    _("Falta que ingrese los miembros del agente/comité comunitario, verifique"
                      ))

    @api.constrains('carga_documento')
    def _constrains_carga_documento(self):
        for record in self:
            if not record.carga_documento:
                raise ValidationError(_("Debe adjuntar al menos un archivo en el campo 'Archivo'."))
        domain = [("key", "=", "cabecera_cantidad_archivos")]
        record = self.env["ir.config_parameter"].search(domain, limit=1)
        if not record or not record.value:
            raise ValidationError("No esta configurado el parámetro de CABECERA CANTIDAD DE ARCHIVOS")
        if len(self.carga_documento) > int(record.value):
            raise ValidationError(
                _("Solo puedo adjuntar hasta %s documentos, verifique" % (record.value))
            )

    @api.onchange("tipo_registro")
    def _onchange_tipo_registro(self):
        # Validamos tipo registro
        if self.tipo_registro == TIPO_REGISTRO_AGENTE:
            self.name = False
            self.tipo_archivo = ARCHIVO_ADJUNTO
            return {
                'value': {
                    'name': '',
                    'tipo_archivo': ARCHIVO_ADJUNTO
                }
            }

    def action_validar(self):
        timezone = self._context.get('tz')
        if not timezone:
            timezone = self.env.user.partner_id.tz or 'UTC'
        timezone = tools.ustr(timezone).encode('utf-8')
        for record in self:
            if not record.diresa_id or \
                not record.establecimiento_id or \
                    record.cantidad_detalle == 0:
                        raise ValidationError(
                            _("Falta que complete el ingreso de datos, verifique"))
            if self.estado == ESTADO_BORRADOR and not (self.es_grupo_red or self.es_grupo_admin):
                raise ValidationError(
                    _("Solo usuarios del perfil de RED, AdminRegCom o Admin pueden VALIDAR, verifique"))
            if self.estado == ESTADO_VALIDADO and not (self.es_grupo_diresa or self.es_grupo_admin):
                raise ValidationError(
                    _("Solo usuarios del perfil de DIRESA, AdminRegCom o Admin pueden VALIDAR, verifique"))
            if self.estado == ESTADO_BORRADOR:
                record.estado = ESTADO_VALIDADO
            elif self.estado == ESTADO_VALIDADO:
                record.estado = ESTADO_VALIDADO_2
            record.valida_date = datetime.now()

    def action_borrador(self):
        for record in self:
            record.estado = ESTADO_BORRADOR

    def action_revalidar(self):
        timezone = self._context.get('tz')
        if not timezone:
            timezone = self.env.user.partner_id.tz or 'UTC'
        timezone = tools.ustr(timezone).encode('utf-8')
        for record in self:
            record.revalida_date = datetime.now()

    @api.depends('detalle_ids')
    def compute_cantidad_miembros(self):
        for record in self:
            record.cantidad_detalle = len(self.detalle_ids)

    @api.depends('detalle_ids', 'valida_date', 'revalida_date')
    def _compute_evalua_revalida(self):
        domain = [("key", "=", "tiempo_dias_validar_registro_agente")]
        record_parameter = self.env["ir.config_parameter"].search(domain, limit=1)
        if record_parameter and record_parameter.value:
            for record in self:
                if not record.valida_date or record.estado == 'borrador':
                    record.evalua_revalida = '0'
                else:
                    fecha_inicio = record.valida_date
                    if record.revalida_date:
                        fecha_inicio = record.revalida_date
                    dias_transcurridos = _diferencia_fecha_dias(self, fecha_inicio.date(), fields.date.today())
                    if dias_transcurridos > int(record_parameter.value):
                        record.evalua_revalida = '1'
                    else:
                        record.evalua_revalida = '0'

    name = fields.Char(string='Nombre comite', tracking=True)
    diresa_id = fields.Many2one(
        'renipress.diresa',
        string=u'Diresa',
        tracking=True,
        required=True,
        default=lambda self: self.env.user.diresa_id.id or False
    )
    establecimiento_id = fields.Many2one(
        'renipress.eess',
        string=u'RENIPRESS',
        tracking=True,
        required=True,
        default=lambda self: self.env.user.establecimiento_id.id or False
    )
    red_id = fields.Many2one(related='establecimiento_id.red_id', store=True)
    ubigeo = fields.Char(related='establecimiento_id.ubigeo', store=True)
    renipress = fields.Char(related='establecimiento_id.codigo_eess', store=True)
    departamento_id = fields.Many2one(related='establecimiento_id.departamento_id', store=True)
    provincia_id = fields.Many2one(related='establecimiento_id.provincia_id', store=True)
    distrito_id = fields.Many2one(related='establecimiento_id.distrito_id', store=True)
    tipo_registro = fields.Selection(selection=TIPO_REGISTRO, string='Tipo registro', default=TIPO_REGISTRO_AGENTE, tracking=True)
    tipo_archivo = fields.Selection(selection=SELECTION_TIPO_ARCHIVO, string='Tipo de archivo', default=ARCHIVO_ADJUNTO, tracking=True)
    url_documento = fields.Char(string='URL Documento', tracking=True)
    carga_documento = fields.Many2many(
        "ir.attachment", "doc_registro_attach_ref",
        string="Archivo", tracking=True,
        help="Adjunte archivo")
    detalle_ids = fields.One2many('minsa.registro.detalle', 'registro_id', string='Detalle Agente Comunitario de Salud')
    cantidad_detalle = fields.Integer('Cant.Miembros', compute='compute_cantidad_miembros', store=True)
    es_grupo_nacional = fields.Boolean(
        'Grupo Nacional',
        compute='_compute_es_grupo_nacional',
        default=lambda self: self.env['res.users'].has_group('minsa_regcom.group_nacional')
    )
    create_date = fields.Datetime('Fecha registro', index=True, readonly=True)
    valida_date = fields.Datetime('Fecha validación', index=True, readonly=True, tracking=True)
    revalida_date = fields.Datetime('Fecha revalidación', index=True, readonly=True, tracking=True)
    es_grupo_diresa = fields.Boolean('Grupo Diresa', compute='_compute_es_grupo_diresa', default=lambda self: self.env['res.users'].has_group('minsa_regcom.group_diresa'))
    es_grupo_red = fields.Boolean('Grupo Red', compute='_compute_es_grupo_red', default=lambda self: self.env['res.users'].has_group('minsa_regcom.group_red'))
    es_grupo_establecimiento = fields.Boolean('Grupo Establecimiento', compute='_compute_es_grupo_establecimiento', default=lambda self: self.env['res.users'].has_group('minsa_regcom.group_establecimiento'))
    es_grupo_admin = fields.Boolean('Grupo Admin', compute='_compute_es_admin', default=lambda self: self.env['res.users'].has_group('base.group_erp_manager') or self.env['res.users'].has_group('minsa_regcom.group_adminregcom'))
    estado = fields.Selection(selection=ESTADO_REGISTRO, string='Estado', default=ESTADO_BORRADOR, tracking=True)
    es_grupo_red = fields.Boolean('Grupo Red', compute='_compute_es_grupo_red', default=lambda self: self.env['res.users'].has_group('minsa_regcom.group_red'))
    evalua_revalida = fields.Integer('Evalua revalida', compute='_compute_evalua_revalida', store=True)
    active = fields.Boolean(default=True, tracking=True)

    def unlink(self):
        self.write({'active': False})

    def write(self, val):
        self._constrains_carga_documento()
        res = super(Registro, self.sudo()).write(val)
        return res

    @api.model_create_multi
    def create(self, vals):
        self._constrains_carga_documento()
        res = super(Registro, self.sudo()).create(vals)
        return res

    _sql_constraints = [
        ('uniq_diresa_renipress_tipo_registro_name_fecha',
         'UNIQUE(diresa_id,establecimiento_id,tipo_registro,name,create_date)', "Registro ya existe, debe ser único: Diresa-Renipress-Tipo registro-Nombre comite y fecha registro, verifique")
    ]


class RegistroDetalle(models.Model):
    _name = 'minsa.registro.detalle'
    _description = u'Registo Detalle Agente Comunitario de Salud'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.constrains('fecha_inicio', 'fecha_fin')
    def _check_fechas(self):
        for record in self:
            if record.fecha_inicio and record.fecha_fin:
                if record.fecha_fin < record.fecha_inicio:
                    raise ValidationError(
                        _("La fecha final no puede ser menor a la fecha de inicio, verifique"))
                if record.fecha_fin == record.fecha_inicio:
                    raise ValidationError(
                        _("La fecha inicio y fecha final no pueden ser iguales, verifique"))

    registro_id = fields.Many2one('minsa.registro', string='Registro comunitario', ondelete='cascade')
    diresa_id = fields.Many2one(related="registro_id.diresa_id", store=True)
    establecimiento_id = fields.Many2one(related="registro_id.establecimiento_id", store=True)
    create_ficha = fields.Datetime(related="registro_id.create_date", store=True)
    valida_date = fields.Datetime(related="registro_id.valida_date", store=True)
    revalida_date = fields.Datetime(related="registro_id.revalida_date", store=True)
    evalua_revalida = fields.Integer(related="registro_id.evalua_revalida", store=True)
    red_id = fields.Many2one(related='establecimiento_id.red_id', store=True)
    ubigeo = fields.Char(related='establecimiento_id.ubigeo', store=True)
    renipress = fields.Char(related='establecimiento_id.codigo_eess', store=True)
    departamento_id = fields.Many2one(related='establecimiento_id.departamento_id', store=True)
    provincia_id = fields.Many2one(related='establecimiento_id.provincia_id', store=True)
    distrito_id = fields.Many2one(related='establecimiento_id.distrito_id', store=True)
    agente_comunitario_id = fields.Many2one('minsa.agente.comunitario', string='Agente Comunitario de Salud', required=True, tracking=True)
    tipo_documento = fields.Selection(related="agente_comunitario_id.tipo_documento")
    numero_documento = fields.Char(related="agente_comunitario_id.numero_documento", store=True)
    name = fields.Char(related="agente_comunitario_id.name", store=True)
    celular = fields.Char(related="agente_comunitario_id.celular", string="Celular")
    fecha_inicio = fields.Date(
        "Fecha inicio Act.",
        tracking=True
    )
    fecha_fin = fields.Date(
        "Fecha fin Act.",
        tracking=True
    )
    carga_documento = fields.Many2many(
        "ir.attachment", "doc_registro_detalle_attach_ref",
        string="Archivo", tracking=True,
        help="Adjunte archivo")
    observacion = fields.Text(string=u"Observación", tracking=True)
    estado = fields.Selection(selection=ESTADO_PERSONA, string='Estado', default=ESTADO_ACTIVO, tracking=True)
    registro_estado = fields.Selection(related='registro_id.estado', string="Registro Estado")

    @api.constrains('carga_documento')
    def _constrains_carga_documento(self):
        domain = [("key", "=", "detalle_cantidad_archivos")]
        record = self.env["ir.config_parameter"].search(domain, limit=1)
        if not record or not record.value:
            raise ValidationError("No esta configurado el parámetro de DETALLE CANTIDAD DE ARCHIVOS")
        if len(self.carga_documento) > int(record.value):
            raise ValidationError(
                _("Solo puedo adjuntar hasta %s documentos en agente comunitario %s, verifique" % (record.value, self.agente_comunitario_id.name))
            )

    def accion_estado(self):
        if self.estado == 'activo':
            self.write({'estado': 'noactivo'})
        else:
            self.write({'estado': 'activo'})

    _sql_constraints = [
        ('uniq_registro_id_tipo_documento_numero_documento',
         'UNIQUE(registro_id,agente_comunitario_id)',
         'Registro de voluntario existente, verifique')
    ]
