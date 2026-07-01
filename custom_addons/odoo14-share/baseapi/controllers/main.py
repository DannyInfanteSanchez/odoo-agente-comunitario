# -*- coding: utf-8 -*-

import logging
import json

from functools import wraps

from odoo import http, fields
from odoo.http import request, Response
from odoo.exceptions import AccessError
from odoo.tools.safe_eval import test_python_expr

_logger = logging.getLogger(__name__)


class AuthToken(object):
    @property
    def headers(self):
        return request.httprequest.headers

    @property
    def content_type(self):
        return self.headers.get('Content-Type')

    @property
    def token(self):
        authorization = self.headers.get('Authorization', False)
        return authorization and \
            (authorization.startswith('Bearer') and authorization[7:] or authorization)

    @property
    def user(self):
        if not self.token:
            return request.env.user

        domain = [('token', '=', self.token),
                  ('is_active', '=', True),
                  ('valid_until', '>=', fields.Datetime.now())]

        usertoken = request.env['res.users.token'].sudo().search(domain, limit=1)
        if not usertoken:
            return {'error': 'El token no existe o no es válido'}

        if not usertoken or usertoken and not usertoken.user_id.has_group('baseapi.group_api_token'):
            return {'error': 'Unicamente los Usuarios Token pueden acceder a esta función'}

        return usertoken.user_id

    def check(self, method, *args, **kwargs):
        @wraps(method)
        def _check_auth(*args, **kwargs):
            if isinstance(self.user, dict):
                return self.user

            if not self.user:
                return {'error': 'No se encontró el usuario'}
            else:
                request.env.uid = self.user.id
                request.uid = self.user.id

            return method(*args, **kwargs)
        return _check_auth


authtoken = AuthToken()


class BaseGetRecords(object):
    def _get_records(self, model_name, **params):
        def response(result=None, error=False, status=200):
            return {'result': result, 'error': error, 'status': status}

        authtoken = AuthToken()
        try:
            model = request.env[model_name]
        except KeyError:
            return response(error='No se encontró el modelo', status=404)

        if not hasattr(model, '_alias_fields'):
            return response(error='El modelo no esta preparado para el servicio', status=404)

        _alias_fields = model._alias_fields

        # Calculo de dominio
        domain = []
        _limit = limit = 100
        order = None
        page = 1
        only_count = False
        only_fields = None
        # Calculo de parametros
        for param_alias, param_value in params.iteritems():
            item_domain = False
            if param_alias in _alias_fields:
                item_domain = [param_alias, '=', param_value]
            elif param_alias.endswith('__like'):
                item_domain = [param_alias[:-6], 'ilike', param_value]
            elif param_alias.endswith('__lte'):
                item_domain = [param_alias[:-5], '<=', param_value]
            elif param_alias.endswith('__lt'):
                item_domain = [param_alias[:-4], '<', param_value]
            elif param_alias.endswith('__lge'):
                item_domain = [param_alias[:-5], '>=', param_value]
            elif param_alias.endswith('__lg'):
                item_domain = [param_alias[:-4], '>', param_value]
            elif param_alias.endswith('__in'):
                error_expr = test_python_expr(expr=param_value, mode="eval")
                if error_expr:
                    return response(error='Error en la expresión del parámetro', status=500)
                try:
                    param_value = eval(param_value)
                except Exception:
                    return response(error='Error en el valor del parámetro', status=500)

                item_domain = [param_alias[:-4], 'in', param_value]
            elif param_alias == 'pagination':
                # Numero de elementos por pagina
                limit = int(param_value)
                limit = limit > 0 and min(limit, _limit) or _limit
            elif param_alias == 'order':
                order = param_value
            elif param_alias == 'page':
                page = int(param_value)
                page = page > 0 and page or 1
            elif param_alias == 'only_count' and param_value.isdigit() and int(param_value) > 0:
                only_count = True
            elif param_alias == 'only_fields':
                only_fields = param_value
            else:
                _logger.info('parametro no reconocido `{}`'.format(param_alias))
                return response(error='Parámetro no reconocido {}'.format(param_alias), status=404)
            if item_domain:
                if item_domain[0] not in _alias_fields:
                    return response(error='Parámetro "{}" no encontrado'.format(item_domain[0]), status=404)
                item_domain[0] = _alias_fields[item_domain[0]]
                domain.append(tuple(item_domain))

        offset = (page - 1) * limit
        offset = offset > 0 and offset or None
        model = request.env[model_name].sudo(authtoken.user.id)
        try:
            count = model.search_count(domain)
        except AccessError:
            return response(error='No tiene permisos para acceder a la información', status=404)
        except Exception as e:
            return response(error='Error desconocido: {}'.format(e.message), status=404)

        if only_count:
            return response(result={'count': count})

        else:
            data = model.get_json(domain=domain, order=order, limit=limit, offset=offset, only_fields=only_fields)
            res = {'data': data,
                   'meta': {'pages': count / limit + (count % limit != 0),
                            'count': count,
                            'pagination': limit}}
            return response(result=res)


class HttpController(http.Controller, BaseGetRecords):
    """
    Clase en desarrollo para consulta de los catalogos
    """

    @http.route(['/api/<string:model_name>/'],
                type='http', methods=['get'], auth='public', website=False, cors="*")
    @authtoken.check
    def get_records(self, model_name, **params):
        res = self._get_records(model_name, **params)
        if res.get('error'):
            return Response({json.dumps({'error': res.get('error')})},
                            mimetype='application/json', status=res['status'])
        else:
            return Response({json.dumps(res['result'])},
                            mimetype='application/json', status=res['status'])


Controller = HttpController  # La asisgnación es para mantener con versiones anteriores


class JsonController(http.Controller, BaseGetRecords):
    """
    Clase en desarrollo para consulta de los catalogos
    """

    @http.route(['/api/auth/get_tokens'],
                type='http', methods=['GET'], auth='public', website=False)
    def _get_records(self, model_name, **params):

        res = self._get_records(model_name, **params)
        return 'error' in res and res['error'] or res['result']
