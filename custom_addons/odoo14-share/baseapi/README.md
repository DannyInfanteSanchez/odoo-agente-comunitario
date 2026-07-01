baseapi
=======

Odoo v10.0


Contiene clase base (abstracta), definiciones, metodos para los `Servicios Web` usando Odoo


```python
class CatalogoBase(models.Model):
    _name = 'baseapi.basemodel'


    _fields_json = [('atributo1', 'etiqueta1') , ('atributo2', 'etiqueta2'), ...]

    """
    Definir los pares `(dato, etiqueta)` que se devolvera en el metodo get_json
    ('create_uid.login', ),  # Devolverá como dato object.create_uid.login y como etiqueta object_create_uid_login
    ('create_uid.login', 'create_login'), # Devolverá como dato object.create_uid.login y como etiqueta create_login
    ('write_date', ),  # Devolverá como dato write_date y como etiqueta write_date
    """

    @api.model
    def get_json(self, domain=None):
        """
        Retorna data del catalogo, usando los "atributos" definidos en `_fields_json`

        :param domain: Dominio para filtrar el catálogo
        :rtype: dict
        """

        return {}
```



# Ejemplo de Catalogo


```python
class CatalogoEjemplo(models.Model):
    _inherit = 'baseapi.basemodel'

    _name = 'catalogominsa.cpt_grupo'
    _order = 'name'
    _rec_name = 'name'
    _description = u'Catálogo CPT - Grupo'

    # Definición de atributos del nuevo catalogo

    # atributo1 = fields....
    # atributo2 = fields....

    _sql_constraints = [
        (...),
    ]
```

# Consulta Api - Token

## Consideraciones

Para el funcionamiento de las consultas via usando token
debe exister solo una base de datos Odoo o setear `db_filter` en el odoo.conf


```
dbfilter=%h
```


## Usuario
El usuario odoo debe tener un token activo y pertenecer al grupo `Usuario Token` y al grupo(s) del Catálogo a Consumir

## Url
```python

url = 'http://localhost:8069/api/modulo_odoo.modelo_odoo'
```



## Headers

Usando un token de usuario
```python
headers = {
    'Authorization': 'Bearer TTTT-OOOO-KKKK-EEEE-NNNN',
}
```

## Envio de Parámetros


```python
params = {...}
```

### Paginación

Parametro | Descripción
----------|------------
page      | Número de página (1 por defecto)
limit     | Items por página (100 por defecto)

```python

params = {
  ...,
  'page': 3,
  'limit': 20,
}
```

### Filtrado de datos

Comparaciones:


Comparación | Código
------|-----
`alias de campo` == `valor` | `'nombre_alias_campo': valor` Búsqueda exacta
`valor` in `alias de campo` | `'nombre_alias_campo__like': valor` Ignora mayúsculas
`alias de campo` >= `valor` | `'nombre_alias_campo__lte': valor`
`alias de campo` > `valor` | `'nombre_alias_campo__lt': valor`
`alias de campo` <= `valor` | `'nombre_alias_campo__lge': valor`
`alias de campo` < `valor` | `'nombre_alias_campo__lg': valor`


```python
params' = {...,
  'nombre_alias_campo': 'valor',

  'nombre_alias_campo__like': 'valor', # Equivale a `nombre_alias_campo in valor` (Ignora Mayúsculas)
  'nombre_alias_campo__lte': 'valor', # Equivale a nombre_alias_campo <= valor
  'nombre_alias_campo_lt': 'valor', # Equivale a nombre_alias_campo < valor
  'nombre_alias_campo__lge': 'valor', # Equivale a nombre_alias_campo >= valor
  'nombre_alias_campo_lg': 'valor', # Equivale a nombre_alias_campo > valor
  'nombre_alias_campo_in': ['1', '2', '3'], # Equivale a nombre_alias_campo in ['1', '2', '3'] valor
  }
}
```

### Cantidad de Registros Filtrados - Count

```python
params = {...,
  'nombre_alias_campo1': valor1,
  'nombre_alias_campo2': valor2,
  'count': True,
}
```

Retornará:
```python
{u'count': #coincidencias}
```

### Seleccion de Campos a devolver

```python
params = {...,
  'nombre_alias_campo1': valor1,
  'nombre_alias_campo2': valor2,
  'only_fields': 'nombre_alias_campo1,nombre_alias_campo2,...',
}
```

### Ejemplo usando python

```python
# -*- coding: utf-8 -*-

import requests
import json


session = requests.session()


headers = {
    'Authorization': 'Bearer xxxxx-xxxxx-xxxxx-xxxxx-xxxxx',
}

url = 'http://localhost:8069/api/catalogominsa.cpt_procedimiento'

params = {'subseccion_codigo': '1.2.3',
          'pagination': 200,
          'page': 1,
          'only_fields': 'subseccion_codigo,procedimiento_codigo',
          'only_count': 0,}

res = session.get(url, data=json.dumps({}),
                  headers=headers,
                  params=params)

if res.status_code == 200:
    res = res.text and json.loads(res.text) or {}
    print res
else:
    print res.text
```