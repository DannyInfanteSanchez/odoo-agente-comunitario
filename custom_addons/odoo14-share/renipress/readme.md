Renipress
=========
- Data actualizada de SUSALUD al 21/10/2019
Antes de actualizar el addon, ejecutar:

```sql

UPDATE ir_model_data
SET noupdate = true
WHERE module = 'renipress' AND model in ('renipress.diresa', ;

UPDATE ir_model_data
SET noupdate=true
WHERE module='renipress' AND model='renipress.red';

UPDATE ir_model_data
SET noupdate=true
WHERE module='renipress' AND model='renipress.microred';

UPDATE ir_model_data
SET noupdate=true
WHERE module='renipress' AND model='renipress.eess';

```
Carga de datos adicionales:
- Ingresar a la opción de Importar establecimientos para poder importar los archivos CSV.
  - renipress/data/renipress_eess_data_privado.csv
  - renipress/data/renipress_eess_data_sanidad.csv
  - renipress/data/renipress_eess_data_essalud.csv
  - renipress/data/renipress_eess_data_inpe.csv
  - renipress/data/renipress_eess_data_municipalidad.csv
  - renipress/data/renipress_eess_data_otros.csv


Dependencia:
- toponimos_peru

Odoo v12
