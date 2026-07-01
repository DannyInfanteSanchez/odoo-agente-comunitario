{
    'name': "Base Multiple Attachments",

    'summary': """
        Allow multiple attachments for database objects.
    """,

    'description': """
Example:
========

1. Add reference to 'depends' of __manifest__.py in your module:

'depends': ['base', 'max_base_multi_attachment'],


2. Column Definition:


    first_attachment_ids = fields.One2many(
        comodel_name='max.base.multi.attachment',
        inverse_name='owner_id',
        string='First Attachments',
        domain=lambda self: [('owner_model', '=', self._name), ('owner_field', '=', 'first_attachment_ids')],
        copy=True)

    second_attachment_ids = fields.One2many(
        comodel_name='max.base.multi.attachment',
        inverse_name='owner_id',
        string='Second Attachments',
        domain=lambda self: [('owner_model', '=', self._name), ('owner_field', '=', 'second_attachment_ids')],
        copy=True)

As you can see, it is possible to define multiple attachments column in same model.


3. Form View Definition:


    <field name="first_attachment_ids"
        context="{
            'default_owner_model': 'your.model.name',
            'default_owner_id': id,
            'default_owner_field': 'first_attachment_ids',
        }"/>
    <field name="second_attachment_ids"
        context="{
            'default_owner_model': 'your.model.name',
            'default_owner_id': id,
            'default_owner_field': 'second_attachment_ids',
        }"
        widget="many2many_kanban"/>


You can use Kanban widget or not.

Done!
Wish you enjoy this!

    """,

    'author': "MAXodoo",
    'website': "http://www.maxodoo.com",
    'category': 'maxbase',
    'version': "14.0.1.0.0",
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/max_base_multi_attachment.xml',
    ],
}
