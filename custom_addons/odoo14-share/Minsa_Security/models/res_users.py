import json

from odoo import api, fields, models
from datetime import timedelta


class ResUsers(models.Model):
    _inherit = 'res.users'
    
    auto_desactivado = fields.Boolean(
        string='Desactivado Automáticamente',
        default=False,
        readonly=True,
    )
    
    fecha_desactivacion = fields.Datetime(
        string='Fecha de Desactivación',
        help='Fecha y hora en que el usuario fue desactivado',
        readonly=True,
    )
    
    @api.model
    def comprobar_desactivar_usuarios_inactivos(self): 
        """
        Método para tarea automática para verificar y desactivar usuarios inactivos.
        Se ejecuta diariamente para verificar usuarios que no han accedido
        en los últimos X días (configurado en parámetros del sistema).
        """
        dias_inactividad = self.get_limite_dias_inactividad()
        fecha_corte = fields.Datetime.now() - timedelta(days=dias_inactividad)

        domain = [
            ('active', '=', True),
            ('auto_desactivado', '=', False),
            ('id', 'not in', [1,2]),
            '|',
            ('login_date', '<', fecha_corte),
            '&',
            ('login_date', '=', False),
            ('create_date', '<', fecha_corte),
        ]

        list_groups = self.get_grupos_validacion()
        
        inactive_users = self.search(domain)
        deactivated_count = 0
        
        for user in inactive_users:
            has_list_group = any(user.has_group(group) for group in list_groups)            
            if has_list_group:
                should_deactivate = False

                if user.login_date and user.login_date < fecha_corte:
                    should_deactivate = True
                elif not user.login_date and user.create_date < fecha_corte:
                    should_deactivate = True

                if should_deactivate:
                    try:
                        user.sudo().write({
                            'active': False,
                            'auto_desactivado': True,
                            'fecha_desactivacion': fields.Datetime.now(),
                        })                        
                        deactivated_count += 1
                    except Exception as e:
                        return {'error': str(e), 'user_id': user.id}
        
        return {
            'processed': len(inactive_users),
            'deactivated': deactivated_count,
            'threshold_days': dias_inactividad
        }
    
    @api.model
    def get_limite_dias_inactividad(self):
        """Obtener el umbral de días de inactividad desde parámetros del sistema"""
        return int(self.env['ir.config_parameter'].sudo().get_param('SEG_USER_LIMITE_DIAS_INACTIVOS', 30))
    
    @api.model
    def get_grupos_validacion(self):
        """
        Obtener el listado de grupos considerados para validación.
        Retorna una lista de XMLIDs de grupos desde los parámetros del sistema.
        El parámetro debe estar en formato JSON: ["grupo1", "grupo2", ...]
        Default: listado con "base.group_user"
        """
        default_groups = ["base.group_user"]
        
        param_value = self.env['ir.config_parameter'].sudo().get_param('SEG_USER_GROUPS_VALIDATION', False)
        
        if not param_value:
            return default_groups
        
        try:
            grupos = json.loads(param_value)
            if isinstance(grupos, list):
                return grupos
        except (json.JSONDecodeError, ValueError):
            grupos = [g.strip() for g in param_value.split(',') if g.strip()]
            if grupos:
                return grupos
        
        return default_groups