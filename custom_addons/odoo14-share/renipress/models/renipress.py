# -*- coding: utf-8 -*-

from odoo import api, fields, models


class InstitucionBase(models.AbstractModel):
    _inherit = 'res.country.lugar'

    _name = 'renipress.institucion_base'
    _description = u'Institución Base'

    name = fields.Char('Nombre', size=100, required=True)
    active = fields.Boolean('Activo/Inactivo', default=True)


class Diresa(models.Model):
    _inherit = 'renipress.institucion_base'
    _name = 'renipress.diresa'

    _description = u'Diresa'

    name = fields.Char('Diresa')
    codigo_diresa = fields.Char(
        u'Código',
        size=2,
        required=True,
        oldname='codigo')
    departamento_ids = fields.Many2many(
        'res.country.state',
        'renipress_diresa_departamento_rel',
        'diresa_id', 'departamento_id',
        'Departamentos', readonly=True)

    red_ids = fields.One2many('renipress.red', 'diresa_id', 'Redes')

    _sql_constraints = [
        ('codigo_unique', 'unique(codigo_diresa)',
         'El código de la Diresa ser único!'),
        ('codigo_name', 'unique(active, name)',
         u'El nombre de la Diresa ser único!'),
    ]


class Red(models.Model):
    _inherit = 'renipress.institucion_base'
    _name = 'renipress.red'

    _description = u'Red de Salud'

    name = fields.Char('Red')
    codigo_red = fields.Char(
        'Código', size=2, required=True, oldname='codigo')

    diresa_id = fields.Many2one(
        'renipress.diresa', 'Diresa', required=True)
    departamento_id = fields.Many2one(
        related='diresa_id.departamento_id', store=True)

    microred_ids = fields.One2many(
        'renipress.microred', 'red_id', 'Microredes')

    _sql_constraints = [
        ('codigo_unique', 'unique(diresa_id, codigo_red)',
         u'El código de la Red de Salud ser único!'),
        ('codigo_name', 'unique(diresa_id, codigo_red, name)',
         u'El Codigo y Red deben ser únicos!'),
    ]

    def name_get(self):
        res = []
        for record in self:
            name = record.name
            if record.diresa_id:
                name = u'%s|%s' % (record.diresa_id.name or '', name)
            res.append((record.id, name))
        return res


class Microred(models.Model):
    _inherit = 'renipress.institucion_base'
    _name = 'renipress.microred'

    _description = u'Micro Red de Salud'

    name = fields.Char('Microred')
    codigo_microred = fields.Char(
        'Código',
        size=2,
        required=True,
        oldname='codigo')

    red_id = fields.Many2one('renipress.red', 'Red', required=True)
    diresa_id = fields.Many2one(
        'renipress.diresa',
        'Diresa',
        related='red_id.diresa_id',
        store=True,
        readonly=True)

    eess_ids = fields.One2many(
        'renipress.eess',
        'microred_id',
        'Establecimientos')

    _sql_constraints = [
        ('codigo_unique', 'unique(red_id, codigo_microred)',
         u'El código de la MicroRed debe ser único!'),
        ('codigo_name', 'unique(red_id, active, name)',
         u'El nombre de la MicroRed debe ser único!'),
    ]

    def name_get(self):
        res = []
        for record in self:
            name = record.name
            if record.diresa_id and record.red_id:
                name = u'%s|%s|%s' % (
                    record.diresa_id.name or '', record.red_id.name or '', name)
            res.append((record.id, name))
        return res


SELECTION_INSTITUCION = [
    ('1', 'MINSA'),
    ('2', 'ESSALUD'),
    ('3', 'SANIDAD DEL EJERCITO DEL PERU'),
    ('4', 'SANIDAD DE LA FUERZA AEREA DEL PERU'),
    ('5', 'SANIDAD DE LA POLICIA NACIONAL DEL PERU'),
    ('6', 'SANIDAD DE LA MARINA DE GUERRA DEL PERU'),
    ('7', 'GOBIERNO REGIONAL'),
    ('8', 'MUNICIPALIDAD PROVINCIAL'),
    ('9', 'MUNICIPALIDAD DISTRITAL'),
    ('10', 'PRIVADO'),
    ('13', 'INPE'),
    ('11', 'OTRO'),
]

SELECTION_CLASIFICACION = [
    ('1', 'PUESTOS DE SALUD O POSTAS DE SALUD'),
    ('2', 'CENTROS DE SALUD O CENTROS MEDICOS'),
    ('3', 'POLICLINICOS'),
    ('4', 'CENTROS MEDICOS ESPECIALIZADOS'),
    ('5', 'CONSULTORIOS MEDICOS Y DE OTROS PROFESIONALES DE LA SALUD'),
    ('6', 'HOSPITALES O CLINICAS DE ATENCION GENERAL'),
    ('7', 'HOSPITALES O CLINICAS DE ATENCION ESPECIALIZADA'),
    ('8', 'CENTROS DE SALUD CON CAMAS DE INTERNAMIENTO'),
    ('9', 'CENTROS DE ATENCION GERIATRICA'),
    ('10', 'INSTITUTOS DE SALUD ESPECIALIZADOS'),
    ('11', 'PATOLOGIA CLINICA'),
    ('12', 'ANATOMIA PATOLOGICA'),
    ('13', 'DIAGNOSTICO POR IMAGENES'),
    ('14', 'MEDICINA NUCLEAR'),
    ('15', 'RADIOTERAPIA'),
    ('16', 'MEDICINA FISICA'),
    ('17', 'REHABILITACION'),
    ('18', 'HEMODIALISIS'),
    ('19', 'LITOTRIPSIA'),
    ('20', 'MEDICINA HIPERBARICA'),
    ('21', 'ENDOSCOPIAS'),
    ('22', 'COLPOSCOPIAS'),
    ('23', 'SERVICIO DE TRASLADO DE PACIENTES'),
    ('24', 'ESTABLECIMIENTOS DE RECUPERACION O REPOSO'),
    ('25', 'CENTROS OPTICOS'),
    ('26', 'LABORATORIOS DE PROTESIS DENTAL'),
    ('27', 'ORTOPEDIAS Y SERVICIOS DE PODOLOGIA'),
    ('28', 'CENTROS DE ATENCION PARA DEPENDIENTES A SUSTANCIAS PSICOACTIVAS Y OTRAS DEPENDENCIAS'),
    ('29', 'CENTROS DE VACUNACION'),
    ('30', 'CENTROS DE MEDICINA ALTERNATIVA'),
    ('31', 'CENTRO ODONTOLOGICO'),
    ('33', 'ATENCION DOMICILIARIA'),
    ('34', 'ATENCION PRE HOSPITALARIA'),
    ('35', 'AISPED'),
    ('36', 'CENTRO DE ATENCIÓN AMBULATORIA'),
    ('37', 'PLATAFORMA ITINERANTE DE ATENCIÓN ACCIÓN SOCIAL'),
    ('38', 'CENTROS DE ATENCION DE SALUD PARA PERSONAS DEPENDIENTES DE SUSTANCIAS PSICOACTIVAS Y SUS RESPECTIVAS FAMILIAS (TIPO I)'),
    ('39', 'CENTROS DE ATENCION DE SALUD PARA PERSONAS DEPENDIENTES DE SUSTANCIAS PSICOACTIVAS Y SUS RESPECTIVAS FAMILIAS (TIPO II)'),
]

SELECTION_TIPO = [
    ('1', 'ESTABLECIMIENTO DE SALUD CON INTERNAMIENTO'),
    ('2', 'ESTABLECIMIENTO DE SALUD SIN INTERNAMIENTO'),
    ('3', 'SERVICIO MÉDICO DE APOYO'),
    ('4', 'OFERTA FLEXIBLE'),
    ('5', 'COMUNIDADES TERAPÉUTICAS'),
]

SELECTION_ESTADO = [
    ('1', 'ACTIVADO'),
    ('0', 'DESACTIVADO'),
]

SELECTION_CONDICION = [
    ('1', 'CIERRE DEFINITIVO'),
    ('2', 'CIERRE TEMPORAL'),
    ('3', 'EN FUNCIONAMIENTO'),
    ('4', 'INOPERATIVO'),
    ('5', 'RESTRICCIÓN DE SERVICIOS'),
]

SELECTION_CATEGORIA = [
    ('1', 'I-1'),
    ('2', 'I-2'),
    ('3', 'I-3'),
    ('4', 'I-4'),
    ('5', 'II-1'),
    ('6', 'II-2'),
    ('7', 'II-E'),
    ('8', 'III-1'),
    ('9', 'III-2'),
    ('10', 'III-E'),
    ('99', 'Sin Categoría'),
]


class EeSs(models.Model):
    _inherit = 'renipress.institucion_base'
    _name = 'renipress.eess'

    _description = u'Establecimiento de Salud'

    name = fields.Char('Nombre')
    codigo_eess = fields.Char(
        'Código',
        size=8,
        required=True,
        oldname='codigo')

    direccion = fields.Char('Dirección')
    institucion = fields.Selection(
        SELECTION_INSTITUCION, u'Institución')
    clasificacion = fields.Selection(
        SELECTION_CLASIFICACION, u'Clasificación')
    tipo = fields.Selection(SELECTION_TIPO, 'Tipo')

    microred_id = fields.Many2one(
        'renipress.microred',
        'Microred',
        required=True)
    red_id = fields.Many2one(
        'renipress.red',
        'Red',
        related='microred_id.red_id',
        store=True,
        readonly=True)
    diresa_id = fields.Many2one(
        'renipress.diresa',
        'Diresa',
        related='red_id.diresa_id',
        store=True,
        readonly=True)

    coor_norte = fields.Float('Coor. Norte', digits=(11, 6))
    coor_este = fields.Float('Coor. Este', digits=(11, 6))

    categoria = fields.Selection(SELECTION_CATEGORIA, u'Categoría')
    estado = fields.Selection(SELECTION_ESTADO, u'Estado')
    condicion = fields.Selection(SELECTION_CONDICION, u'Condición')
    telefono = fields.Char('Teléfono')
    responsable = fields.Char('Director/Responsable')
    ruc = fields.Char('Nro RUC')
    inicio_actividad = fields.Char('Inicio de Actividad')

    def name_get(self):
        return [(obj.id, u'{} - {} - {}'.format(
            obj.codigo_eess, obj.diresa_id.name, obj.name
        )
        ) for obj in self]

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if operator not in ('ilike', 'like', '=', '=like', '=ilike'):
            return super(EeSs, self).name_search(name, args, operator, limit)
        args = args or []
        domain = ['|', ('codigo_eess', operator, name),
                  ('name', operator, name)]
        recs = self.search(domain + args, limit=limit)
        return recs.name_get()

    _sql_constraints = [
        ('codigo_unique', 'unique(codigo_eess)',
         u'El código del Establecimiento de Salud ser único!'),
    ]
