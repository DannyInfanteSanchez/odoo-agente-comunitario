
from odoo import models, fields, api
import os


class Attachment(models.Model):
    _name = 'max.base.multi.attachment'
    _description = 'Attachment'

    name = fields.Char('Name', required=True)
    description = fields.Text('Description')
    file = fields.Binary('File', attachment=True)
    file_size = fields.Integer('File Size')
    file_type = fields.Char('File Type')
    owner_model = fields.Char(required=True, index=True)
    owner_field = fields.Char(required=True, index=True)
    owner_id = fields.Integer(required=True, ondelete="cascade", index=True)

    @api.model
    def create(self, vals):
        if vals.get('file'):
            vals['file_size'] = len(vals.get('file')) * 0.75
        else:
            vals['file_size'] = 0
        return super(Attachment, self).create(vals)

    def write(self, vals):
        if 'image' in vals.keys():
            if vals.get('file'):
                vals['file_size'] = len(vals.get('file')) * 0.75
            else:
                vals['file_size'] = 0
        return super(Attachment, self).write(vals)

    @api.onchange('name')
    def _onchange_name(self):
        if self.name:
            self.file_type = os.path.splitext(self.name)[1].replace('.', '')
