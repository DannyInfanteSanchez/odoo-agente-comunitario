![logo-minsa](https://www.minsa.gob.pe/Especial/2019/salud_mental/img/logo_minsa.png )
![logo-reniec](https://www.reniec.gob.pe/portal/images/logo_escudo.gif)

consultadatos
=============

# Versión

13.0.1.0.0

# Dependencias Python

[mpi-client](https://git.minsa.gob.pe/oidt/mpi-client/tree/release/1.5.5)

# Dependencias Odoo

[l10n_minsa](l10n_minsa/)

# Instalacion de dependencias
```bash
pip install -r requirements.txt
```

# Configuración Consultas MPI

En `ir.parameters` configurar los parámetros:

Parametro | Descripción
----------|-------------
mpi_api_host | url del host mpi (*)
mpi_api_token | cadena token de mpi (*)
mpi_minutos_sinactualizar | `1` por defecto, minutos en que se actualizará una consulta mpi (0: Actualizar siempre)
consultadatos.modo_online | `True` ó `1` modo online, otro valor se considera como 'False', `True` por defecto


(*) Puede configurar los parámetros `mpi_api_host` y `mpi_api_token` desde el archivo `odoo.conf`. Los valores desde `ir.parameters`  tendrá prevalencia sobre los valores desde la configuración en `odoo.conf`.

```
[options]

; configuracion de parámetros mpi
mpi_api_host=url_mpi
mpi_api_token=token_mpi
```


# Consumo de Consulta de Datos

## Configuración de la aplicación

En el archivo de configuración de la aplicación o módulo
```python
    {
        ...
        'depends': [..., 'consultadatos'],

    }
}
```


Ejemplos de uso:
# Consulta Reniec

```python
    data = self.env['consultadatos.reniec'].consultardni(numerodni)
```

Resultado:

```python
    data = { #...
    }
```

# Consulta MPI

## Método consultardni

```python
    data = self.env['consultadatos.mpi'].consultardni(numerodni)
```

## Método ver

```python
    data = self.env['consultadatos.mpi'].ver(numero_documento_or_uuid, tipo_documento="01")
```

## Método ver_datos_sis

```python
    data = self.env['consultadatos.mpi'].ver_datos_sis(numero_documento_or_uuid, tipo_documento="01"):
```

Resultados:

```python
    data = { #...
    }
```
    

# Fallas al actualizar o instalar

Si al instalar o actualizar el modulo se muestran mensajes de error similares a:

```
ParseError: "duplicate key value violates unique constraint "ir_config_parameter_key_uniq"
DETAIL:  Key (key)=(mpi_api_host) already exists.
```

o

```
ParseError: "duplicate key value violates unique constraint "ir_config_parameter_key_uniq"
DETAIL:  Key (key)=(mpi_api_key) already exists.
```

 Ejecutar:

```sql
update ir_config_parameter set key='mpi_api_host2' where key='mpi_api_host';
update ir_config_parameter set key='mpi_api_token2' where key='mpi_api_token';
```

Actualizar el modulo, y luego ejecutar:

```sql
update ir_config_parameter
set value=(select value from ir_config_parameter where key='mpi_api_host2')
where key='mpi_api_host';

update ir_config_parameter
set value=(select value from ir_config_parameter where key='mpi_api_token2')
where key='mpi_api_token';
```