Módulo Seguridad - MINSA Odoo
=============================

# 1. Módulos del Proyecto

minsa_seguridad

- Permite deshabilitar a los usuarios que no hayan iniciado sesión en un determinado tiempo.

# 2. Requisitos del Sistema

Odoo v14
Python 3.8.*

# 3. Dependencias

# 4. Instalación

# 4.1 Clonar el ODOO SHARE 14

git clone https://git.minsa.gob.pe/oidt/odoo14-share.git

# 4.2 Instalación de la Aplicación

Instalar la aplicación Módulo Seguridad - MINSA Odoo

# 5. Configuración de parámetros de la aplicación

Activar el modo desarrollador

En el menú `Configuración`/`Parámetros`/`Parámetros del sistema` configurar los parámetros:

Parámetro | Descripción
-----|-----
SEG_USER_LIMITE_DIAS_INACTIVOS | Número de días sin acceso antes de desactivar usuario
SEG_USER_GROUPS_VALIDATION | Grupos de usuarios afectados para desactivación

# 6. Configuración Job de la aplicación

En el menú `Configuración`/`Parámetros`/`Acciones Programadas` configurar el Job:

Parámetro | Descripción
-----|-----
SEG: Desactivar Usuarios Inactivos | Tarea programada para ejecutar la desactivación de usuarios