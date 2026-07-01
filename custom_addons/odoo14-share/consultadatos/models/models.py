import base64
import json
import logging
import pprint
import re
import requests

from dateutil.relativedelta import relativedelta
from PIL import ImageFile

from odoo import api, fields, models, modules, tools
from odoo.exceptions import ValidationError
import odoo.tools.config as config

from .constants import mpi_msg_not_install

try:
    from mpi_client import client as mpiclient
except Exception as e:
    mpiclient = None


ImageFile.LOAD_TRUNCATED_IMAGES = True

__image_path = modules.get_module_resource(
    "base", "static/src/img", "avatar.png"
)
image_avatar = None

# Tipos de documento en mpi
TIPODOC_NO_SE_CONOCE = TIPODOC_SD = "00"
TIPODOC_DNI = TIPODOC_DNI = "01"
TIPODOC_LIBRETA_MILITAR = TIPODOC_LM = "02"
TIPODOC_CARNET_EXTRANJERIA = TIPODOC_CE = "03"
TIPODOC_ACTA_NACIMIENTO = TIPODOC_ACTA_NAC = TIPODOC_ACTAC_NAC = "04"
TIPODOC_PASAPORTE = "06"
TIPODOC_DNI_EXTRANJERO = "07"

TIPODOC_LISTA = (
    TIPODOC_SD,
    TIPODOC_DNI,
    TIPODOC_LM,
    TIPODOC_CE,
    TIPODOC_ACTA_NAC,
    TIPODOC_PASAPORTE,
    TIPODOC_DNI_EXTRANJERO,
)

TIPODOC_SELECTION = [
    (TIPODOC_SD, u"Sin documento"),
    (TIPODOC_DNI, u"Dni"),
    (TIPODOC_LIBRETA_MILITAR, u"Libreta Militar"),
    (TIPODOC_CARNET_EXTRANJERIA, u"Carnet Extranjería"),
    (TIPODOC_ACTA_NACIMIENTO, u"Acta de Nacimiento"),
    (TIPODOC_PASAPORTE, u"Pasaporte"),
    (TIPODOC_DNI_EXTRANJERO, u"Dni Extranjero"),
]


TIPODOC_UID_LONG = 20
TIPODOC_DNI_LONG = 8
TIPODOC_CE_LONG = 9

TIPODOC_LONG = {
    TIPODOC_SD: {"min": 6, "max": 30},
    TIPODOC_DNI: {"fijo": 8},
    TIPODOC_LIBRETA_MILITAR: {"min": 9, "max": 10},
    TIPODOC_CARNET_EXTRANJERIA: {"fijo": 9},
    TIPODOC_ACTA_NACIMIENTO: {"min": 6, "max": 10},
    TIPODOC_PASAPORTE: {"min": 6, "max": 12},
    TIPODOC_DNI_EXTRANJERO: {"min": 6, "max": 15},
}

# No fijos y alfanumerico
TIPODOC_LONG_NOFIJOS = tuple(
    [
        tipodoc
        for tipodoc in TIPODOC_LONG
        if not TIPODOC_LONG[tipodoc].get("fijo")
    ]
)

# ##### TIPO SEGURO #####
TIPO_SEGURO_SIS = "2"


# ##### HR Estado Civil(marital) #####
MARITAL_SINGLE = "single"
MARITAL_MARRIED = "married"
MARITAL_WIDOWER = "widower"
MARITAL_DIVORCED = "divorced"
MARITAL_OTHER = "other"

dict_estado_civil = {
    "1": MARITAL_SINGLE,  # soltero(a)
    "2": MARITAL_MARRIED,  # casado(a)
    "3": MARITAL_WIDOWER,  # viudo(a)
    "4": MARITAL_DIVORCED,  # divorciado(a)
}
inv_dict_estado_civil = {
    value: key for key, value in dict_estado_civil.items()
}

HR_SELECTION_MARITAL = [
    (MARITAL_SINGLE, "Soltero(a)"),
    (MARITAL_MARRIED, "Casado(a)"),
    (MARITAL_WIDOWER, "Viudo(a)"),
    (MARITAL_DIVORCED, "Divorciado(a)"),
    (MARITAL_OTHER, "Otro/Error"),
]


# ##### HR Sexo(gender) #####
GENDER_MALE = "male"
GENDER_FEMALE = "female"
GENDER_OTHER = "other"

dict_sexo = {
    "1": GENDER_MALE,
    "2": GENDER_FEMALE,
}
inv_dict_sexo = {value: key for key, value in dict_sexo.items()}

HR_SELECTION_GENDER = [
    (GENDER_MALE, "Masculino"),
    (GENDER_FEMALE, "Femenino"),
    (GENDER_OTHER, "Otro/Error"),
]

_logger = logging.getLogger(__name__)


TIPOCONSULTA_CIUDADANO = "ciudadano"
TIPOCONSULTA_CIUDADANO_ACTUALIZAR_SIS = "ciudadano_actualizar_sis"
TIPOCONSULTA_SIS = "sis"
TIPOCONSULTA_CNV = "cnv"

SELECTION_TIPOCONSULTA = [
    (TIPOCONSULTA_CIUDADANO, "Ciudadano"),
    (TIPOCONSULTA_CIUDADANO_ACTUALIZAR_SIS, "Actualizar sis"),
    (TIPOCONSULTA_SIS, "Sis"),
    (TIPOCONSULTA_CNV, "Consulta DNI madre"),
]


class ConsultadatosReniec(models.TransientModel):
    """Clase ConsultadatosReniec."""

    _description = "Consulta de datos Reniec"
    _name = "consultadatos.reniec"

    @api.model
    def consultardni(self, numerodni):
        return self.env["consultadatos.mpi"].consultardni(numerodni)


class ConsultadatosMpiTemplate(models.AbstractModel):
    _name = "consultadatos.mpi.template"
    _description = "Consulta de datos de Mpi - Template"

    tipo_consulta = fields.Selection(SELECTION_TIPOCONSULTA, index=True)
    tipo_documento = fields.Char(
        "Tipo de Documento", size=3, required=True, index=True
    )
    identificacion = fields.Char(
        "Número documento/uuid", required=True, index=True
    )
    text_json = fields.Binary("Contenido", attachment=True)
    fecha_mpi = fields.Datetime("Actualización MPI", required=True)
    status = fields.Char("Status", default="200", size=3)


class ConsultadatosMpiWizard(models.TransientModel):
    _name = "consultadatos.mpi.wizard"
    _description = u"Pruebas de Consulta de datos de Mpi - Wizard"

    tipo_consulta = fields.Selection(
        SELECTION_TIPOCONSULTA, default=TIPOCONSULTA_CIUDADANO
    )
    tipo_documento = fields.Char(
        "Tipo de Documento", size=3, required=True, default=TIPODOC_DNI
    )
    identificacion = fields.Char("Número documento/uuid", required=True)
    fecha_mpi = fields.Datetime("Actualización MPI", readonly=True)
    status = fields.Char("Status", readonly=True)
    text_json = fields.Text("Contenido Json", readonly=True)
    res_id = fields.Integer("Id. del recurso", readonly=True)

    def action_consultar(self):
        self.ensure_one()
        params = dict(
            numero_documento_or_uuid=self.identificacion,
            tipo_documento=self.tipo_documento,
            tipo_consulta=self.tipo_consulta,
        )
        vals = self.env["consultadatos.mpi"].ver(**params)

        foto = vals.get("foto")
        if foto and type(foto) == str:
            vals["foto"] = u"{}...".format(foto[-40:])

        self.write(
            {
                "res_id": vals["meta_consultadatos"]["id"],
                "status": vals["meta_consultadatos"]["status"],
                "fecha_mpi": vals["meta_consultadatos"]["fecha_mpi"],
                "text_json": pprint.pformat(vals),
            }
        )


class ConsultadatosMpi(models.Model):
    _description = "Consulta de datos de Mpi"
    _inherit = "consultadatos.mpi.template"
    _name = "consultadatos.mpi"
    _order = "create_date desc, write_date desc"

    _sql_constraints = [
        (
            "documento_unique",
            "unique(tipo_consulta, tipo_documento, identificacion)",
            "El documento debe ser único!",
        ),
    ]

    def get_parametros_mpi(self):
        """
        Devuelve los parametros host y token de MPI contenidos en ir.config_parameter
        returna (mpiclient, mpi_api_host, mpi_api_token)
        """
        get_param = self.env["ir.config_parameter"].sudo().get_param

        modo_online = (
            get_param("consultadatos.modo_online")
            or get_param("modo_online")
            or "True"
        )

        if modo_online.title() not in ["True", "1"]:
            return {}

        env_mpi_api_host = config.get("mpi_api_host", False)
        env_mpi_api_token = config.get("mpi_api_token", False)

        mpi_api_host = get_param("mpi_api_host") or get_param(
            "consultadatos.mpi_api_host"
        )
        mpi_api_token = get_param("mpi_api_token") or get_param(
            "consultadatos.mpi_api_token"
        )
        mpi_api_host = mpi_api_host != "mpi_api_host" and mpi_api_host
        mpi_api_token = mpi_api_token != "mpi_api_token" and mpi_api_token

        mpi_api_host = not mpi_api_host and env_mpi_api_host or mpi_api_host
        mpi_api_token = (
            not mpi_api_token and env_mpi_api_token or mpi_api_token
        )

        if not mpi_api_host:
            raise ValidationError(
                "No esta configurado el parámetro de sistema mpi_api_host"
            )
        elif not mpi_api_token:
            raise ValidationError(
                "No esta configurado el parámetro de sistema mpi_api_token"
            )

        if not mpiclient:
            raise ValidationError(mpi_msg_not_install)

        mpiclient.MPI_API_HOST = mpi_api_host

        return (mpiclient, mpi_api_host, mpi_api_token)

    @api.model
    def consultardocumento(self, numero_documento, tipo_documento):
        u"""
        : param numero_documento, número de documento or uuui del ciudadano
        : param tipo_documento, tipo de documento
        :rtype diccionario
        """

        if not numero_documento:
            return {"error": u"No se especificó el número de documento"}

        if not tipo_documento:
            return {"error": u"No se especificó el tipo de documento"}

        data = self.ver(numero_documento, tipo_documento=tipo_documento)
        if not data:
            return {}

        if data is None or data.get("error"):
            raise ValidationError(
                data.get("error", "Error al consultar el documento")
            )
        errors = data.get("errors", [])

        if errors:
            errors = errors[0]
            raise ValidationError(u"Tipo y número de documento no encontrado")

        res = dict(
            dni=data.get("numero_documento", False),
            ape_paterno=data.get("apellido_paterno", False),
            ape_materno=data.get("apellido_materno", False),
            nombres=data.get("nombres", False),
            # Datos Nacimiento
            nacimiento=dict(
                ubigeo=data.get("nacimiento_ubigeo", False),
                fecha=data.get("fecha_nacimiento", False),
            ),
            # Datos Domicilio
            domicilio=dict(
                direccion=data.get("domicilio_direccion", False),
                ubigeo=data.get("get_distrito_domicilio_ubigeo_reniec", False),
                direccion_descripcion=data.get("domicilio_direccion", False),
            ),
            sexo=dict_sexo.get(data.get("sexo"), GENDER_OTHER),
            estadocivil=dict_estado_civil.get(
                data.get("estado_civil"), MARITAL_OTHER
            ),
            fotografia=data.get("foto", False),
            telefono=data.get("telefono", False),
            celular=data.get("celular", False),
        )

        return res

    @api.model
    def consultardni(self, numerodni):
        message = False
        if not numerodni:
            message = u"No se especificó el número de dni"

        if len(numerodni) != 8 or not numerodni.isdigit():
            message = u"Error en el dni, debe ser de 8 dígitos"

        if message:
            raise ValidationError(message)

        return self.consultardocumento(numerodni, TIPODOC_DNI)

    def _clean_tipo_documento(self, tipo_documento):
        if type(tipo_documento) == 'str':
            tipo_documento = tipo_documento.lower()
        if tipo_documento in ("dni", "1"):
            return TIPODOC_DNI
        elif tipo_documento == "sd":
            return TIPODOC_SD
        elif tipo_documento in ("ce", "3"):
            return TIPODOC_CARNET_EXTRANJERIA
        elif tipo_documento not in (TIPODOC_LISTA):
            raise ValidationError(u"Tipo de documento no válido")
        else:
            return tipo_documento

    def ver(
        self,
        numero_documento_or_uuid,
        tipo_documento=TIPODOC_DNI,
        tipo_consulta=TIPOCONSULTA_CIUDADANO,
        minutos_sinactualizar=None,
    ):
        if not numero_documento_or_uuid:
            logging.debug("No se especifico el numero documento")
            return {}

        tipo_documento = self._clean_tipo_documento(tipo_documento)
        self = self.sudo()

        domain = [
            ("tipo_consulta", "=", tipo_consulta),
            ("tipo_documento", "=", tipo_documento),
            ("identificacion", "=", numero_documento_or_uuid),
        ]
        record = self.search(domain, limit=1)

        if record and not record.text_json:
            sql = """SELECT text_json FROM {} WHERE id={};"""
            sql = sql.format(self._table, record.id)
            self.env.cr.execute(sql)
            text_json = self.env.cr.fetchone()[0]
            sql = """UPDATE {} set text_json=null WHERE id={};"""
            sql = sql.format(self._table, record.id)
            self.env.cr.execute(sql)
            record.text_json = base64.encodestring(text_json)

        if not record:
            res_json = self.__ver(
                numero_documento_or_uuid,
                tipo_documento=tipo_documento,
                tipo_consulta=tipo_consulta,
            )
            if res_json:
                errors = res_json.get("errors")
                if res_json.get("errors"):
                    if type(errors) is list:
                        status = res_json["errors"][0].get("status", False)
                    elif type(errors) is not None:
                        status = "500"
                    else:
                        status = "200"
                elif "error" in res_json:
                    status = "500"
                else:
                    status = "200"
            else:
                return {}

            values = dict(
                tipo_consulta=tipo_consulta,
                tipo_documento=tipo_documento,
                identificacion=numero_documento_or_uuid,
                text_json=base64.encodebytes(str(res_json).encode()),
                fecha_mpi=fields.Datetime.now(),
                status=status,
            )

            record = self.create(values)

        json_vals = eval(base64.decodebytes(record.text_json))
        meta_consultadatos = dict(
            id=record.id, fecha_mpi=record.fecha_mpi, status=record.status,
        )
        json_vals = dict(json_vals, meta_consultadatos=meta_consultadatos)

        if "error" not in json_vals and "errors" not in json_vals:
            #foto = unicode(json_vals.get("foto"))
            foto = json_vals.get("foto")
            if foto and len(foto) < 100:
                json_vals["foto"] = image_avatar

        return json_vals

    def __ver(
        self,
        numero_documento_or_uuid,
        tipo_documento=TIPODOC_DNI,
        tipo_consulta="ciudadano",
    ):
        def ver_datos_sis(
            self, numero_documento_or_uuid, tipo_documento=TIPODOC_DNI
        ):
            """Metodo que reemplaza a ver_datos_sis en CiudadanoClient(mpi_client)."""
            kwargs = {"headers": self.client_headers, "timeout": self.timeout}

            def ver(url):
                try:
                    response = requests.get(url, **kwargs)
                    if response.status_code == 200:
                        return response.json().get("data").get("attributes")

                    try:
                        res = json.loads(response.content.decode())
                        if response.status_code == 404 and res.get(
                            "errors", {}
                        ).get("datos_sis"):
                            return res["errors"]
                        return res
                    except json.JSONDecodeError:
                        return {"error": response.reason}
                except requests.Timeout:
                    return {"error": "Timeout error"}

            if re.match(r"^\d{8,15}$", numero_documento_or_uuid):
                url = "{server}/api/v1/ciudadano/datos-sis/{tipo_documento}/{numero_documento}/".format(
                    server=self.__mpi_api_url__,
                    tipo_documento=tipo_documento,
                    numero_documento=numero_documento_or_uuid,
                )
            elif re.match(r"^SD-N\d{8}$", numero_documento_or_uuid):
                url = "{server}/api/v1/ciudadano/datos-sis/{tipo_documento}/{numero_documento}/".format(
                    server=self.__mpi_api_url__,
                    tipo_documento=TIPODOC_SD,
                    numero_documento=numero_documento_or_uuid,
                )
            else:
                url = "{server}/api/v1/ciudadano/datos-sis/{uuid}/".format(
                    server=self.__mpi_api_url__, uuid=numero_documento_or_uuid
                )
            return ver(url)

        def ver_datos_cnv_madre(
            ciudadanoclient,
            numero_documento_or_uuid,
            tipo_documento=TIPODOC_DNI,
        ):
            """Metodo que invoca a servicio cnv: consulta por DNI de madre"""
            kwargs = {
                "headers": ciudadanoclient.client_headers,
                "timeout": ciudadanoclient.timeout,
            }

            def ver(url):
                try:
                    response = requests.get(url, **kwargs)
                    if response.status_code == 200:
                        return {"list": response.json().get("data")}

                    try:
                        res = json.loads(response.content.decode())
                        if response.status_code == 404 and res.get(
                            "errors", {}
                        ).get("datos_sis"):
                            return res["errors"]
                        return res
                    except json.JSONDecodeError:
                        return {"error": response.reason}
                    except Exception as e:
                        return {"error": e.message}

                except requests.Timeout:
                    return {"error": "Timeout error"}
                except Exception as e:
                    return {"error": e.message}

            if re.match(r"^\d{8,15}$", numero_documento_or_uuid):
                url = "{server}/api/v1/cnv/madre/{tipo_documento}/{numero_documento}/".format(
                    server=ciudadanoclient.__mpi_api_url__,
                    tipo_documento=tipo_documento,
                    numero_documento=numero_documento_or_uuid,
                )
            elif re.match(r"^SD-N\d{8}$", numero_documento_or_uuid):
                url = "{server}/api/v1/cnv/madre/{tipo_documento}/{numero_documento}/".format(
                    server=ciudadanoclient.__mpi_api_url__,
                    tipo_documento=TIPODOC_SD,
                    numero_documento=numero_documento_or_uuid,
                )
            else:
                url = "{server}/api/v1/cnv/madre/{uuid}/".format(
                    server=ciudadanoclient.__mpi_api_url__,
                    uuid=numero_documento_or_uuid,
                )
            return ver(url)

        if not numero_documento_or_uuid:
            return {"error": u"No se especifico el número de documento"}

        if not tipo_documento:
            return {"error": u"No se especifico el tipo de documento"}

        tipo_documento = self._clean_tipo_documento(tipo_documento)

        long_numero_documento = len(numero_documento_or_uuid)

        if long_numero_documento != TIPODOC_UID_LONG:
            if tipo_documento not in TIPODOC_LONG:
                return {"error": u"No se puede validar este tipo de documento"}
            tipodoc_long_dict = TIPODOC_LONG[tipo_documento]
            if tipo_documento in TIPODOC_LONG_NOFIJOS:
                long_min = tipodoc_long_dict["min"]
                long_max = tipodoc_long_dict["max"]
                if not long_min <= long_numero_documento <= long_max:
                    return {
                        "error": u"El documento debe tener {}-{} caracteres entre letras y/o números".format(
                            long_min, long_max
                        )
                    }
            else:
                if tipodoc_long_dict.get("fijo"):
                    if not (
                        long_numero_documento == tipodoc_long_dict["fijo"]
                        and numero_documento_or_uuid.isdigit()
                    ):
                        return {
                            "error": u"El documento debe tener {} dígitos".format(
                                tipodoc_long_dict.get("fijo")
                            )
                        }
                else:
                    long_min = tipodoc_long_dict["min"]
                    long_max = tipodoc_long_dict["max"]

                    if not (
                        long_min <= long_numero_documento <= long_max
                        and numero_documento_or_uuid.isdigit()
                    ):
                        return {
                            "error": u"El documento debe tener {}-{} dígitos".format(
                                long_min, long_max
                            )
                        }

        elif not (
            numero_documento_or_uuid.isalpha()
            or numero_documento_or_uuid.isdigit()
            or long_numero_documento != TIPODOC_UID_LONG
        ):
            return {
                "error": u"El documento debe tener {} caracteres".format(
                    TIPODOC_UID_LONG
                )
            }

        parametros_mpi = self.get_parametros_mpi()
        if not parametros_mpi:
            return {"error": "No hay parametros MPI"}

        mpiclient, mpi_api_host, mpi_api_token = parametros_mpi
        mpiclient.CiudadanoClient.ver_datos_sis = ver_datos_sis

        try:
            ciudadanoclient = mpiclient.CiudadanoClient(mpi_api_token)
            if tipo_consulta == "ciudadano":
                response = ciudadanoclient.ver(
                    numero_documento_or_uuid, tipo_documento
                )
            elif tipo_consulta == TIPOCONSULTA_CIUDADANO_ACTUALIZAR_SIS:
                response = ciudadanoclient.ver(
                    numero_documento_or_uuid,
                    tipo_documento,
                    actualizar_sis=True,
                )
            elif tipo_consulta == "sis":
                response = ciudadanoclient.ver_datos_sis(
                    numero_documento_or_uuid, tipo_documento
                )
            elif tipo_consulta == "cnv":
                response = ver_datos_cnv_madre(
                    ciudadanoclient, numero_documento_or_uuid, tipo_documento
                )
            else:
                return {
                    "error": "Tipo_consulta {} no es válido".format(
                        tipo_consulta
                    )
                }

            if response.get("error", False):
                t = tipo_documento, numero_documento_or_uuid, response["error"]
                message = "Error MPI tipo_documento: {} numero_documento: {} - {}".format(
                    *t
                )
                _logger.error(message)
                return {"error": message}
            return response
        except AttributeError:
            return {"error": "Error en MPI/No se puede consultar el documento"}
        except Exception as e:
            return {"error": e.message}

    def _ver(
        self,
        numero_documento_or_uuid,
        tipo_documento=TIPODOC_DNI,
        tipo_consulta=TIPOCONSULTA_CIUDADANO,
    ):
        return self.__ver(
            numero_documento_or_uuid, tipo_documento, tipo_consulta
        )

    def ver_actualizar_sis(
        self,
        numero_documento_or_uuid,
        tipo_documento=TIPODOC_DNI,
        tipo_consulta=TIPOCONSULTA_CIUDADANO_ACTUALIZAR_SIS,
    ):
        return self.ver_datos_sis(
            numero_documento_or_uuid, tipo_documento, tipo_consulta
        )

    def ver_datos_sis(
        self,
        numero_documento_or_uuid,
        tipo_documento=TIPODOC_DNI,
        tipo_consulta=TIPOCONSULTA_CIUDADANO,
    ):
        if tipo_consulta == TIPOCONSULTA_CIUDADANO_ACTUALIZAR_SIS:
            params = (numero_documento_or_uuid, tipo_documento, tipo_consulta)
        else:
            params = (numero_documento_or_uuid, tipo_documento)
        ciudadano = self.ver(*params)
        if ciudadano:
            if ciudadano.get("error"):
                raise ValidationError(ciudadano["error"])
            elif ciudadano.get("tipo_seguro") == TIPO_SEGURO_SIS:
                res = self.ver(
                    numero_documento_or_uuid,
                    tipo_documento,
                    tipo_consulta="sis",
                )
                value = {"tipo_seguro_general": TIPO_SEGURO_SIS}
                res.update(value)
                return res
        return {}

    @api.model
    def _cron_delete(self):
        get_param = self.env["ir.config_parameter"].sudo().get_param
        minutos_sinactualizar = get_param("mpi_minutos_sinactualizar") or 1
        try:
            minutos_sinactualizar = int(minutos_sinactualizar)
        except Exception:
            minutos_sinactualizar = 0
        now = fields.Datetime.from_string(fields.Datetime.now())

        try:
            time1 = now - relativedelta(minutes=minutos_sinactualizar)
        except Exception:
            return

        if time1.year < 1900:
            return

        time2 = now - relativedelta(minutes=1)
        time3 = now - relativedelta(minutes=60)

        domain = [
            "|",
            "&",
            ("status", "=", "200"),
            ("fecha_mpi", "<=", fields.Datetime.to_string(time1)),
            "|",
            "&",
            ("status", "!=", "200"),
            ("fecha_mpi", "<=", fields.Datetime.to_string(time2)),
            "&",
            ("status", "=", False),
            ("fecha_mpi", "<=", fields.Datetime.to_string(time3)),
        ]
        self.search(domain).unlink()

    @api.model
    def crearciudadano(self, data):
        """
        Crea un ciudadano en el servicio mpi, si el parametro mpi_crear es True.
        Retorna los datos del ciudadano desde el servicio de MPI

        : param data: diccionario con los datos del ciudadano
        {
            'tipo_documento': valor,
            'numero_documento': valor,
            'apellido_paterno': valor,
            'apellido_materno': valor,
            'nombres': valor,
            'sexo': valor,
            'fecha_nacimiento': valor,
            'estado_civil': valor,
            'nacimiento_ubigeo': valor,
            'celular': valor,
            'foto': valor,
            'es_persona_viva': valor,
            'nacimiento_ubigeo': valor
        }
        :rtype dict
        """
        get_param = self.env["ir.config_parameter"].sudo().get_param

        mpi_crear = get_param("consultadatos.mpi_crear") or "False"
        mpi_crear = mpi_crear.title() in ["True", "1"]
        if not mpi_crear:
            raise ValidationError("No tiene permisos para crear en MPI")

        mpiclient, mpi_api_host, mpi_api_token = self.get_parametros_mpi()

        # check status mpi
        session = requests.session()
        headers = {
            "Authorization": "Bearer {}".format(mpi_api_token),
            "Content-type": "application/json",
        }
        service_path = "/api/connection-status/"
        url = "{}{}".format(mpi_api_host, service_path)

        try:
            res = session.get(url, headers=headers)
        except Exception as e:
            raise ValidationError(
                "El servicio de MPI, error desconocido: {}".format(e.message)
            )

        if res.status_code == 404:
            raise ValidationError(
                "El servicio de MPI no reconoce la ruta {}".format(
                    service_path
                )
            )

        if res.status_code != 200:
            raise ValidationError(
                "El servicio de MPI produjo un error desconocido"
            )

        res = json.loads(res.text)
        if res.get("conexion_reniec", True):
            raise ValidationError(
                "No esta habilitado el sistema para crear ciudadanos"
            )

        ciudadanoclient = mpiclient.CiudadanoClient(mpi_api_token)
        tipo_documento = data.get("tipo_documento", False)

        if data.get("fecha_nacimiento", False):
            fecha_nacimiento = data["fecha_nacimiento"]
            fecha_nacimiento = fecha_nacimiento and fecha_nacimiento.replace(
                "/", "-"
            )
            data.update(dict(fecha_nacimiento=fecha_nacimiento))

        if "fecha_nacimiento" in data and not data.get(
            "fecha_nacimiento", False
        ):
            del data["fecha_nacimiento"]

        if tipo_documento == TIPODOC_NO_SE_CONOCE:
            method = "crear_sin_documento"
        elif tipo_documento in (TIPODOC_DNI, TIPODOC_CARNET_EXTRANJERIA):
            method = "crear_ciudadano_otro_tipo_documento"
        else:
            raise ValidationError(
                "No se puede crear el tipo de documento: {}".format(
                    tipo_documento
                )
            )

        if not hasattr(ciudadanoclient, method):
            raise ValidationError(
                "Esta version de mpi_client {}".format(mpiclient.version)
            )

        try:
            res_mpi = getattr(ciudadanoclient, method)(data)
        except Exception as e:
            raise ValidationError(e.message)

        errors = res_mpi.get("errors", {})

        if errors:
            if errors.get("non_field_errors"):
                raise ValidationError(res_mpi["errors"]["non_field_errors"][0])

            for field, list_error in errors.iteritems():
                raise ValidationError(
                    u"{} - {}".format(
                        field, list_error and list_error[0] or "No es correcto"
                    )
                )

        if res_mpi.get("error", False):
            t = res_mpi.get("error")
            raise ValidationError(
                "Error al crear ciudadano en mpi: {}".format(t)
            )

        return res_mpi
