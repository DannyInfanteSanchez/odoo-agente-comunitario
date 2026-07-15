import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.odoo_client import odoo_client

def test_creation():
    print("Testing Agent Creation directly in Odoo...")
    # Intentamos crear un agente con datos mínimos
    values = {
        "tipo_documento": "01",
        "numero_documento": "99999991", # Cambiar a un DNI que no exista
        "ape_paterno": "TEST",
        "ape_materno": "ACS",
        "nombres": "AGENTE PRUEBA",
        "direccion": "Dirección de Prueba 123",
        "es_voluntario": True,
        # Relaciones mínimas
        "diresa_id": 1,
        "red_id": 1,
        "establecimiento_id": 1,
    }
    try:
        new_id = odoo_client.create("minsa.agente.comunitario", values)
        print(f"✅ Success! Created Agent with ID: {new_id}")
    except Exception as e:
        print(f"❌ Error from Odoo: {e}")

if __name__ == "__main__":
    test_creation()
