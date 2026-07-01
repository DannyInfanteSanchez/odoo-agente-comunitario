# -- coding: utf-8 --
from odoo import http, _
from odoo.http import request
from odoo.addons.web.controllers.main import Home
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
import logging

_logger = logging.getLogger(__name__)


class ForcePasswordChange(Home):

    @http.route('/web/login', type='http', auth='none', website=True)
    def web_login(self, redirect=None, **kw):
        response = super().web_login(redirect=redirect, **kw)

        login = kw.get('login')
        password = kw.get('password')

        if login and password:
            db = request.session.db
            if db:
                user = request.env['res.users'].sudo().search(
                    [('login', '=', login)],
                    limit=1
                )
                if user and user.must_change_password:
                    return request.render(
                        'force_password_change.password_expired',
                        {
                            'error': _(
                                'Su contraseña ha expirado. '
                                'Debe cambiarla antes de continuar.'
                            )
                        }
                    )
        return response


class ForcePasswordChangeReset(AuthSignupHome):

    @http.route('/web/reset_password', type='http', auth='public', website=True)
    def web_auth_reset_password(self, *args, **kw):
        response = super().web_auth_reset_password(*args, **kw)

        try:
            token = kw.get('token')
            if token:
                user = request.env['res.users'].sudo().search(
                    [('signup_token', '=', token)],
                    limit=1
                )
                if user:
                    user.write({'must_change_password': False})
        except Exception as e:
            _logger.error(
                "Error al limpiar must_change_password: %s",
                e
            )

        return response
