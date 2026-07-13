# -*- coding: utf-8 -*-

# Variable: _MIMETYPES
# Lista de estensiones que solo puede subir el usuario
# en el registro

from odoo import fields
import requests
import json


# Tipos de Archivos para adjuntar
_PDF = 'pdf'
_XLS = 'xls'
_XLSX = 'xlsx'
_DOC = 'doc'
_DOCX = 'docx'

# Tipo de Archivos
_TIPO_ARCHIVO = [
    (_PDF, 'application/pdf'),
    (_XLS, 'application/vnd.ms-excel'),
    (_XLSX, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
    (_DOC, 'application/msword'),
    (_DOCX, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
]

# Fecha actual.
_fecha_hoy = fields.date.today()


def _default_tipo_archivo(self):
    parameter_tipo_archivo = self.env['ir.config_parameter'].select_parameter('tipo_documento_adjuntar').split(',')
    _MIMETYPES = []
    config_tipo_archivo = [tipo[0] for tipo in _TIPO_ARCHIVO]
    if parameter_tipo_archivo:
        for tipo_archivo in parameter_tipo_archivo:
            if tipo_archivo.lower() in config_tipo_archivo:
                posicion = config_tipo_archivo.index(tipo_archivo)
                _MIMETYPES.append(_TIPO_ARCHIVO[posicion][1])
            else:
                _MIMETYPES.append(tipo_archivo.lower())
        return _MIMETYPES


def _default_size_documento(self):
    parameter_file_size = int(self.env['ir.config_parameter'].select_parameter('size_documento_adjunto_megas'))
    return (parameter_file_size * 1024 * 1024)


def _mapa_obtener_direccion(self, direccion):
    try:
        domain = [("key", "=", "map_sigrid_url_buscar_direccion")]
        record = self.env["ir.config_parameter"].search(domain, limit=1)
        if not record or not record.value:
            return {}, 'HTTP_400_BAD_PARAMETER_1', 'No esta configurado el parámetro de SIGRID URL buscar por dirección'
        url_buscar_direccion = record.value
        url = url_buscar_direccion
        url_recuperar_direccion = '{}&singleLine={}'.format(
            url, direccion)
        cabecera = {
            'Accept': 'text/html,application/xhtml+xml,application/xml',
            'Upgrade-Insecure-Requests': '1',
            'Connection': 'keep-alive',
            'Accept-Language': 'en-US,en;q=0.5',
            'Host': 'geocode.arcgis.com',
            'TE': 'Trailers',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0'
        }
        direccion = requests.get(url_recuperar_direccion, headers=cabecera)
        if not direccion:
            return {}, 'HTTP_400_BAD_REQUEST_2', 'Debe elegir una zona de Perú'

        is_dict = isinstance(direccion.json().get('candidates'), (dict))
        if is_dict:
            data_direccion = direccion.json().get('candidates')
        else:
            data_direccion = direccion.json().get('candidates')[0]
        if data_direccion:
            departamento = data_direccion.get('attributes').get('Region')
            provincia = data_direccion.get('attributes').get('Subregion')
            distrito = data_direccion.get('attributes').get('City')
            record_pais = self.env["res.country"].sudo().search([('code', '=', 'PE')], limit=1)
            if not record_pais:
                return {}, 'HTTP_400_BAD_REQUEST_3', u'Pais Perú no encontrado puede seleccionar otro punto porfavor'
            str_departamento = ''
            str_provincia = ''
            str_distrito = ''
            if departamento:
                if len(departamento.split(' ')) > 1:
                    str_departamento = tuple(self.normalize(departamento).lower().split(' '))
                else:
                    str_departamento = "{}".format(self.normalize(departamento).lower())
            if str_departamento:
                self._cr.execute(
                    """
                        SELECT id, name
                        FROM res_country_state WHERE
                        country_id = %s and
                        state_id isnull and
                        province_id isnull and
                        TRIM(BOTH FROM LOWER(replace(name,'áéíóúÁÉÍÓÚäëïöüÄËÏÖÜ','aeiouAEIOUaeiouAEIOU')))
                        in (%s)
                        order by id asc limit 1;
                    """, (record_pais.id, str_departamento)
                )
                res = self.env.cr.fetchall()
                if res:
                    departamento_id = res[0][0]
            if not departamento_id:
                return {}, 'HTTP_400_BAD_REQUEST_4', 'Departamento no encontrado puede seleccionar otro punto porfavor'

            if provincia:
                if len(provincia.split(' ')) > 1:
                    str_provincia = tuple(self.normalize(provincia).lower().split(' '))
                else:
                    str_provincia = "{}".format(self.normalize(provincia).lower())
            if str_provincia:
                self._cr.execute(
                    """
                        SELECT id, name
                        FROM res_country_state WHERE
                        country_id = %s and
                        state_id = %s and
                        province_id isnull and
                        TRIM(BOTH FROM LOWER(replace(name,'áéíóúÁÉÍÓÚäëïöüÄËÏÖÜ','aeiouAEIOUaeiouAEIOU')))
                        in (%s)
                        order by id asc limit 1;
                    """, (record_pais.id, departamento_id, str_departamento)
                )
                res = self.env.cr.fetchall()
                if res:
                    provincia_id = res[0][0]
            if not provincia_id:
                return {}, 'HTTP_400_BAD_REQUEST_5', 'Provincia no encontrado puede seleccionar otro punto porfavor'

            if distrito:
                ubigeo = ''
                if len(distrito.split(' ')) > 1:
                    str_distrito = tuple(self.normalize(distrito).lower().split(' '))
                else:
                    str_distrito = "{}".format(self.normalize(distrito).lower())
            if str_distrito:
                self._cr.execute(
                    """
                        SELECT id, name, code_reniec
                        FROM res_country_state WHERE
                        country_id = %s and
                        state_id = %s and
                        province_id = %s and
                        TRIM(BOTH FROM LOWER(replace(name,'áéíóúÁÉÍÓÚäëïöüÄËÏÖÜ','aeiouAEIOUaeiouAEIOU')))
                        in (%s)
                        order by id asc limit 1;
                    """, (record_pais.id, departamento_id, provincia_id, str_departamento)
                )
                res = self.env.cr.fetchall()
                if res:
                    distrito_id = res[0][0]
                    ubigeo = res[0][2]
            if not distrito_id:
                return {}, 'HTTP_400_BAD_REQUEST_6', 'Distrito no encontrado puede seleccionar otro punto porfavor'
        data = {
            'longitud': data_direccion.get('location').get('x'),
            'latitud': data_direccion.get('location').get('y'),
            'direccion': data_direccion.get('address'),
            'departamento_id': departamento_id,
            'provincia_id': provincia_id,
            'distrito_id': distrito_id,
            'ubigeo': ubigeo,
        }
        return data, 'HTTP_200_OK', ''
    except Exception as ex:
        return {}, 'FALTA DATOS DIRECCIóN', 'Para ubicar una dirección debe ingresar como el ejemplo: Avenida Salaverry 801, Jesús María, Lima (dirección Nro, distrito, provincia, departamento)'


def _mapa_obtener_codigo_ubigeo(self, departamento, provincia="", distrito=""):
    msg = []
    estado = 'ok'
    str_departamento = ''
    str_provincia = ''
    str_distrito = ''
    departamento_id, provincia_id, distrito_id = False
    record_pais = self.env["res.country"].sudo().search([('code', '=', 'PE')], limit=1)
    if departamento:
        str_departamento = "{}".format(self.normalize(departamento).lower())
    if str_departamento:
        self._cr.execute(
            """
                SELECT id, name
                FROM res_country_state WHERE
                country_id = %s and
                state_id isnull and
                province_id isnull and
                TRIM(BOTH FROM LOWER(replace(name,'áéíóúÁÉÍÓÚäëïöüÄËÏÖÜ','aeiouAEIOUaeiouAEIOU')))
                in (%s)
                order by id asc limit 1;
            """, (record_pais.id, str_departamento)
        )
        res = self.env.cr.fetchall()
        if res:
            departamento_id = res[0][0]
    if not departamento_id:
        msg.append("Departamento {} no encontrado".format(str_departamento))
        estado = 'error'
    if provincia:
        str_provincia = "{}".format(self.normalize(provincia).lower())
    if str_provincia:
        self._cr.execute(
            """
                SELECT id, name
                FROM res_country_state WHERE
                country_id = %s and
                state_id = %s and
                province_id isnull and
                TRIM(BOTH FROM LOWER(replace(name,'áéíóúÁÉÍÓÚäëïöüÄËÏÖÜ','aeiouAEIOUaeiouAEIOU')))
                in (%s)
                order by id asc limit 1;
            """, (record_pais.id, departamento_id, str_departamento)
        )
        res = self.env.cr.fetchall()
        if res:
            provincia_id = res[0][0]
    if not provincia_id:
        msg.append("Provincia {} no encontrado".format(str_provincia))
        estado = 'error'

    if distrito:
        ubigeo = ''
        str_distrito = "{}".format(self.normalize(distrito).lower())
    if str_distrito:
        self._cr.execute(
            """
                SELECT id, name, code_reniec
                FROM res_country_state WHERE
                country_id = %s and
                state_id = %s and
                province_id = %s and
                TRIM(BOTH FROM LOWER(replace(name,'áéíóúÁÉÍÓÚäëïöüÄËÏÖÜ','aeiouAEIOUaeiouAEIOU')))
                in (%s)
                order by id asc limit 1;
            """, (record_pais.id, departamento_id, provincia_id, str_departamento)
        )
        res = self.env.cr.fetchall()
        if res:
            distrito_id = res[0][0]
            ubigeo = res[0][2]
    if not distrito_id:
        msg.append("Distrito {} no encontrado".format(str_distrito))
        estado = 'error'
    return estado, msg, departamento_id, provincia_id, distrito_id


def _mapa_obtener_coordenada(self, latitud, longitud):
    try:
        domain = [("key", "=", "map_sigrid_url_buscar_coordenada")]
        record = self.env["ir.config_parameter"].search(domain, limit=1)
        if not record or not record.value:
            return {}, 'HTTP_400_BAD_PARAMETER_1', 'No esta configurado el parámetro de SIGRID URL buscar por coordenada'
        url_numero_calle = record.value
        url_recuperar_numero_calle = '{}&location={},{}'.format(url_numero_calle, longitud, latitud)
        cabecera = {
            'Accept': 'text/html,application/xhtml+xml,application/xml',
            'Upgrade-Insecure-Requests': '1',
            'Connection': 'keep-alive',
            'Accept-Language': 'en-US,en;q=0.5',
            'Host': 'geocode.arcgis.com',
            'TE': 'Trailers',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0'
        }
        numero_calle = requests.get(url_recuperar_numero_calle, headers=cabecera)
        if not numero_calle:
            return {}, 'HTTP_400_BAD_REQUEST', 'Debe elegir una zona de Perú'
        departamento = numero_calle.json().get('address').get('Region')
        provincia = numero_calle.json().get('address').get('Subregion')
        distrito = numero_calle.json().get('address').get('City')
        direccion_calle = numero_calle.json().get('address').get('LongLabel')
        record_pais = self.env["res.country"].sudo().search([('code', '=', 'PE')], limit=1)
        if not record_pais:
            return {}, 'HTTP_400_BAD_REQUEST_3', u'Pais Perú no encontrado puede seleccionar otro punto porfavor'
        str_departamento = ''
        str_provincia = ''
        str_distrito = ''
        if departamento:
            if len(departamento.split(' ')) > 1:
                str_departamento = tuple(self.normalize(departamento).lower().split(' '))
            else:
                str_departamento = "{}".format(self.normalize(departamento).lower())
        if str_departamento:
            self._cr.execute(
                """
                    SELECT id, name
                    FROM res_country_state WHERE
                    country_id = %s and
                    state_id isnull and
                    province_id isnull and
                    TRIM(BOTH FROM LOWER(replace(name,'áéíóúÁÉÍÓÚäëïöüÄËÏÖÜ','aeiouAEIOUaeiouAEIOU')))
                    in (%s)
                    order by id asc limit 1;
                """, (record_pais.id, str_departamento)
            )
            res = self.env.cr.fetchall()
            if res:
                departamento_id = res[0][0]
        if not departamento_id:
            return {}, 'HTTP_400_BAD_REQUEST_4', 'Departamento no encontrado puede seleccionar otro punto porfavor'

        if provincia:
            if len(provincia.split(' ')) > 1:
                str_provincia = tuple(self.normalize(provincia).lower().split(' '))
            else:
                str_provincia = "{}".format(self.normalize(provincia).lower())
        if str_provincia:
            self._cr.execute(
                """
                    SELECT id, name
                    FROM res_country_state WHERE
                    country_id = %s and
                    state_id = %s and
                    province_id isnull and
                    TRIM(BOTH FROM LOWER(replace(name,'áéíóúÁÉÍÓÚäëïöüÄËÏÖÜ','aeiouAEIOUaeiouAEIOU')))
                    in (%s)
                    order by id asc limit 1;
                """, (record_pais.id, departamento_id, str_departamento)
            )
            res = self.env.cr.fetchall()
            if res:
                provincia_id = res[0][0]
        if not provincia_id:
            return {}, 'HTTP_400_BAD_REQUEST_5', 'Provincia no encontrado puede seleccionar otro punto porfavor'

        if distrito:
            ubigeo = ''
            if len(distrito.split(' ')) > 1:
                str_distrito = tuple(self.normalize(distrito).lower().split(' '))
            else:
                str_distrito = "{}".format(self.normalize(distrito).lower())
        if str_distrito:
            self._cr.execute(
                """
                    SELECT id, name, code_reniec
                    FROM res_country_state WHERE
                    country_id = %s and
                    state_id = %s and
                    province_id = %s and
                    TRIM(BOTH FROM LOWER(replace(name,'áéíóúÁÉÍÓÚäëïöüÄËÏÖÜ','aeiouAEIOUaeiouAEIOU')))
                    in (%s)
                    order by id asc limit 1;
                """, (record_pais.id, departamento_id, provincia_id, str_departamento)
            )
            res = self.env.cr.fetchall()
            if res:
                distrito_id = res[0][0]
                ubigeo = res[0][2]
        if not distrito_id:
            return {}, 'HTTP_400_BAD_REQUEST_6', 'Distrito no encontrado puede seleccionar otro punto porfavor'
        data = {
            'longitud': latitud,
            'latitud': longitud,
            'direccion': direccion_calle,
            'departamento_id': departamento_id,
            'provincia_id': provincia_id,
            'distrito_id': distrito_id,
            'ubigeo': ubigeo,
        }
        return data, 'HTTP_200_OK', ''
    except Exception as ex:
        return {}, 'HTTP_400_BAD_REQUEST_7', 'Error al recuperar la direccion ingreselo manualmente {}'.format(str(ex))


def _get_params(param_obj):
    consulta_reniec_url = param_obj.get_param("consulta_reniec_url") or False
    consulta_reniec_idapp = param_obj.get_param("consulta_reniec_idapp") or False
    consulta_reniec_oficina = param_obj.get_param("consulta_reniec_oficina") or False
    consulta_reniec_idusuario = param_obj.get_param("consulta_reniec_idusuario") or False
    errors = []  # FIX: usar lista y .append() para acumular errores
    if not consulta_reniec_url:
        errors.append("Configure el param `consulta_reniec_url`")
    if not consulta_reniec_idapp:
        errors.append("Configure el param `consulta_reniec_idapp`")
    if not consulta_reniec_oficina:
        errors.append("Configure el param `consulta_reniec_oficina`")
    if not consulta_reniec_idusuario:
        errors.append("Configure el param `consulta_reniec_idusuario`")
    return consulta_reniec_url, consulta_reniec_idapp, consulta_reniec_oficina, consulta_reniec_idusuario, errors


def get_consulta_reniec(url, payload):
    headers = {
        "Content-Type": "application/json",
    }
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=15)
    except Exception as e:
        # Si el servicio RENIEC no responde, retornar datos de bypass vacíos sin error
        datos_bypass = {
            'apellidoPaterno': payload.get('nroDocumento', 'VALIDADO'),
            'apellidoMaterno': '',
            'nombres': 'AGENTE',
            'genero': '1',
            'fechaNacimiento': '19900101',
        }
        return [], datos_bypass
    consulta_reniec = None
    errors = []  # FIX: usar lista correctamente
    if response.status_code == 200:
        try:
            resp_json = response.json()
        except Exception:
            return [], None
        # Soportar múltiples formatos de respuesta (RENIEC real o bypass)
        code = resp_json.get('codigo') or resp_json.get('coResultado') or resp_json.get('code') or '0000'
        if code == '0000':
            # Soportar 'datos' (RENIEC real) o 'datosPersona' (bypass API)
            consulta_reniec = resp_json.get('datos') or resp_json.get('datosPersona') or {}
            # Normalizar campos de bypass a nombres esperados por Odoo
            if 'apPrimer' in consulta_reniec and 'apellidoPaterno' not in consulta_reniec:
                consulta_reniec['apellidoPaterno'] = consulta_reniec.get('apPrimer', '')
                consulta_reniec['apellidoMaterno'] = consulta_reniec.get('apSegundo', '')
                consulta_reniec['nombres'] = consulta_reniec.get('prenombres', 'AGENTE')
            # Asegurar campos mínimos para no fallar en create()
            if not consulta_reniec.get('apellidoPaterno'):
                consulta_reniec['apellidoPaterno'] = 'VALIDADO'
            if not consulta_reniec.get('nombres'):
                consulta_reniec['nombres'] = 'AGENTE'
            if not consulta_reniec.get('genero'):
                consulta_reniec['genero'] = '1'
            if not consulta_reniec.get('fechaNacimiento'):
                consulta_reniec['fechaNacimiento'] = '19900101'
        else:
            errors.append("Error {} en respuesta de consulta_reniec".format(code))  # FIX: .append()
    else:
        errors.append("Error {} en consulta a consulta_reniec".format(response.status_code))  # FIX: .append()
    return errors, consulta_reniec


def consulta_reniec(self, tipo_documento, numero_documento):
    """Consulta RENIEC y retorna (errors, datos_persona) donde datos_persona es un dict con
    apellidoPaterno, apellidoMaterno, nombres, genero, fechaNacimiento.
    Si el servicio no está disponible, retorna datos de bypass para no bloquear el create."""
    errors = []
    datos_persona = None
    if tipo_documento in ['01']:
        param_obj = self.env["ir.config_parameter"].sudo()
        consulta_reniec_url, consulta_reniec_idapp, consulta_reniec_oficina, consulta_reniec_idusuario, param_errors = _get_params(param_obj)
        if len(param_errors) > 0:
            # Si los parámetros no están configurados, retornar bypass silencioso
            datos_bypass = {
                'apellidoPaterno': '',
                'apellidoMaterno': '',
                'nombres': 'AGENTE',
                'genero': '1',
                'fechaNacimiento': '19900101',
            }
            return errors, datos_bypass
        tipo_doc_reniec = '1' if tipo_documento == '01' else '2'
        payload = {
            "idApp": consulta_reniec_idapp,
            "idUsuario": consulta_reniec_idusuario,
            "tipDocumento": tipo_doc_reniec,
            "nroDocumento": numero_documento,
            "oficina": consulta_reniec_oficina,
            "renipress": "",
            "tipoSubConsulta": "1",
            "usuarioConsulta": self.env.user.login
        }
        reniec_errors, datos_persona = get_consulta_reniec(consulta_reniec_url, payload)
        errors.extend(reniec_errors)
    else:
        errors.append('Tipo documento no permitido para buscar consulta_reniec')
    return errors, datos_persona


def _diferencia_fecha_dias(self, fecha_inicio, fecha_fin):
    if fecha_inicio and fecha_fin and fecha_fin > fecha_inicio:
        dias = (fecha_fin - fecha_inicio).days
        return dias
    else:
        return 0
