# agente_comite_comunitario

REGISTRO COMUNITARIO
====================
*Módulo de Registro comunitario por establecimientos desarrollado para la versión 14.0 de Odoo*

Modulos dependientes de Odoo:
----------------------------
- base
- base_setup
- mail
- auth_signup
- oi_attachment_error
- web
- renipress
- toponimos_peru
  

CLONE EL ODOO SHARE 14
----------------------
git clone https://git.minsa.gob.pe/oidt/odoo14-share.git


Instalación
------------
*Para la siguiente instalación se asume que ya tiene instalado la versión de odoo (v. 14.0) de no ser asi puedes seguir el siguiente instructivo [Instalación de Odoo 14 en un entorno virtual de python.](https://noviello.it/es/como-instalar-odoo-14-en-ubuntu-20-04-lts/)*


Requisitos del sistema operativo:
--------------------------------
- Odoo 14
- PostgreSQL 10 (Base de datos)
- Python 3.*


Clonar el Odoo14-share
----------------------
git clone git@git.minsa.gob.pe:oidt/odoo14-share.git

Instalación Nueva:
-----------------
mkdir py_agente_comite_comunitario
cd py_agente_comite_comunitario
git clone git@git.minsa.gob.pe:oidt/agente_comite_comunitario.git
git clone git@git.minsa.gob.pe:oidt/odoo14-share.git

Configuración básica del archivo odoo.conf
------------------------------------------
```
[options]
admin_passwd = password
db_host = 127.0.0.1
db_port = 5432
db_user = db_username
db_password = db_password
addons_path = ../odoo14/addons,../py_agente_comite_comunitario/odoo-share,../py_agente_comite_comunitario,../py_agente_comite_comunitario/agente_comite_comunitario/minsa__regcom
```

## Instalación del modulo

1. minsa_regcom

El resto de addons de odoo-serums se instalarán automáticamente por la dependencia entre ellos.


## Configuración de parámetros

Ingresar al aplicativo con el usuario `admin` y activar el `modo desarrollador`.

