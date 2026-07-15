import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.odoo_client import odoo_client

def test_param():
    print("Reading ir.config_parameter from Odoo...")
    try:
        # Buscar el parametro
        params = odoo_client.search_read(
            model="ir.config_parameter",
            domain=[("key", "=", "consulta_reniec_url")],
            fields=["key", "value"]
        )
        print(f"Params found: {params}")
        
        # Si no existe o tiene valor incorrecto, vamos a configurarlo a una URL simulada o vacia para bypass
        if not params:
            print("Parameter 'consulta_reniec_url' does not exist. Creating it...")
            new_id = odoo_client.create("ir.config_parameter", {
                "key": "consulta_reniec_url",
                "value": "https://postgres-odoo-api.fspjfd.easypanel.host/api/reniec-bypass"
            })
            print(f"Created parameter with ID: {new_id}")
        else:
            param = params[0]
            val = param.get("value", "")
            # Actualizar siempre para apuntar a la API intermedia en produccion
            print(f"Updating parameter '{param['key']}' because value '{val}' is invalid...")
            success = odoo_client.write("ir.config_parameter", [param["id"]], {
                "value": "https://postgres-odoo-api.fspjfd.easypanel.host/api/reniec-bypass"
            })
            print(f"Update status: {success}")
                
    except Exception as e:
        print(f"Error checking parameter: {e}")

if __name__ == "__main__":
    test_param()
