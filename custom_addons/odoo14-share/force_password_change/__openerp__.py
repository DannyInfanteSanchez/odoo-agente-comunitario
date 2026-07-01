{
    'name': 'Force Password Change',
    'version': '1.0',
    'author': 'Ministerio de Salud',
    'category': 'Security',
    'depends': ['base', 'auth_signup'],
    'description': """Agrega campo must_change_password al usuario, bloquea el acceso si está activo,
y agrega un cron diario que revisa expiraciones según company.password_expiration.""",
    'data': [
        'data/cron_force_password_change.xml',
        'views/password_expired.xml',
    ],
    'installable': True,
    'auto_install': False,
}
