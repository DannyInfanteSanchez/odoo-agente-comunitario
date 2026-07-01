# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import UserError
from .helper import _default_tipo_archivo, _default_size_documento


class Attachment(models.Model):
    _inherit = "ir.attachment"

    @api.model
    def create(self, vals):
        values = self._check_contents(vals)
        if values.get("res_model", False) == "minsa.registro":
            _MIMETYPES = _default_tipo_archivo(self)
            if values.get("mimetype", False) not in _MIMETYPES:
                raise UserError(_("Tipo de archivo no permitido: %s", values.get("name", False)))
            file_size = _default_size_documento(self)
            file_size_adjunto = len(values['datas'])
            if file_size > 0 and file_size_adjunto > file_size:
                raise UserError(_("Tamaño de archivo no permitido: %s MB", file_size_adjunto / 1024 / 1024))
        return super(Attachment, self).create(vals)
