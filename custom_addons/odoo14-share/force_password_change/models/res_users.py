# -- coding: utf-8 --
from odoo import models, fields, api, SUPERUSER_ID, _
from odoo.exceptions import AccessDenied
import logging

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    must_change_password = fields.Boolean(
        string='Debe cambiar contraseña',
        default=False
    )

    @classmethod
    def authenticate(cls, db, login, password, user_agent_env):
        uid = super().authenticate(db, login, password, user_agent_env)
        if not uid:
            return uid

        registry = cls.pool
        with registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            user = env['res.users'].browse(uid)

            if user.must_change_password:
                _logger.info("Login bloqueado: usuario %s debe cambiar contraseña", login)
                raise AccessDenied(_("Debe cambiar su contraseña antes de continuar."))

        return uid