# -- coding: utf-8 --
import logging

from odoo import api, models, fields, _
from odoo.exceptions import UserError
from odoo.addons.auth_signup.models.res_partner import now

_logger = logging.getLogger(__name__)


class ResUser(models.Model):
    _inherit = 'res.users'

    @api.onchange("diresa_id", "red_id", "establecimiento_id", "groups_id")
    def onchange_diresa_red_establecimiento(self):
        self._compute_es_grupo_diresa()
        self._compute_es_grupo_red()
        self._compute_es_grupo_establecimiento()

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
        if self.env['res.users'].has_group('minsa_regcom.group_renipress'):
            self.es_grupo_establecimiento = True
        else:
            self.es_grupo_establecimiento = False
        return self.es_grupo_establecimiento

    def _compute_es_admin(self):
        if self.env['res.users'].has_group('base.group_erp_manager'):
            self.es_grupo_admin = True
        else:
            self.es_grupo_admin = False
        return self.es_grupo_admin

    def _tipo_usuario(self, nombre_categorias):
        tipo_usuario = 'agente'
        return tipo_usuario

    def get_user_groups(self, user_id):
        # Obtener el objeto del usuario
        user = self.env['res.users'].browse(user_id)

        # Obtener los IDs de los grupos a los que pertenece el usuario
        group_ids = user.groups_id.ids

        # Obtener los objetos de los grupos a partir de los IDs
        groups = self.env['res.groups'].browse(group_ids)

        # Obtener los objetos de las categorias de los grupos a partir de los IDs
        category_ids = groups.mapped('category_id.id')
        categorys = self.env['ir.module.category'].browse(category_ids)

        # Obtener los nombres de los categorias
        category_names = categorys.mapped('name')
        return category_names

    def action_reset_password(self):
        """ create signup token for each user, and send their signup url by email """
        if self.env.context.get('install_mode', False):
            return
        if self.filtered(lambda user: not user.active):
            raise UserError(_("You cannot perform this action on an archived user."))
        # prepare reset password signup
        create_mode = bool(self.env.context.get('create_user'))

        # no time limit for initial invitation, only for reset password
        expiration = False if create_mode else now(days=+1)

        self.sudo().mapped('partner_id').signup_prepare(signup_type="reset", expiration=expiration)

        # send email to users with their signup url
        template = False
        if create_mode:
            try:
                template = self.env.ref('auth_signup.set_password_email', raise_if_not_found=False)
            except ValueError:
                pass
        if not template:
            template = self.env.ref('auth_signup.reset_password_email')
        assert template._name == 'mail.template'

        template_values = {
            'email_to': '${object.email|safe}',
            'email_cc': False,
            'auto_delete': True,
            'partner_to': False,
            'scheduled_date': False,
        }
        template.sudo().write(template_values)

        for user in self:
            if not user.email:
                raise UserError(_("Cannot send email: user %s has no email address.", user.name))
            # TDE FIXME: make this template technical (qweb)
            with self.env.cr.savepoint():
                force_send = not(self.env.context.get('import_file', False))
                template.sudo().send_mail(user.id, force_send=force_send, raise_exception=True)
            _logger.info("Password reset email sent for user <%s> to <%s>", user.login, user.email)

    diresa_id = fields.Many2one('renipress.diresa', string=u'Diresa', default=lambda self: self.env.user.diresa_id)
    red_id = fields.Many2one(
        'renipress.red',
        'Red',
        domain="[('diresa_id', '=', diresa_id)]",
        default=lambda self: self.env.user.red_id
    )
    establecimiento_id = fields.Many2one(
        'renipress.eess',
        string='Renipress',
        domain="[('red_id', '=', red_id)]",
    )
    es_grupo_diresa = fields.Boolean('Grupo Diresa', compute='_compute_es_grupo_diresa', default=False)
    es_grupo_red = fields.Boolean('Grupo Red', compute='_compute_es_grupo_red', default=False)
    es_grupo_establecimiento = fields.Boolean('Grupo Establecimiento', compute='_compute_es_grupo_establecimiento', default=False)
    es_grupo_admin = fields.Boolean('Grupo Admin', compute='_compute_es_admin', default=False)
    tipo_usuario = fields.Char('Tipo de usuario')
    nro_documento = fields.Char(string="Nro. documento")

    def actualiza_tipo_usuario_sql(self, tipo_usuario, user_id):
        query = '''
            UPDATE res_users
            SET tipo_usuario = '{0}'
            WHERE id = {1}
        '''
        query = query.format(
            tipo_usuario,
            user_id
        )
        if user_id:
            self.env.cr.execute(query)

    def write(self, val):
        if self.env.user.has_group('base.group_erp_manager') or self.env.user.id == self.id:
            if self.env.user.has_group('minsa_regcom.group_diresa') and self.env.user.id == self.id:
                if 'red_id' in val and not val.get('red_id') and len(val.keys()) >= 1:
                    raise UserError(_("Para un usuario Diresa, el campo de RED no es requerido, deje vacio ese campo."))
            if self.env.user.has_group('minsa_regcom.group_red') and self.env.user.id == self.id:
                if 'establecimiento_id' in val and not val.get('establecimiento_id') and len(val.keys()) >= 1:
                    raise UserError(_("Para un usuario RED, el campo de Renipress no es requerido, deje vacio ese campo."))
            res = super(ResUser, self.sudo()).write(val)
            nombre_categoria = self.get_user_groups(self.id)
            tipo_usuario = self._tipo_usuario(nombre_categoria)
            self.actualiza_tipo_usuario_sql(tipo_usuario, self.id)
            return res
        else:
            if (self.env.user.has_group('minsa_regcom.group_diresa') and not self.red_id) or (self.env.user.has_group('minsa_regcom.group_red') and not self.establecimiento_id):
                raise UserError(_("No puede modificar los datos de otro usuario de otra Diresa o de otra Red"))
            else:
                res = super(ResUser, self.sudo()).write(val)
                nombre_categoria = self.get_user_groups(self.id)
                tipo_usuario = self._tipo_usuario(nombre_categoria)
                self.actualiza_tipo_usuario_sql(tipo_usuario, self.id)
                return res

    @api.model_create_multi
    def create(self, vals):
        flat_diccionario = False
        if type(vals) == 'dict':
            vals = list(vals.items())
            flat_diccionario = True
        print("** flat_diccionario=", flat_diccionario)
        if self.env.user.has_group('base.group_erp_manager'):
            if flat_diccionario:
                vals = dict(vals)
            print("** vals=", vals)
            users = super(ResUser, self).create(vals)
            nombre_categoria = self.get_user_groups(users.id)
            tipo_usuario = self._tipo_usuario(nombre_categoria)
            self.actualiza_tipo_usuario_sql(tipo_usuario, users.id)
            return users
        else:
            print("************ context('origen')=", self._context.get('origen'))
            group_adminregcom_id = 'in_group_{}'.format(self.sudo().env.ref('minsa_regcom.group_adminregcom').id)
            base_group_id = 'in_group_{}'.format(self.sudo().env.ref('minsa_regcom.group_base_user').id)
            group_diresa_id = 'in_group_{}'.format(self.sudo().env.ref('minsa_regcom.group_diresa').id)
            group_red_id = 'in_group_{}'.format(self.sudo().env.ref('minsa_regcom.group_red').id)
            group_renipress_id = 'in_group_{}'.format(self.sudo().env.ref('minsa_regcom.group_renipress').id)
            print('***** vals:', vals)
            # Creación de perfil para Agente Comunitario
            if self.env.user.has_group('minsa_regcom.group_diresa'):
                if ('red_id' not in vals[0] or vals[0].get('red_id') == False) and len(vals[0].keys()) >= 1:
                    raise UserError(_("Un usuario Diresa, solo puede crear usuarios de RED, el campo de RED es requerido"))
                vals[0].update({
                    base_group_id: True,
                    group_adminregcom_id: False,
                    group_diresa_id: False,
                    group_red_id: True,
                    group_renipress_id: False,
                    'sel_groups_1_9_10': 1
                })
            if self.env.user.has_group('minsa_regcom.group_red'):
                if ('establecimiento_id' not in vals[0] or vals[0].get('establecimiento_id') == False) and len(vals[0].keys()) >= 1:
                    raise UserError(_("Un usuario Red, solo puede crear usuarios Renipress, el campo de Renipress es requerido"))
                vals[0].update({
                    base_group_id: True,
                    group_adminregcom_id: False,
                    group_diresa_id: False,
                    group_red_id: False,
                    group_renipress_id: True,
                    'sel_groups_1_9_10': 1
                })

            if flat_diccionario:
                vals = dict(vals)
            users = super(ResUser, self.sudo()).create(vals)
            nombre_categoria = self.get_user_groups(users.id)
            tipo_usuario = self._tipo_usuario(nombre_categoria)
            self.actualiza_tipo_usuario_sql(tipo_usuario, users.id)
            return users

    def unlink(self):
        self.write({'active': False})

    _sql_constraints = [
        ('nro_documento_uniq', 'unique (nro_documento)',
         "Nro. documento ya existe !")]
