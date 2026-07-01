'''
Created on Dec 31, 2018

@author: Zuhair Hammadi
'''

from odoo.addons.web.controllers.main import Binary, serialize_exception
from odoo import http, _
from odoo.http import request, NO_POSTMORTEM
import base64
import unicodedata
import logging
import json

_logger = logging.getLogger(__name__)

class MyBinary(Binary):

    @http.route()
    @serialize_exception
    def upload_attachment(self, model, id, ufile, callback=None): # @ReservedAssignment
        files = request.httprequest.files.getlist('ufile')  # @UndefinedVariable
        Model = request.env['ir.attachment']
        out = """<script language="javascript" type="text/javascript">
                    var win = window.top.window;
                    win.jQuery(win).trigger(%s, %s);
                </script>"""
        args = []
        for ufile in files:

            filename = ufile.filename
            if request.httprequest.user_agent.browser == 'safari': # @UndefinedVariable
                # Safari sends NFD UTF-8 (where é is composed by 'e' and [accent])
                # we need to send it the same stuff, otherwise it'll fail
                filename = unicodedata.normalize('NFD', ufile.filename)

            try:
                attachment = Model.create({
                    'name': filename,
                    'datas': base64.encodebytes(ufile.read()),
                    'res_model': model,
                    'res_id': int(id)
                })
            except NO_POSTMORTEM as e:    
                msg = hasattr(e, 'name') and e.name or str(e)
                args.append({'error': msg})
                _logger.exception("Fail to upload attachment %s" % ufile.filename)                 
            except Exception:
                args.append({'error': _("Something horrible happened")})
                _logger.exception("Fail to upload attachment %s" % ufile.filename)
            else:
                args.append({
                    'filename': filename,
                    'mimetype': ufile.content_type,
                    'id': attachment.id,
                    'size': attachment.file_size
                })
        return out % (json.dumps(callback), json.dumps(args))
           